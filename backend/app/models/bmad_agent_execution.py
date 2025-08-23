"""
BMAD 代理执行记录模型
"""

from datetime import datetime
from .. import db


class BMADAgentExecution(db.Model):
    """BMAD 代理执行记录"""

    __tablename__ = 'bmad_agent_executions'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    agent_name = db.Column(db.String(100), nullable=False)
    agent_role = db.Column(db.String(255), nullable=False)
    execution_status = db.Column(
        db.Enum('pending', 'running', 'completed', 'failed', name='execution_status_enum'),
        default='pending',
        nullable=False
    )
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    output_content = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关联关系
    task = db.relationship('Task', backref='bmad_agent_executions')

    def __repr__(self):
        return f'<BMADAgentExecution {self.id}: {self.agent_name} ({self.execution_status})>'

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'agent_name': self.agent_name,
            'agent_role': self.agent_role,
            'execution_status': self.execution_status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'output_content': self.output_content,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def get_by_task_id(cls, task_id: int):
        """根据任务ID获取代理执行记录"""
        return cls.query.filter_by(task_id=task_id).all()

    @classmethod
    def get_by_agent_name(cls, task_id: int, agent_name: str):
        """根据任务ID和代理名称获取执行记录"""
        return cls.query.filter_by(task_id=task_id, agent_name=agent_name).first()

    def update_status(self, status: str, output_content: str = None, error_message: str = None):
        """更新执行状态"""
        self.execution_status = status

        if status in ['running', 'completed']:
            if not self.start_time:
                self.start_time = datetime.utcnow()

        if status in ['completed', 'failed']:
            self.end_time = datetime.utcnow()

        if output_content:
            self.output_content = output_content

        if error_message:
            self.error_message = error_message

        db.session.commit()

