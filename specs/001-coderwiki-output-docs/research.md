# Research & Analysis: 代码质量分析模块增强

## Technical Decisions

### Decision: 扩展现有Repository模型而非创建新模型
**Rationale**:
- 保持数据一致性和关系完整性
- 复用现有的Repository相关业务逻辑
- 最小化代码变更和维护复杂度

**Alternatives considered**:
- 创建独立的LocalRepository模型：会导致代码重复和数据割裂
- 使用继承关系：增加不必要的复杂性

### Decision: 使用 pathlib.Path 进行路径操作
**Rationale**:
- Python 3.4+ 标准库，更安全的路径处理
- 跨平台兼容性更好
- 与现有代码库的Path使用一致

**Alternatives considered**:
- os.path: 老旧的API，容易出现平台兼容性问题
- 手动字符串操作：容易出错，不安全

### Decision: 复用现有CodeAnalysisEngine，仅修改路径解析
**Rationale**:
- 保持分析结果格式一致性
- 避免重复实现分析逻辑
- 确保性能特性和配置选项一致

**Alternatives considered**:
- 创建专用的本地仓库分析器：会导致功能分化和维护负担

### Decision: 在仓库列表界面添加来源类型字段
**Rationale**:
- 用户需要清楚区分仓库来源
- 便于筛选和管理不同类型的仓库
- 保持界面简洁，不过度复杂化

**Alternatives considered**:
- 分离式界面：增加导航复杂度
- 图标标识：可能不够直观和明确

### Decision: 目录扫描采用按需触发，不实现自动监控
**Rationale**:
- 避免文件系统监控的性能开销
- 用户可控的刷新时机
- 符合现有系统的操作模式

**Alternatives considered**:
- 文件系统监控：复杂性高，资源消耗大
- 定时扫描：可能产生不必要的IO操作

## Architecture Analysis

### Current System Components
- **Repository Model**: 已有完整的仓库数据模型
- **AnalysisService**: 成熟的分析业务逻辑
- **CodeAnalysisEngine**: 强大的分析引擎
- **DirectoryService**: 统一的目录管理

### Integration Points
- Repository.local_path → Repository.get_analysis_path()
- AnalysisService.start_analysis() → 支持本地路径
- Repository API → 新增发现端点
- 前端仓库列表 → 显示来源和刷新按钮

### Risk Assessment
- **Low Risk**: 扩展现有模型字段
- **Low Risk**: 添加新的服务方法
- **Medium Risk**: 确保分析引擎路径兼容性
- **Low Risk**: 前端界面更新

## Performance Considerations

### Expected Load
- 本地仓库数量：100-500个典型
- 目录扫描频率：用户主动触发，每天几次
- 分析负载：与现有Git仓库相同

### Optimization Strategies
- 复用现有的LargeRepositoryOptimizer
- 利用现有的缓存机制
- 批量数据库操作避免N+1查询

## Security Review

### Attack Vectors
- 路径遍历攻击：已通过DirectoryService约束
- 符号链接攻击：pathlib.resolve()处理
- 权限提升：仅读取指定输出目录

### Mitigation Strategies
- 严格限制扫描路径在coderwiki-output-docs/repos/下
- 验证路径规范化
- 保持现有的用户权限检查

## Implementation Complexity

### Low Complexity Components
- Repository模型扩展（2个新字段）
- API端点添加（1个新端点）
- 前端界面更新（来源标识显示）

### Medium Complexity Components
- RepositoryService扫描逻辑
- AnalysisService路径处理修改

### Zero New Dependencies
- 完全基于现有技术栈
- 无需引入新的第三方库