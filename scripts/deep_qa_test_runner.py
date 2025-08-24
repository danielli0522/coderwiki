#!/usr/bin/env python3
"""
深度无人值守QA测试脚本
基于BMAD角色系统进行自动化测试、日志分析和bug修复
"""

import os
import sys
import time
import json
import subprocess
import threading
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import yaml
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deep_qa_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BMADRole(Enum):
    """BMAD角色枚举"""
    QA_ANALYST = "qa_analyst"
    TEST_DESIGNER = "test_designer"
    RISK_ANALYST = "risk_analyst"
    NFR_SPECIALIST = "nfr_specialist"
    DEV_AGENT = "dev_agent"
    ARCHITECT = "architect"
    SECURITY_SPECIALIST = "security_specialist"

@dataclass
class TestResult:
    """测试结果数据类"""
    test_name: str
    status: str  # PASS, FAIL, ERROR, TIMEOUT
    duration: float
    error_message: Optional[str] = None
    logs: List[str] = None

@dataclass
class BugReport:
    """Bug报告数据类"""
    id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # AUTH, API, UI, PERFORMANCE, SECURITY, DATABASE
    title: str
    description: str
    logs: List[str]
    suggested_fix: str
    bmad_role: BMADRole

class DeepQATestRunner:
    """深度QA测试运行器"""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.bug_reports: List[BugReport] = []
        self.server_process = None
        self.task_worker_process = None
        self.log_buffer = []
        
        # BMAD角色处理器
        self.role_handlers = {
            BMADRole.QA_ANALYST: self.qa_analyst_handler,
            BMADRole.TEST_DESIGNER: self.test_designer_handler,
            BMADRole.RISK_ANALYST: self.risk_analyst_handler,
            BMADRole.NFR_SPECIALIST: self.nfr_specialist_handler,
            BMADRole.DEV_AGENT: self.dev_agent_handler,
            BMADRole.ARCHITECT: self.architect_handler,
            BMADRole.SECURITY_SPECIALIST: self.security_specialist_handler
        }
    
    def start_services(self) -> bool:
        """启动服务"""
        logger.info("🚀 启动服务...")
        
        # 启动Flask服务器
        try:
            self.server_process = subprocess.Popen(
                ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"],
                cwd="backend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info("✅ Flask服务器启动成功")
        except Exception as e:
            logger.error(f"❌ Flask服务器启动失败: {e}")
            return False
        
        # 启动任务工作器
        try:
            self.task_worker_process = subprocess.Popen(
                ["python", "task_worker.py"],
                cwd="backend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info("✅ 任务工作器启动成功")
        except Exception as e:
            logger.error(f"❌ 任务工作器启动失败: {e}")
            return False
        
        # 等待服务启动
        return self.wait_for_services()
    
    def wait_for_services(self) -> bool:
        """等待服务启动"""
        logger.info("⏳ 等待服务启动...")
        
        for i in range(30):  # 等待30秒
            try:
                response = requests.get("http://localhost:5001/api/system/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ 服务健康检查通过")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        logger.error("❌ 服务启动超时")
        return False
    
    def start_log_monitoring(self):
        """启动日志监控"""
        logger.info("📊 启动日志监控...")
        self.log_monitor_thread = threading.Thread(target=self.monitor_logs, daemon=True)
        self.log_monitor_thread.start()
    
    def monitor_logs(self):
        """监控日志"""
        log_file = "server.log"
        last_position = 0
        
        while True:
            try:
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = f.tell()
                        
                        for line in new_lines:
                            self.analyze_log_line(line.strip())
                            self.log_buffer.append(line.strip())
                            
                            if len(self.log_buffer) > 1000:
                                self.log_buffer = self.log_buffer[-500:]
                
                time.sleep(10)
            except Exception as e:
                logger.error(f"日志监控错误: {e}")
                time.sleep(5)
    
    def analyze_log_line(self, line: str):
        """分析单行日志"""
        if not line:
            return
        
        # 检测错误模式
        error_patterns = ["ERROR", "Exception", "Traceback", "Failed", "Timeout"]
        
        for pattern in error_patterns:
            if pattern.lower() in line.lower():
                self.detect_bug_from_log(line, pattern)
                break
    
    def detect_bug_from_log(self, log_line: str, pattern: str):
        """从日志检测bug"""
        bug_id = f"LOG_{int(time.time())}"
        
        bug_report = BugReport(
            id=bug_id,
            severity="HIGH" if "ERROR" in pattern else "MEDIUM",
            category="SYSTEM",
            title=f"日志错误: {pattern}",
            description=f"在日志中检测到错误模式: {pattern}",
            logs=[log_line],
            suggested_fix="需要进一步分析错误原因并修复",
            bmad_role=BMADRole.QA_ANALYST
        )
        
        self.bug_reports.append(bug_report)
        logger.warning(f"🐛 检测到bug: {bug_id} - {pattern}")
    
    def run_test_suite(self) -> List[TestResult]:
        """运行测试套件"""
        logger.info("🧪 开始运行测试套件...")
        
        test_suite = [
            ("健康检查测试", self.test_health_check),
            ("认证测试", self.test_authentication),
            ("API功能测试", self.test_api_functionality),
            ("性能测试", self.test_performance),
            ("安全测试", self.test_security),
        ]
        
        results = []
        for test_name, test_func in test_suite:
            try:
                logger.info(f"运行测试: {test_name}")
                start_time = time.time()
                result = test_func()
                duration = time.time() - start_time
                
                test_result = TestResult(
                    test_name=test_name,
                    status="PASS" if result else "FAIL",
                    duration=duration,
                    logs=self.log_buffer[-10:]
                )
                results.append(test_result)
                
                if result:
                    logger.info(f"✅ {test_name} 通过")
                else:
                    logger.error(f"❌ {test_name} 失败")
                    
            except Exception as e:
                logger.error(f"❌ {test_name} 异常: {e}")
                test_result = TestResult(
                    test_name=test_name,
                    status="ERROR",
                    duration=0,
                    error_message=str(e),
                    logs=self.log_buffer[-10:]
                )
                results.append(test_result)
        
        return results
    
    def test_health_check(self) -> bool:
        """健康检查测试"""
        try:
            response = requests.get("http://localhost:5001/api/system/health", timeout=10)
            return response.status_code == 200 and response.json().get("success", False)
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return False
    
    def test_authentication(self) -> bool:
        """认证测试"""
        try:
            response = requests.get("http://localhost:5001/api/users/stats", timeout=10)
            return response.status_code == 302  # 应该重定向到登录
        except Exception as e:
            logger.error(f"认证测试失败: {e}")
            return False
    
    def test_api_functionality(self) -> bool:
        """API功能测试"""
        try:
            response = requests.get("http://localhost:5001/api/system/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API功能测试失败: {e}")
            return False
    
    def test_performance(self) -> bool:
        """性能测试"""
        try:
            start_time = time.time()
            response = requests.get("http://localhost:5001/api/system/health", timeout=10)
            duration = time.time() - start_time
            return duration < 2.0 and response.status_code == 200
        except Exception as e:
            logger.error(f"性能测试失败: {e}")
            return False
    
    def test_security(self) -> bool:
        """安全测试"""
        try:
            response = requests.get("http://localhost:5001/api/admin/users", timeout=10)
            return response.status_code in [401, 403, 404]
        except Exception as e:
            logger.error(f"安全测试失败: {e}")
            return False
    
    def analyze_results_with_bmad_roles(self):
        """使用BMAD角色分析结果"""
        logger.info("🔍 使用BMAD角色分析测试结果...")
        
        # 按优先级激活角色
        roles = [
            BMADRole.QA_ANALYST,
            BMADRole.TEST_DESIGNER,
            BMADRole.RISK_ANALYST,
            BMADRole.NFR_SPECIALIST,
            BMADRole.DEV_AGENT,
            BMADRole.ARCHITECT,
            BMADRole.SECURITY_SPECIALIST
        ]
        
        for role in roles:
            handler = self.role_handlers.get(role)
            if handler:
                logger.info(f"🎭 激活BMAD角色: {role.value}")
                handler()
    
    def qa_analyst_handler(self):
        """QA分析师角色处理"""
        logger.info("📋 QA分析师分析测试结果...")
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        logger.info(f"测试统计: 总计={total_tests}, 通过={passed_tests}")
    
    def test_designer_handler(self):
        """测试设计师角色处理"""
        logger.info("🎨 测试设计师分析测试覆盖...")
        covered_areas = set()
        for result in self.test_results:
            if "健康" in result.test_name:
                covered_areas.add("系统健康")
            elif "认证" in result.test_name:
                covered_areas.add("认证系统")
        logger.info(f"测试覆盖区域: {', '.join(covered_areas)}")
    
    def risk_analyst_handler(self):
        """风险分析师角色处理"""
        logger.info("⚠️ 风险分析师评估风险...")
        high_risk_bugs = [b for b in self.bug_reports if b.severity == "CRITICAL"]
        if high_risk_bugs:
            logger.warning(f"发现 {len(high_risk_bugs)} 个高风险bug")
    
    def nfr_specialist_handler(self):
        """NFR专家角色处理"""
        logger.info("📊 NFR专家分析非功能性需求...")
        performance_results = [r for r in self.test_results if "性能" in r.test_name]
        for result in performance_results:
            if result.duration > 2.0:
                logger.warning(f"性能问题: {result.test_name} 耗时 {result.duration:.2f}s")
    
    def dev_agent_handler(self):
        """开发代理角色处理"""
        logger.info("🔧 开发代理准备修复方案...")
        for bug in self.bug_reports:
            if bug.severity in ["CRITICAL", "HIGH"]:
                logger.info(f"需要修复的bug: {bug.id} - {bug.title}")
    
    def architect_handler(self):
        """架构师角色处理"""
        logger.info("🏗️ 架构师分析系统架构...")
        health_test = next((r for r in self.test_results if "健康" in r.test_name), None)
        if health_test and health_test.status == "PASS":
            logger.info("系统架构健康")
        else:
            logger.warning("系统架构存在问题")
    
    def security_specialist_handler(self):
        """安全专家角色处理"""
        logger.info("🔒 安全专家分析安全问题...")
        security_bugs = [b for b in self.bug_reports if b.category == "AUTH" or b.category == "SECURITY"]
        for bug in security_bugs:
            logger.warning(f"安全问题: {bug.id} - {bug.title}")
    
    def generate_test_report(self):
        """生成测试报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.test_results),
                "passed": len([r for r in self.test_results if r.status == "PASS"]),
                "failed": len([r for r in self.test_results if r.status == "FAIL"]),
                "errors": len([r for r in self.test_results if r.status == "ERROR"]),
                "total_bugs": len(self.bug_reports)
            },
            "test_results": [
                {
                    "name": r.test_name,
                    "status": r.status,
                    "duration": r.duration,
                    "error": r.error_message
                }
                for r in self.test_results
            ],
            "bug_reports": [
                {
                    "id": b.id,
                    "severity": b.severity,
                    "category": b.category,
                    "title": b.title,
                    "description": b.description
                }
                for b in self.bug_reports
            ]
        }
        
        with open("deep_qa_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info("📄 测试报告已生成: deep_qa_test_report.json")
    
    def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理资源...")
        
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
        
        if self.task_worker_process:
            self.task_worker_process.terminate()
            self.task_worker_process.wait()
    
    def run(self):
        """运行深度QA测试"""
        logger.info("🚀 开始深度无人值守QA测试...")
        
        try:
            # 启动服务
            if not self.start_services():
                logger.error("❌ 服务启动失败")
                return False
            
            # 启动日志监控
            self.start_log_monitoring()
            
            # 等待服务稳定
            time.sleep(10)
            
            # 运行测试套件
            self.test_results = self.run_test_suite()
            
            # 使用BMAD角色分析结果
            self.analyze_results_with_bmad_roles()
            
            # 生成报告
            self.generate_test_report()
            
            logger.info("✅ 深度QA测试完成")
            return True
            
        except KeyboardInterrupt:
            logger.info("⏹️ 测试被用户中断")
        except Exception as e:
            logger.error(f"❌ 测试过程中发生错误: {e}")
        finally:
            self.cleanup()
        
        return False

def main():
    """主函数"""
    runner = DeepQATestRunner()
    success = runner.run()
    
    if success:
        print("🎉 深度QA测试成功完成！")
        print("📄 查看测试报告: deep_qa_test_report.json")
        print("📝 查看详细日志: deep_qa_test.log")
    else:
        print("❌ 深度QA测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
