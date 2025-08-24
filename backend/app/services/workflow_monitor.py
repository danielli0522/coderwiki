"""
工作流监控和日志服务
提供实时的工作流执行监控、日志记录和性能分析
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from flask import current_app

logger = logging.getLogger(__name__)


class WorkflowEventType(Enum):
    """工作流事件类型"""
    WORKFLOW_START = "workflow_start"
    WORKFLOW_END = "workflow_end"
    AGENT_START = "agent_start" 
    AGENT_END = "agent_end"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PROGRESS_UPDATE = "progress_update"


@dataclass
class WorkflowEvent:
    """工作流事件数据类"""
    timestamp: datetime
    event_type: WorkflowEventType
    workflow_id: str
    agent_name: Optional[str] = None
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    error_traceback: Optional[str] = None
    execution_time: Optional[float] = None


@dataclass
class WorkflowMetrics:
    """工作流执行指标"""
    workflow_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_execution_time: Optional[float] = None
    agent_count: int = 0
    completed_agents: int = 0
    failed_agents: int = 0
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    error_count: int = 0
    warning_count: int = 0


class WorkflowMonitor:
    """工作流监控服务"""
    
    def __init__(self):
        """初始化监控服务"""
        self.active_workflows: Dict[str, WorkflowMetrics] = {}
        self.workflow_events: Dict[str, List[WorkflowEvent]] = {}
        self.log_directory = None
        self._setup_logging_directory()
    
    def _setup_logging_directory(self):
        """设置日志目录"""
        try:
            # 在项目根目录下创建工作流日志目录
            self.log_directory = Path(__file__).parent.parent.parent / 'logs' / 'workflows'
            self.log_directory.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Workflow logging directory initialized: {self.log_directory}")
            
        except Exception as e:
            logger.error(f"Failed to setup workflow logging directory: {e}")
            self.log_directory = None
    
    def start_workflow_monitoring(self, workflow_id: str, config: Dict[str, Any]) -> bool:
        """
        开始监控工作流
        
        Args:
            workflow_id: 工作流ID
            config: 工作流配置
            
        Returns:
            是否成功开始监控
        """
        try:
            # 初始化工作流指标
            metrics = WorkflowMetrics(
                workflow_id=workflow_id,
                start_time=datetime.utcnow()
            )
            
            self.active_workflows[workflow_id] = metrics
            self.workflow_events[workflow_id] = []
            
            # 记录工作流开始事件
            self._log_event(WorkflowEvent(
                timestamp=datetime.utcnow(),
                event_type=WorkflowEventType.WORKFLOW_START,
                workflow_id=workflow_id,
                message=f"Workflow started with config: {json.dumps(config, default=str)}",
                data=config
            ))
            
            logger.info(f"Started monitoring workflow: {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start workflow monitoring: {e}")
            return False
    
    def end_workflow_monitoring(self, workflow_id: str, success: bool = True, error_message: Optional[str] = None):
        """
        结束工作流监控
        
        Args:
            workflow_id: 工作流ID
            success: 是否成功完成
            error_message: 错误消息（如果失败）
        """
        try:
            if workflow_id not in self.active_workflows:
                logger.warning(f"Workflow {workflow_id} not found in active workflows")
                return
            
            metrics = self.active_workflows[workflow_id]
            metrics.end_time = datetime.utcnow()
            
            if metrics.start_time:
                metrics.total_execution_time = (metrics.end_time - metrics.start_time).total_seconds()
            
            # 记录工作流结束事件
            event_type = WorkflowEventType.WORKFLOW_END if success else WorkflowEventType.ERROR
            message = "Workflow completed successfully" if success else f"Workflow failed: {error_message}"
            
            self._log_event(WorkflowEvent(
                timestamp=datetime.utcnow(),
                event_type=event_type,
                workflow_id=workflow_id,
                message=message,
                execution_time=metrics.total_execution_time,
                error_traceback=error_message if not success else None
            ))
            
            # 生成工作流报告
            self._generate_workflow_report(workflow_id)
            
            # 移出活动工作流（保留事件记录）
            del self.active_workflows[workflow_id]
            
            logger.info(f"Ended monitoring workflow: {workflow_id} (success={success})")
            
        except Exception as e:
            logger.error(f"Failed to end workflow monitoring: {e}")
    
    def log_agent_start(self, workflow_id: str, agent_name: str, agent_config: Dict[str, Any]):
        """
        记录代理开始执行
        
        Args:
            workflow_id: 工作流ID
            agent_name: 代理名称
            agent_config: 代理配置
        """
        try:
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id].agent_count += 1
            
            self._log_event(WorkflowEvent(
                timestamp=datetime.utcnow(),
                event_type=WorkflowEventType.AGENT_START,
                workflow_id=workflow_id,
                agent_name=agent_name,
                message=f"Agent {agent_name} started execution",
                data=agent_config
            ))
            
        except Exception as e:
            logger.error(f"Failed to log agent start: {e}")
    
    def log_agent_end(self, workflow_id: str, agent_name: str, success: bool = True, 
                     execution_time: Optional[float] = None, output_size: Optional[int] = None,
                     error_message: Optional[str] = None):
        """
        记录代理执行结束
        
        Args:
            workflow_id: 工作流ID
            agent_name: 代理名称
            success: 是否成功
            execution_time: 执行时间
            output_size: 输出大小
            error_message: 错误消息
        """
        try:
            if workflow_id in self.active_workflows:
                if success:
                    self.active_workflows[workflow_id].completed_agents += 1
                else:
                    self.active_workflows[workflow_id].failed_agents += 1
            
            event_type = WorkflowEventType.AGENT_END if success else WorkflowEventType.ERROR
            message = f"Agent {agent_name} completed" if success else f"Agent {agent_name} failed: {error_message}"
            
            data = {}
            if execution_time:
                data['execution_time'] = execution_time
            if output_size:
                data['output_size'] = output_size
            
            self._log_event(WorkflowEvent(
                timestamp=datetime.utcnow(),
                event_type=event_type,
                workflow_id=workflow_id,
                agent_name=agent_name,
                message=message,
                data=data if data else None,
                execution_time=execution_time,
                error_traceback=error_message if not success else None
            ))
            
        except Exception as e:
            logger.error(f"Failed to log agent end: {e}")
    
    def log_progress_update(self, workflow_id: str, progress_percent: int, current_step: str, agent_name: Optional[str] = None):
        """
        记录进度更新
        
        Args:
            workflow_id: 工作流ID
            progress_percent: 进度百分比
            current_step: 当前步骤描述
            agent_name: 当前执行的代理名称
        """
        try:
            self._log_event(WorkflowEvent(
                timestamp=datetime.utcnow(),
                event_type=WorkflowEventType.PROGRESS_UPDATE,
                workflow_id=workflow_id,
                agent_name=agent_name,
                message=f"Progress: {progress_percent}% - {current_step}",
                data={
                    'progress_percent': progress_percent,
                    'current_step': current_step
                }
            ))
            
        except Exception as e:
            logger.error(f"Failed to log progress update: {e}")
    
    def log_error(self, workflow_id: str, error_message: str, agent_name: Optional[str] = None, 
                  error_traceback: Optional[str] = None):
        """
        记录错误事件
        
        Args:
            workflow_id: 工作流ID
            error_message: 错误消息
            agent_name: 相关代理名称
            error_traceback: 错误堆栈跟踪
        """
        try:
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id].error_count += 1
            
            self._log_event(WorkflowEvent(
                timestamp=datetime.utcnow(),
                event_type=WorkflowEventType.ERROR,
                workflow_id=workflow_id,
                agent_name=agent_name,
                message=error_message,
                error_traceback=error_traceback
            ))
            
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
    
    def log_warning(self, workflow_id: str, warning_message: str, agent_name: Optional[str] = None):
        """
        记录警告事件
        
        Args:
            workflow_id: 工作流ID
            warning_message: 警告消息
            agent_name: 相关代理名称
        """
        try:
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id].warning_count += 1
            
            self._log_event(WorkflowEvent(
                timestamp=datetime.utcnow(),
                event_type=WorkflowEventType.WARNING,
                workflow_id=workflow_id,
                agent_name=agent_name,
                message=warning_message
            ))
            
        except Exception as e:
            logger.error(f"Failed to log warning: {e}")
    
    def get_workflow_metrics(self, workflow_id: str) -> Optional[WorkflowMetrics]:
        """
        获取工作流指标
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            工作流指标或None
        """
        return self.active_workflows.get(workflow_id)
    
    def get_workflow_events(self, workflow_id: str, event_types: Optional[List[WorkflowEventType]] = None) -> List[WorkflowEvent]:
        """
        获取工作流事件
        
        Args:
            workflow_id: 工作流ID
            event_types: 过滤的事件类型
            
        Returns:
            事件列表
        """
        events = self.workflow_events.get(workflow_id, [])
        
        if event_types:
            events = [event for event in events if event.event_type in event_types]
        
        return events
    
    def get_active_workflows(self) -> Dict[str, WorkflowMetrics]:
        """
        获取所有活动工作流
        
        Returns:
            活动工作流字典
        """
        return self.active_workflows.copy()
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        清理旧日志文件
        
        Args:
            days_to_keep: 保留天数
        """
        try:
            if not self.log_directory or not self.log_directory.exists():
                return
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            for log_file in self.log_directory.glob("*.json"):
                try:
                    # 从文件修改时间判断是否过期
                    file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    if file_mtime < cutoff_date:
                        log_file.unlink()
                        logger.info(f"Deleted old workflow log: {log_file}")
                        
                except Exception as e:
                    logger.warning(f"Failed to delete log file {log_file}: {e}")
            
            logger.info(f"Workflow log cleanup completed, kept logs from last {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old workflow logs: {e}")
    
    def _log_event(self, event: WorkflowEvent):
        """
        记录事件到内存和文件
        
        Args:
            event: 工作流事件
        """
        try:
            # 添加到内存中的事件列表
            if event.workflow_id not in self.workflow_events:
                self.workflow_events[event.workflow_id] = []
            
            self.workflow_events[event.workflow_id].append(event)
            
            # 写入日志文件
            if self.log_directory:
                log_file = self.log_directory / f"workflow_{event.workflow_id}_{event.timestamp.strftime('%Y%m%d')}.json"
                
                # 准备日志条目
                log_entry = {
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.event_type.value,
                    'workflow_id': event.workflow_id,
                    'agent_name': event.agent_name,
                    'message': event.message,
                    'data': event.data,
                    'error_traceback': event.error_traceback,
                    'execution_time': event.execution_time
                }
                
                # 追加到日志文件
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + '\n')
            
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
    
    def _generate_workflow_report(self, workflow_id: str):
        """
        生成工作流执行报告
        
        Args:
            workflow_id: 工作流ID
        """
        try:
            if workflow_id not in self.workflow_events:
                return
            
            metrics = self.active_workflows.get(workflow_id)
            events = self.workflow_events[workflow_id]
            
            # 生成报告数据
            report = {
                'workflow_id': workflow_id,
                'generated_at': datetime.utcnow().isoformat(),
                'metrics': asdict(metrics) if metrics else None,
                'event_summary': {
                    'total_events': len(events),
                    'errors': len([e for e in events if e.event_type == WorkflowEventType.ERROR]),
                    'warnings': len([e for e in events if e.event_type == WorkflowEventType.WARNING]),
                    'agent_executions': len([e for e in events if e.event_type == WorkflowEventType.AGENT_START]),
                },
                'timeline': [
                    {
                        'timestamp': event.timestamp.isoformat(),
                        'event_type': event.event_type.value,
                        'agent_name': event.agent_name,
                        'message': event.message,
                        'execution_time': event.execution_time
                    }
                    for event in events
                ]
            }
            
            # 保存报告文件
            if self.log_directory:
                report_file = self.log_directory / f"workflow_report_{workflow_id}.json"
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2, default=str)
                
                logger.info(f"Generated workflow report: {report_file}")
                
        except Exception as e:
            logger.error(f"Failed to generate workflow report: {e}")


# 全局工作流监控实例
workflow_monitor = WorkflowMonitor()