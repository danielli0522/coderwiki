import subprocess
import os
from typing import List, Dict, Optional
from pathlib import Path

class GitUtils:
    """Git仓库管理工具"""
    
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or os.getcwd()
    
    def clone_repository(self, repo_url: str, target_dir: str = None) -> bool:
        """克隆Git仓库"""
        try:
            cmd = ['git', 'clone', repo_url]
            if target_dir:
                cmd.append(target_dir)
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            return result.returncode == 0
        except Exception as e:
            print(f"克隆仓库失败: {e}")
            return False
    
    def get_repository_info(self, repo_path: str = None) -> Dict[str, str]:
        """获取仓库信息"""
        repo_path = repo_path or self.repo_path
        info = {}
        
        try:
            # 获取远程仓库URL
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  capture_output=True, text=True, cwd=repo_path)
            if result.returncode == 0:
                info['remote_url'] = result.stdout.strip()
            
            # 获取当前分支
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, cwd=repo_path)
            if result.returncode == 0:
                info['current_branch'] = result.stdout.strip()
            
            # 获取最新提交
            result = subprocess.run(['git', 'log', '-1', '--pretty=format:%H|%s|%an|%ae'], 
                                  capture_output=True, text=True, cwd=repo_path)
            if result.returncode == 0:
                commit_info = result.stdout.strip().split('|')
                if len(commit_info) >= 4:
                    info['latest_commit'] = {
                        'hash': commit_info[0],
                        'message': commit_info[1],
                        'author': commit_info[2],
                        'email': commit_info[3]
                    }
            
            return info
        except Exception as e:
            print(f"获取仓库信息失败: {e}")
            return {}
    
    def get_file_list(self, repo_path: str = None) -> List[str]:
        """获取仓库文件列表"""
        repo_path = repo_path or self.repo_path
        
        try:
            result = subprocess.run(['git', 'ls-files'], 
                                  capture_output=True, text=True, cwd=repo_path)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
            return []
        except Exception as e:
            print(f"获取文件列表失败: {e}")
            return []
    
    def get_file_content(self, file_path: str, repo_path: str = None) -> Optional[str]:
        """获取文件内容"""
        repo_path = repo_path or self.repo_path
        
        try:
            full_path = os.path.join(repo_path, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"获取文件内容失败: {e}")
            return None
    
    def get_branch_list(self, repo_path: str = None) -> List[str]:
        """获取分支列表"""
        repo_path = repo_path or self.repo_path
        
        try:
            result = subprocess.run(['git', 'branch', '-a'], 
                                  capture_output=True, text=True, cwd=repo_path)
            if result.returncode == 0:
                branches = []
                for line in result.stdout.strip().split('\n'):
                    branch = line.strip().replace('*', '').strip()
                    if branch:
                        branches.append(branch)
                return branches
            return []
        except Exception as e:
            print(f"获取分支列表失败: {e}")
            return []
    
    def create_branch(self, branch_name: str, repo_path: str = None) -> bool:
        """创建新分支"""
        repo_path = repo_path or self.repo_path
        
        try:
            result = subprocess.run(['git', 'checkout', '-b', branch_name], 
                                  capture_output=True, text=True, cwd=repo_path)
            return result.returncode == 0
        except Exception as e:
            print(f"创建分支失败: {e}")
            return False
    
    def commit_changes(self, message: str, repo_path: str = None) -> bool:
        """提交更改"""
        repo_path = repo_path or self.repo_path
        
        try:
            # 添加所有更改
            subprocess.run(['git', 'add', '.'], cwd=repo_path)
            
            # 提交更改
            result = subprocess.run(['git', 'commit', '-m', message], 
                                  capture_output=True, text=True, cwd=repo_path)
            return result.returncode == 0
        except Exception as e:
            print(f"提交更改失败: {e}")
            return False