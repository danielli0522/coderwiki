#!/usr/bin/env python3
"""
项目结构验证脚本
用于验证Story 1.2的项目结构是否完整
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class ProjectStructureValidator:
    """项目结构验证器"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        
        # 定义必需的目录结构
        self.required_directories = {
            'backend': {
                'app': {
                    'api': ['__init__.py'],
                    'models': ['__init__.py'],
                    'services': ['__init__.py'],
                    'utils': ['__init__.py'],
                    'static': ['css', 'js', 'images'],
                    '__init__.py': True,
                    'config.py': True
                },
                'tests': {
                    'unit': ['__init__.py'],
                    'integration': ['__init__.py'],
                    'e2e': ['__init__.py'],
                    '__init__.py': True
                },
                'migrations': True,
                'run.py': True,
                'config.py': True
            },
            'frontend': {
                'templates': {
                    'auth': True,
                    'dashboard': True,
                    'document': True,
                    'repository': True,
                    'partials': True,
                    'base.html': True
                },
                'static': {
                    'css': ['style.css'],
                    'js': ['main.js'],
                    'images': True
                }
            },
            'config': {
                'development.py': True,
                'production.py': True,
                'testing.py': True
            },
            'database': {
                'schema.sql': True,
                'init_data.sql': True
            },
            'docs': True,
            'scripts': True
        }
        
        # 定义必需的文件
        self.required_files = {
            'requirements.txt': True,
            'requirements-dev.txt': True,
            '.env.example': True,
            '.gitignore': True,
            'README.md': True,
            'setup.cfg': True,
            'pyproject.toml': True
        }
    
    def validate_structure(self) -> Dict[str, List[str]]:
        """验证项目结构"""
        print("开始验证项目结构...")
        print(f"项目根目录: {self.project_root}")
        print("=" * 50)
        
        # 验证目录结构
        self._validate_directories()
        
        # 验证文件
        self._validate_files()
        
        # 验证后端特定文件
        self._validate_backend_files()
        
        # 验证前端特定文件
        self._validate_frontend_files()
        
        # 输出结果
        self._print_results()
        
        return self.results
    
    def _validate_directories(self):
        """验证目录结构"""
        print("\n验证目录结构...")
        
        for dir_name, dir_structure in self.required_directories.items():
            dir_path = self.project_root / dir_name
            
            if dir_path.exists() and dir_path.is_dir():
                self._check_directory(dir_path, dir_structure, f"{dir_name}/")
                self.results['passed'].append(f"目录 {dir_name}/ 存在")
            else:
                self.results['failed'].append(f"目录 {dir_name}/ 不存在")
    
    def _check_directory(self, dir_path: Path, structure, prefix: str):
        """递归检查目录结构"""
        if isinstance(structure, dict):
            for item_name, item_structure in structure.items():
                item_path = dir_path / item_name
                
                if isinstance(item_structure, dict):
                    # 子目录
                    if item_path.exists() and item_path.is_dir():
                        self._check_directory(item_path, item_structure, f"{prefix}{item_name}/")
                        self.results['passed'].append(f"目录 {prefix}{item_name}/ 存在")
                    else:
                        self.results['failed'].append(f"目录 {prefix}{item_name}/ 不存在")
                elif isinstance(item_structure, list):
                    # 包含特定文件的目录
                    if item_path.exists() and item_path.is_dir():
                        for required_file in item_structure:
                            file_path = item_path / required_file
                            if file_path.exists():
                                self.results['passed'].append(f"文件 {prefix}{item_name}/{required_file} 存在")
                            else:
                                self.results['failed'].append(f"文件 {prefix}{item_name}/{required_file} 不存在")
                    else:
                        self.results['failed'].append(f"目录 {prefix}{item_name}/ 不存在")
                else:
                    # 文件
                    if item_path.exists():
                        self.results['passed'].append(f"文件 {prefix}{item_name} 存在")
                    else:
                        self.results['failed'].append(f"文件 {prefix}{item_name} 不存在")
        else:
            # 简单目录存在检查
            if dir_path.exists() and dir_path.is_dir():
                self.results['passed'].append(f"目录 {prefix} 存在")
            else:
                self.results['failed'].append(f"目录 {prefix} 不存在")
    
    def _validate_files(self):
        """验证根目录文件"""
        print("\n验证根目录文件...")
        
        for file_name, required in self.required_files.items():
            file_path = self.project_root / file_name
            
            if file_path.exists():
                self.results['passed'].append(f"文件 {file_name} 存在")
            else:
                self.results['failed'].append(f"文件 {file_name} 不存在")
    
    def _validate_backend_files(self):
        """验证后端特定文件"""
        print("\n验证后端文件...")
        
        backend_files = [
            'backend/app/models/user.py',
            'backend/app/models/repository.py',
            'backend/app/models/document.py',
            'backend/app/models/task.py',
            'backend/app/services/auth_service.py',
            'backend/app/services/repo_service.py',
            'backend/app/services/doc_service.py',
            'backend/app/services/task_service.py',
            'backend/app/utils/git_utils.py',
            'backend/app/utils/code_analyzer.py',
            'backend/app/utils/llm_client.py',
            'backend/app/utils/doc_formatter.py',
            'backend/tests/unit/test_auth_service.py',
            'backend/tests/unit/test_user_model.py'
        ]
        
        for file_path in backend_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.results['passed'].append(f"后端文件 {file_path} 存在")
            else:
                self.results['failed'].append(f"后端文件 {file_path} 不存在")
    
    def _validate_frontend_files(self):
        """验证前端特定文件"""
        print("\n验证前端文件...")
        
        frontend_files = [
            'frontend/templates/partials/navbar.html',
            'frontend/templates/partials/footer.html',
            'frontend/static/css/style.css',
            'frontend/static/js/main.js'
        ]
        
        for file_path in frontend_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.results['passed'].append(f"前端文件 {file_path} 存在")
            else:
                self.results['failed'].append(f"前端文件 {file_path} 不存在")
    
    def _print_results(self):
        """打印验证结果"""
        print("\n" + "=" * 50)
        print("验证结果")
        print("=" * 50)
        
        # 统计结果
        total_passed = len(self.results['passed'])
        total_failed = len(self.results['failed'])
        total_warnings = len(self.results['warnings'])
        total_checks = total_passed + total_failed + total_warnings
        
        print(f"\n总检查项: {total_checks}")
        print(f"通过: {total_passed} ({total_passed/total_checks*100:.1f}%)")
        print(f"失败: {total_failed} ({total_failed/total_checks*100:.1f}%)")
        print(f"警告: {total_warnings} ({total_warnings/total_checks*100:.1f}%)")
        
        # 显示通过的项
        if self.results['passed']:
            print(f"\n✅ 通过的项目 ({len(self.results['passed'])}):")
            for item in self.results['passed']:
                print(f"  ✓ {item}")
        
        # 显示失败的项
        if self.results['failed']:
            print(f"\n❌ 失败的项目 ({len(self.results['failed'])}):")
            for item in self.results['failed']:
                print(f"  ✗ {item}")
        
        # 显示警告
        if self.results['warnings']:
            print(f"\n⚠️ 警告 ({len(self.results['warnings'])}):")
            for item in self.results['warnings']:
                print(f"  ⚠ {item}")
        
        # 总体结论
        print("\n" + "=" * 50)
        if total_failed == 0:
            print("🎉 项目结构验证通过！所有必需的目录和文件都已创建。")
            return True
        else:
            print(f"⚠️ 项目结构验证失败，有 {total_failed} 个项目需要修复。")
            return False
    
    def generate_report(self) -> str:
        """生成验证报告"""
        report = []
        report.append("CoderWiki 项目结构验证报告")
        report.append("=" * 50)
        report.append(f"验证时间: {self._get_current_time()}")
        report.append(f"项目根目录: {self.project_root}")
        report.append("")
        
        # 统计结果
        total_passed = len(self.results['passed'])
        total_failed = len(self.results['failed'])
        total_warnings = len(self.results['warnings'])
        total_checks = total_passed + total_failed + total_warnings
        
        report.append("验证结果统计:")
        report.append(f"  总检查项: {total_checks}")
        report.append(f"  通过: {total_passed} ({total_passed/total_checks*100:.1f}%)")
        report.append(f"  失败: {total_failed} ({total_failed/total_checks*100:.1f}%)")
        report.append(f"  警告: {total_warnings} ({total_warnings/total_checks*100:.1f}%)")
        report.append("")
        
        # 详细结果
        if self.results['passed']:
            report.append("通过的项目:")
            for item in self.results['passed']:
                report.append(f"  ✓ {item}")
            report.append("")
        
        if self.results['failed']:
            report.append("失败的项目:")
            for item in self.results['failed']:
                report.append(f"  ✗ {item}")
            report.append("")
        
        if self.results['warnings']:
            report.append("警告:")
            for item in self.results['warnings']:
                report.append(f"  ⚠ {item}")
            report.append("")
        
        # 结论
        report.append("=" * 50)
        if total_failed == 0:
            report.append("✅ 项目结构验证通过！")
        else:
            report.append(f"❌ 项目结构验证失败，有 {total_failed} 个项目需要修复。")
        
        return "\n".join(report)
    
    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数"""
    validator = ProjectStructureValidator()
    success = validator.validate_structure()
    
    # 生成报告文件
    report = validator.generate_report()
    report_file = "project_structure_validation_report.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n详细报告已保存到: {report_file}")
    
    # 返回退出码
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()