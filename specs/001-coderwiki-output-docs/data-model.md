# Data Model: 代码质量分析模块增强

## Entity Extensions

### Repository (扩展现有实体)

**现有字段**:
- `id`: Integer, Primary Key
- `user_id`: Integer, Foreign Key to users
- `name`: String(255), Repository name
- `url`: String(500), Git repository URL
- `local_path`: String(1000), Cloned repository path
- `status`: Enum('active', 'inactive', 'error', 'cloning', 'analyzing')
- `clone_status`: Enum('pending', 'cloning', 'completed', 'failed')

**新增字段**:
```python
source_type = db.Column(
    db.Enum('git_remote', 'local_output'),
    default='git_remote',
    nullable=False,
    index=True
)
local_source_path = db.Column(db.String(1000))  # Path in coderwiki-output-docs/repos/
```

**字段说明**:
- `source_type`: 仓库来源类型
  - `git_remote`: Git远程仓库（现有模式）
  - `local_output`: 本地输出目录仓库（新增）
- `local_source_path`: 本地源路径，仅当source_type为local_output时使用

**验证规则**:
- 当 `source_type = 'local_output'` 时，`local_source_path` 必须非空
- 当 `source_type = 'git_remote'` 时，`local_path` 用于分析路径
- `local_source_path` 必须在 `coderwiki-output-docs/repos/` 目录下

**状态转换**:
```
local_output仓库:
[discovered] -> status='active', clone_status='completed'
[path_missing] -> status='error', clone_status='failed'
[path_restored] -> status='active', clone_status='completed'
```

### 新增方法

**Repository.get_analysis_path()**:
```python
def get_analysis_path(self) -> str:
    """获取用于分析的路径"""
    if self.source_type == 'local_output':
        return self.local_source_path
    else:
        return self.local_path
```

**Repository.is_ready_for_analysis()**:
```python
def is_ready_for_analysis(self) -> bool:
    """检查仓库是否准备好进行分析"""
    if self.source_type == 'local_output':
        return (
            self.local_source_path is not None and
            os.path.exists(self.local_source_path)
        )
    else:
        return (
            self.local_path is not None and
            self.clone_status == 'completed' and
            self.commit_hash is not None
        )
```

**Repository.create_local_repository()** (静态方法):
```python
@staticmethod
def create_local_repository(user_id: int, name: str, local_path: str,
                           description: str = None) -> 'Repository':
    """为本地仓库创建Repository实例"""
    return Repository(
        user_id=user_id,
        name=name,
        url='local://' + local_path,
        description=description,
        source_type='local_output',
        local_source_path=local_path,
        status='active',
        clone_status='completed'
    )
```

## Relationships

### 保持现有关系
- Repository -> User (多对一)
- Repository -> Document (一对多)
- Repository -> Task (一对多)
- Repository -> CodeAnalysis (一对多)

### 新增约束
- 同一用户不能有相同 `local_source_path` 的多个本地仓库
- `source_type` 字段默认值为 `git_remote` 确保向后兼容

## Database Migration

### 新增字段
```sql
ALTER TABLE repositories
ADD COLUMN source_type ENUM('git_remote', 'local_output')
DEFAULT 'git_remote' NOT NULL;

ALTER TABLE repositories
ADD COLUMN local_source_path VARCHAR(1000) NULL;

CREATE INDEX idx_repositories_source_type ON repositories(source_type);
```

### 数据迁移
```sql
-- 所有现有仓库默认为git_remote类型
UPDATE repositories
SET source_type = 'git_remote'
WHERE source_type IS NULL;
```

## Query Patterns

### 获取用户的仓库列表（包含来源信息）
```python
repositories = Repository.query.filter_by(user_id=user_id)\
    .order_by(Repository.source_type, Repository.name)\
    .all()
```

### 筛选特定来源类型的仓库
```python
# 只获取本地仓库
local_repos = Repository.query.filter_by(
    user_id=user_id,
    source_type='local_output'
).all()

# 只获取Git仓库
git_repos = Repository.query.filter_by(
    user_id=user_id,
    source_type='git_remote'
).all()
```

### 检查本地路径冲突
```python
existing_repo = Repository.query.filter_by(
    user_id=user_id,
    source_type='local_output',
    local_source_path=path
).first()
```

## Data Integrity

### 约束规则
1. `source_type` 为 `local_output` 时，`local_source_path` 不能为空
2. `local_source_path` 必须是绝对路径
3. 同一用户的本地仓库路径不能重复
4. 本地仓库的 `clone_status` 始终为 'completed'

### 验证函数
```python
def validate_repository_data(self):
    """验证仓库数据完整性"""
    if self.source_type == 'local_output':
        if not self.local_source_path:
            raise ValueError("Local repository must have local_source_path")
        if not os.path.isabs(self.local_source_path):
            raise ValueError("local_source_path must be absolute path")
```