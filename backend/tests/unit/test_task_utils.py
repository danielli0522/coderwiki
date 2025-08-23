"""
Task Utility Functions Unit Tests
"""
import pytest
import json
from datetime import datetime, timedelta
from app.utils.task_utils import (
    generate_task_id, validate_task_type, validate_task_status, validate_task_progress,
    format_task_duration, get_task_status_color, get_task_status_icon,
    get_task_type_display_name, calculate_task_eta, create_batch_tasks,
    get_task_summary, export_task_data, get_task_filters, apply_task_filters,
    validate_task_permissions, get_task_dependencies, can_execute_task,
    get_task_resource_requirements
)
from app.models.task import Task
from app import create_app, db
from config import TestingConfig


class TestTaskUtils:
    
    def setup_method(self):
        """测试前设置"""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建数据库表
        db.create_all()
        
        # 创建测试用户
        from app.models.user import User
        from app.models.repository import Repository
        
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('testpassword123')
        db.session.add(self.user)
        
        # 创建测试仓库
        self.repo = Repository(
            user_id=self.user.id,
            name='test-repo',
            url='https://github.com/test/test-repo.git',
            description='Test repository'
        )
        db.session.add(self.repo)
        db.session.commit()
    
    def teardown_method(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_generate_task_id(self):
        """测试生成任务ID"""
        task_id = generate_task_id()
        assert isinstance(task_id, str)
        assert len(task_id) > 0
        
        # 测试生成的ID是唯一的
        another_task_id = generate_task_id()
        assert task_id != another_task_id
    
    def test_validate_task_type(self):
        """测试验证任务类型"""
        # 测试有效类型
        assert validate_task_type('generate_document') is True
        assert validate_task_type('sync_repository') is True
        assert validate_task_type('analyze_code') is True
        
        # 测试无效类型
        assert validate_task_type('invalid_type') is False
        assert validate_task_type('') is False
        assert validate_task_type(None) is False
    
    def test_validate_task_status(self):
        """测试验证任务状态"""
        # 测试有效状态
        assert validate_task_status('pending') is True
        assert validate_task_status('running') is True
        assert validate_task_status('completed') is True
        assert validate_task_status('failed') is True
        
        # 测试无效状态
        assert validate_task_status('invalid_status') is False
        assert validate_task_status('') is False
        assert validate_task_status(None) is False
    
    def test_validate_task_progress(self):
        """测试验证任务进度"""
        # 测试有效进度
        assert validate_task_progress(0) is True
        assert validate_task_progress(50) is True
        assert validate_task_progress(100) is True
        assert validate_task_progress(0.0) is True
        assert validate_task_progress(100.0) is True
        
        # 测试无效进度
        assert validate_task_progress(-1) is False
        assert validate_task_progress(101) is False
        assert validate_task_progress(-0.1) is False
        assert validate_task_progress(100.1) is False
        assert validate_task_progress('invalid') is False
        assert validate_task_progress(None) is False
    
    def test_format_task_duration(self):
        """测试格式化任务持续时间"""
        # 测试短时间
        assert format_task_duration(0.5) == '0.5s'
        assert format_task_duration(30) == '30.0s'
        
        # 测试分钟
        assert format_task_duration(60) == '1.0m'
        assert format_task_duration(90) == '1.5m'
        assert format_task_duration(3600) == '60.0m'
        
        # 测试小时
        assert format_task_duration(3600) == '1.0h'
        assert format_task_duration(7200) == '2.0h'
    
    def test_get_task_status_color(self):
        """测试获取任务状态颜色"""
        assert get_task_status_color('pending') == 'warning'
        assert get_task_status_color('running') == 'info'
        assert get_task_status_color('completed') == 'success'
        assert get_task_status_color('failed') == 'danger'
        assert get_task_status_color('unknown') == 'secondary'
    
    def test_get_task_status_icon(self):
        """测试获取任务状态图标"""
        assert get_task_status_icon('pending') == 'clock'
        assert get_task_status_icon('running') == 'play-circle'
        assert get_task_status_icon('completed') == 'check-circle'
        assert get_task_status_icon('failed') == 'x-circle'
        assert get_task_status_icon('unknown') == 'question-circle'
    
    def test_get_task_type_display_name(self):
        """测试获取任务类型显示名称"""
        assert get_task_type_display_name('generate_document') == 'Generate Document'
        assert get_task_type_display_name('sync_repository') == 'Sync Repository'
        assert get_task_type_display_name('analyze_code') == 'Analyze Code'
        assert get_task_type_display_name('unknown_type') == 'Unknown Type'
    
    def test_calculate_task_eta(self):
        """测试计算任务预计完成时间"""
        now = datetime.utcnow()
        
        # 测试非运行任务
        pending_task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        eta = calculate_task_eta(pending_task)
        assert eta is None
        
        # 测试运行任务
        running_task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='running',
            started_at=now - timedelta(minutes=2),
            progress=50
        )
        
        eta = calculate_task_eta(running_task)
        assert eta is not None
        assert eta > now
        
        # 测试使用默认完成时间
        task_with_no_progress = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='running',
            started_at=now - timedelta(minutes=1),
            progress=0
        )
        
        eta = calculate_task_eta(task_with_no_progress)
        assert eta is not None
        assert eta > now
    
    def test_create_batch_tasks(self):
        """测试创建批量任务"""
        # 创建多个仓库
        from app.models.repository import Repository
        
        repos = []
        for i in range(3):
            repo = Repository(
                user_id=self.user.id,
                name=f'test-repo-{i}',
                url=f'https://github.com/test/test-repo-{i}.git',
                description=f'Test repository {i}'
            )
            db.session.add(repo)
            repos.append(repo)
        
        db.session.commit()
        
        # 创建批量任务
        repository_ids = [repo.id for repo in repos]
        created_tasks = create_batch_tasks(self.user.id, repository_ids, 'generate_document')
        
        assert len(created_tasks) == 3
        
        for task in created_tasks:
            assert task.user_id == self.user.id
            assert task.type == 'generate_document'
            assert task.status == 'pending'
            assert task.repository_id in repository_ids
    
    def test_create_batch_tasks_invalid_type(self):
        """测试创建批量任务无效类型"""
        repository_ids = [self.repo.id]
        
        with pytest.raises(ValueError):
            create_batch_tasks(self.user.id, repository_ids, 'invalid_type')
    
    def test_get_task_summary(self):
        """测试获取任务摘要"""
        now = datetime.utcnow()
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='running',
            progress=50,
            created_at=now - timedelta(minutes=5),
            started_at=now - timedelta(minutes=2)
        )
        db.session.add(task)
        db.session.commit()
        
        summary = get_task_summary(task)
        
        assert summary['id'] == task.id
        assert summary['type'] == 'Generate Document'
        assert summary['status'] == 'running'
        assert summary['progress'] == 50
        assert summary['duration'] is not None
        assert summary['status_color'] == 'info'
        assert summary['status_icon'] == 'play-circle'
        assert summary['can_retry'] is False
        assert summary['is_running'] is True
        assert summary['is_completed'] is False
        assert summary['is_failed'] is False
    
    def test_export_task_data_json(self):
        """测试导出任务数据为JSON"""
        # 创建测试任务
        tasks = []
        for i in range(2):
            task = Task(
                user_id=self.user.id,
                repository_id=self.repo.id,
                type='generate_document',
                status='completed',
                progress=100
            )
            db.session.add(task)
            tasks.append(task)
        
        db.session.commit()
        
        # 导出为JSON
        json_data = export_task_data(tasks, 'json')
        
        assert isinstance(json_data, str)
        parsed_data = json.loads(json_data)
        assert len(parsed_data) == 2
        
        for task_data in parsed_data:
            assert 'id' in task_data
            assert 'type' in task_data
            assert 'status' in task_data
            assert 'progress' in task_data
    
    def test_export_task_data_csv(self):
        """测试导出任务数据为CSV"""
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='completed',
            progress=100
        )
        db.session.add(task)
        db.session.commit()
        
        # 导出为CSV
        csv_data = export_task_data([task], 'csv')
        
        assert isinstance(csv_data, str)
        assert 'ID,Type,Status,Progress' in csv_data
        assert 'generate_document,completed,100' in csv_data
    
    def test_export_task_data_txt(self):
        """测试导出任务数据为TXT"""
        # 创建测试任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='completed',
            progress=100
        )
        db.session.add(task)
        db.session.commit()
        
        # 导出为TXT
        txt_data = export_task_data([task], 'txt')
        
        assert isinstance(txt_data, str)
        assert 'Task' in txt_data
        assert 'Generate Document' in txt_data
        assert 'completed' in txt_data
    
    def test_export_task_data_invalid_format(self):
        """测试导出任务数据无效格式"""
        with pytest.raises(ValueError):
            export_task_data([], 'invalid_format')
    
    def test_get_task_filters(self):
        """测试获取任务过滤器"""
        filters = get_task_filters()
        
        assert 'status' in filters
        assert 'type' in filters
        assert 'progress_ranges' in filters
        assert 'time_ranges' in filters
        
        assert 'pending' in filters['status']
        assert 'generate_document' in filters['type']
        assert '0-25' in filters['progress_ranges']
        assert 'today' in filters['time_ranges']
    
    def test_apply_task_filters(self):
        """测试应用任务过滤器"""
        # 创建测试任务
        tasks = [
            Task(user_id=self.user.id, repository_id=self.repo.id, type='generate_document', status='pending', progress=10),
            Task(user_id=self.user.id, repository_id=self.repo.id, type='sync_repository', status='running', progress=50),
            Task(user_id=self.user.id, repository_id=self.repo.id, type='analyze_code', status='completed', progress=100)
        ]
        
        for task in tasks:
            db.session.add(task)
        
        db.session.commit()
        
        # 获取基础查询
        query = Task.query
        
        # 测试状态过滤
        filtered_query = apply_task_filters(query, {'status': 'pending'})
        filtered_tasks = filtered_query.all()
        assert len(filtered_tasks) == 1
        assert filtered_tasks[0].status == 'pending'
        
        # 测试类型过滤
        filtered_query = apply_task_filters(query, {'type': 'sync_repository'})
        filtered_tasks = filtered_query.all()
        assert len(filtered_tasks) == 1
        assert filtered_tasks[0].type == 'sync_repository'
        
        # 测试进度范围过滤
        filtered_query = apply_task_filters(query, {'progress_range': '0-25'})
        filtered_tasks = filtered_query.all()
        assert len(filtered_tasks) == 1
        assert 0 <= filtered_tasks[0].progress <= 25
        
        # 测试时间范围过滤
        filtered_query = apply_task_filters(query, {'time_range': 'today'})
        filtered_tasks = filtered_query.all()
        assert len(filtered_tasks) == 3  # 所有任务都是今天创建的
    
    def test_validate_task_permissions(self):
        """测试验证任务权限"""
        # 创建另一个用户
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        db.session.commit()
        
        # 创建任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 测试任务所有者权限
        assert validate_task_permissions(self.user, task) is True
        
        # 测试其他用户权限
        assert validate_task_permissions(other_user, task) is False
        
        # 测试管理员权限
        admin_user = User(username='admin', email='admin@example.com', is_admin=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        
        assert validate_task_permissions(admin_user, task) is True
    
    def test_get_task_dependencies(self):
        """测试获取任务依赖"""
        # 创建任务
        task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 获取依赖（当前实现返回空列表）
        dependencies = get_task_dependencies(task)
        assert isinstance(dependencies, list)
        assert len(dependencies) == 0
    
    def test_can_execute_task(self):
        """测试检查任务是否可以执行"""
        # 测试pending任务
        pending_task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='pending'
        )
        db.session.add(pending_task)
        db.session.commit()
        
        assert can_execute_task(pending_task) is True
        
        # 测试running任务
        running_task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='running'
        )
        db.session.add(running_task)
        db.session.commit()
        
        assert can_execute_task(running_task) is False
        
        # 测试completed任务
        completed_task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='completed'
        )
        db.session.add(completed_task)
        db.session.commit()
        
        assert can_execute_task(completed_task) is False
        
        # 测试failed任务
        failed_task = Task(
            user_id=self.user.id,
            repository_id=self.repo.id,
            type='generate_document',
            status='failed'
        )
        db.session.add(failed_task)
        db.session.commit()
        
        assert can_execute_task(failed_task) is False
    
    def test_get_task_resource_requirements(self):
        """测试获取任务资源需求"""
        # 测试文档生成任务
        doc_requirements = get_task_resource_requirements('generate_document')
        assert doc_requirements['memory_mb'] == 512
        assert doc_requirements['cpu_cores'] == 1
        assert doc_requirements['timeout_seconds'] == 1800
        assert doc_requirements['max_retries'] == 3
        
        # 测试仓库同步任务
        sync_requirements = get_task_resource_requirements('sync_repository')
        assert sync_requirements['memory_mb'] == 256
        assert sync_requirements['cpu_cores'] == 1
        assert sync_requirements['timeout_seconds'] == 600
        assert sync_requirements['max_retries'] == 2
        
        # 测试代码分析任务
        analysis_requirements = get_task_resource_requirements('analyze_code')
        assert analysis_requirements['memory_mb'] == 1024
        assert analysis_requirements['cpu_cores'] == 2
        assert analysis_requirements['timeout_seconds'] == 1200
        assert analysis_requirements['max_retries'] == 3
        
        # 测试未知任务类型
        unknown_requirements = get_task_resource_requirements('unknown_type')
        assert unknown_requirements['memory_mb'] == 512
        assert unknown_requirements['cpu_cores'] == 1
        assert unknown_requirements['timeout_seconds'] == 900
        assert unknown_requirements['max_retries'] == 2