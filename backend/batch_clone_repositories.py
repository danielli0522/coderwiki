#!/usr/bin/env python3
"""
批量克隆现有仓库脚本
处理那些尚未克隆或克隆失败的仓库
"""

from app import create_app, db
from app.models.repository import Repository
from app.services.repository_service import RepositoryService
from config import DevelopmentConfig
import time

def is_valid_repository_url(url):
    """检查是否是有效的仓库URL"""
    # 排除明显无效的URL
    invalid_patterns = [
        'javascript:', 'script>', 'passwd', 'invalid', 'not-a-valid', 
        '🚀', 'null-byte', 'data:', 'file://', 'alert('
    ]
    
    if any(pattern in url.lower() for pattern in invalid_patterns):
        return False
    
    # 必须以http开头且包含常见Git托管服务
    if not url.startswith('http'):
        return False
    
    # 允许的Git托管服务
    valid_hosts = ['github.com', 'gitlab.com', 'bitbucket.org']
    if not any(host in url for host in valid_hosts):
        return False
        
    return True

def batch_clone_repositories():
    """批量克隆现有仓库"""
    app, _ = create_app(DevelopmentConfig)
    
    with app.app_context():
        service = RepositoryService()
        
        # 查找需要克隆的仓库
        repositories_to_clone = Repository.query.filter(
            db.or_(
                Repository.local_path.is_(None),
                Repository.clone_status == 'failed',
                Repository.clone_status.is_(None)
            )
        ).all()
        
        # 过滤出有效的仓库
        valid_repos = []
        for repo in repositories_to_clone:
            if is_valid_repository_url(repo.url):
                valid_repos.append(repo)
        
        print(f"找到 {len(valid_repos)} 个有效仓库需要克隆")
        print("=" * 50)
        
        success_count = 0
        failed_count = 0
        
        for i, repo in enumerate(valid_repos, 1):
            print(f"[{i}/{len(valid_repos)}] 正在处理: {repo.name}")
            print(f"  URL: {repo.url}")
            
            try:
                # 重置克隆状态
                repo.clone_status = 'pending'
                db.session.commit()
                
                # 开始克隆
                service._start_cloning_process(repo)
                
                # 刷新状态
                db.session.refresh(repo)
                
                if repo.clone_status == 'completed':
                    print(f"  ✅ 克隆成功 - 文件数: {repo.file_count}, 路径: {repo.local_path}")
                    success_count += 1
                else:
                    print(f"  ❌ 克隆失败 - 错误: {repo.clone_error}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"  ❌ 处理异常: {str(e)}")
                failed_count += 1
            
            print("-" * 40)
            
            # 避免过快请求，稍微延迟
            if i < len(valid_repos):
                time.sleep(1)
        
        print("=" * 50)
        print(f"批量克隆完成:")
        print(f"  成功: {success_count}")
        print(f"  失败: {failed_count}")
        print(f"  总计: {len(valid_repos)}")

if __name__ == "__main__":
    print("🚀 开始批量克隆现有仓库...")
    batch_clone_repositories()
    print("✅ 批量克隆任务完成!")