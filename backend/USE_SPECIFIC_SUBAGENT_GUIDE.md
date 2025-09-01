# Claude Code特定子代理固定使用指南

## 1. BMAD子代理系统架构

CoderWiki系统集成了5个专业BMAD子代理：

### 可用子代理列表：
1. **Code Analyst (Alex)** - 代码分析师
   - ID: `code-analyst`
   - 专长：代码扫描、架构分析、模式识别
   
2. **Tech Architect (Sarah)** - 技术架构师  
   - ID: `tech-architect`
   - 专长：架构设计、技术选型、系统集成

3. **Flow Analyst (Jordan)** - 流程分析师
   - ID: `flow-analyst`
   - 专长：流程分析、时序图生成、业务规则提取

4. **Problem Solver (Dr. Morgan)** - 问题诊断专家
   - ID: `problem-solver`
   - 专长：问题诊断、风险评估、解决方案设计

5. **Doc Engineer (Maya)** - 文档工程师
   - ID: `doc-engineer`
   - 专长：文档生成、模板管理、质量控制

## 2. 固定使用特定子代理的方法

### 方法1：通过API参数指定

```python
# backend/app/api/repositories.py 调用示例
@bp.route('/repositories/<int:id>/generate-with-agent', methods=['POST'])
def generate_with_specific_agent(id):
    """使用特定子代理生成文档"""
    data = request.json
    
    # 指定要使用的子代理
    specific_agent = data.get('agent_id', 'code-analyst')  # 默认使用代码分析师
    use_only_agent = data.get('use_only_agent', False)     # 是否只使用该代理
    
    config = {
        'use_bmad': True,
        'specific_agent': specific_agent,    # 指定特定代理
        'use_only_agent': use_only_agent,    # 只使用该代理，不运行完整工作流
        'analysis_depth': 'detailed',
        'language': data.get('language', 'zh')
    }
    
    # 调用文档生成服务
    result = doc_service.generate_smart_document(repository_id=id, config=config)
    return jsonify(result)
```

### 方法2：修改BMAD Orchestrator配置

```python
# backend/app/utils/bmad_orchestrator.py
class BMADOrchestrator:
    def __init__(self, claude_client: ClaudeCodeClient, use_specific_agent: str = None):
        """
        初始化 BMAD 编排器
        
        Args:
            claude_client: Claude Code 客户端实例
            use_specific_agent: 指定只使用某个特定代理
        """
        self.claude_client = claude_client
        self.use_specific_agent = use_specific_agent
        
        # 如果指定了特定代理，只加载该代理
        if use_specific_agent:
            self.agents = self._load_specific_agent(use_specific_agent)
        else:
            self.agents = self._load_all_agents()
    
    def _load_specific_agent(self, agent_id: str) -> Dict:
        """加载特定代理"""
        all_agents = {
            'code-analyst': {
                'name': 'Alex',
                'role': 'Code Analyst',
                'tasks': ['scan-codebase', 'validate-analysis']
            },
            'flow-analyst': {
                'name': 'Jordan',
                'role': 'Flow Analyst',
                'tasks': ['analyze-complex-flows', 'validate-flow-analysis']
            },
            # ... 其他代理定义
        }
        
        if agent_id in all_agents:
            return {agent_id: all_agents[agent_id]}
        else:
            raise ValueError(f"Unknown agent: {agent_id}")
```

### 方法3：通过环境变量配置

```bash
# 设置环境变量来指定默认子代理
export USE_SPECIFIC_BMAD_AGENT=code-analyst
export BMAD_SINGLE_AGENT_MODE=true

# 启动服务
PORT=5007 python run.py
```

### 方法4：直接调用特定代理的任务

```python
# backend/app/services/document_generator.py
class DocumentGenerator:
    def generate_with_specific_agent(self, 
                                    repository: Repository, 
                                    agent_id: str,
                                    task: str = None) -> Dict:
        """
        使用特定的BMAD子代理生成文档
        
        Args:
            repository: 仓库对象
            agent_id: 代理ID (如 'code-analyst', 'flow-analyst')
            task: 指定任务 (可选，如 'scan-codebase', 'analyze-complex-flows')
        """
        # 初始化特定代理
        orchestrator = BMADOrchestrator(
            claude_client=self.claude_client,
            use_specific_agent=agent_id
        )
        
        # 配置代理任务
        agent_config = {
            'agent_id': agent_id,
            'task': task or self._get_default_task(agent_id),
            'analysis_depth': 'detailed',
            'output_format': 'markdown'
        }
        
        # 执行代理任务
        result = orchestrator.execute_single_agent(
            repo_path=repository.local_path,
            config=agent_config
        )
        
        return result
    
    def _get_default_task(self, agent_id: str) -> str:
        """获取代理的默认任务"""
        default_tasks = {
            'code-analyst': 'scan-codebase',
            'tech-architect': 'create-architecture-views',
            'flow-analyst': 'analyze-complex-flows',
            'problem-solver': 'diagnose-potential-problems',
            'doc-engineer': 'assemble-final-documentation'
        }
        return default_tasks.get(agent_id, 'analyze')
```

## 3. 实际使用示例

### 示例1：只使用Code Analyst (Alex)进行代码分析

```python
# 创建API请求
import requests

# 只使用代码分析师Alex
response = requests.post(
    'http://localhost:5007/api/repositories/13/generate-with-agent',
    json={
        'agent_id': 'code-analyst',
        'use_only_agent': True,
        'language': 'zh',
        'tasks': ['scan-codebase', 'analyze-dependencies']
    },
    cookies={'session': 'your_session_cookie'}
)

print(response.json())
```

### 示例2：只使用Flow Analyst (Jordan)分析业务流程

```python
# 只使用流程分析师Jordan
response = requests.post(
    'http://localhost:5007/api/repositories/13/generate-with-agent',
    json={
        'agent_id': 'flow-analyst',
        'use_only_agent': True,
        'language': 'zh',
        'tasks': ['analyze-complex-flows', 'generate-sequence-diagrams']
    },
    cookies={'session': 'your_session_cookie'}
)
```

### 示例3：通过命令行直接调用特定代理

```python
# test_specific_agent.py
from app.services.bmad_subagent_config import BMADSubagentConfig
from app.services.document_generator import DocumentGenerator

# 初始化配置
config = BMADSubagentConfig()
doc_generator = DocumentGenerator()

# 获取可用的代理列表
agents = config.get_subagent_agents()
print("可用的子代理：")
for agent in agents:
    print(f"- {agent['id']}: {agent['name']} ({agent['role']})")

# 选择特定代理
selected_agent = 'problem-solver'  # 使用Dr. Morgan进行问题诊断

# 执行特定代理任务
result = doc_generator.generate_with_specific_agent(
    repository=repository,
    agent_id=selected_agent,
    task='diagnose-potential-problems'
)

print(f"执行结果：{result}")
```

## 4. 配置文件示例

### 创建自定义代理配置文件

```yaml
# backend/config/specific_agent_config.yaml
specific_agent_mode:
  enabled: true
  default_agent: code-analyst
  
  # 各代理的专属配置
  agents:
    code-analyst:
      enabled: true
      tasks:
        - scan-codebase
        - analyze-dependencies
        - identify-patterns
      output_format: detailed_analysis
      
    flow-analyst:
      enabled: true
      tasks:
        - analyze-complex-flows
        - generate-sequence-diagrams
        - validate-flow-analysis
      include_diagrams: true
      
    problem-solver:
      enabled: true
      tasks:
        - diagnose-potential-problems
        - assess-risks
        - propose-solutions
      severity_levels: [critical, high, medium, low]
      
  # 执行策略
  execution_strategy:
    mode: single_agent  # single_agent | sequential | parallel
    timeout: 300  # 秒
    retry_on_failure: true
    max_retries: 3
```

## 5. 高级用法：组合特定代理

如果需要使用2-3个特定代理而不是全部5个：

```python
# 只使用Code Analyst和Problem Solver
class SelectiveAgentOrchestrator:
    def __init__(self, selected_agents: List[str]):
        """
        只使用选定的代理
        
        Args:
            selected_agents: 要使用的代理ID列表
        """
        self.selected_agents = selected_agents
        self.agents = {}
        
        # 只加载选定的代理
        all_agents = self._get_all_agent_definitions()
        for agent_id in selected_agents:
            if agent_id in all_agents:
                self.agents[agent_id] = all_agents[agent_id]
    
    def execute_selected_agents(self, repository_path: str) -> Dict:
        """执行选定的代理"""
        results = {}
        
        for agent_id, agent_info in self.agents.items():
            print(f"执行代理: {agent_info['name']} ({agent_id})")
            
            # 执行代理任务
            agent_result = self._execute_single_agent(
                agent_id=agent_id,
                agent_info=agent_info,
                repository_path=repository_path
            )
            
            results[agent_id] = agent_result
            
        return results

# 使用示例
orchestrator = SelectiveAgentOrchestrator(
    selected_agents=['code-analyst', 'problem-solver']
)
results = orchestrator.execute_selected_agents(repository_path)
```

## 6. 性能优化建议

### 单代理模式的优势：
- ⚡ **更快的响应速度**：只运行必要的分析
- 💰 **更低的API成本**：减少Claude API调用
- 🎯 **更精准的输出**：专注于特定任务
- 🔧 **更容易调试**：单一执行路径

### 适用场景：
1. **只需要代码分析**：使用code-analyst
2. **只需要架构图**：使用tech-architect  
3. **只需要流程图**：使用flow-analyst
4. **只需要问题诊断**：使用problem-solver
5. **只需要格式化文档**：使用doc-engineer

## 7. 注意事项

1. **依赖关系**：某些代理可能依赖其他代理的输出
   - doc-engineer通常需要其他代理的分析结果
   - flow-analyst可能需要code-analyst的代码扫描结果

2. **输出格式**：不同代理的输出格式可能不同
   - code-analyst：代码分析报告
   - flow-analyst：流程图和时序图
   - problem-solver：问题列表和解决方案

3. **性能考虑**：
   - 单代理模式更快但信息可能不完整
   - 完整工作流更全面但耗时更长

## 8. 故障排查

如果特定代理调用失败：

1. **检查代理ID是否正确**
```python
# 获取所有可用的代理ID
config = BMADSubagentConfig()
agents = config.get_subagent_agents()
valid_ids = [agent['id'] for agent in agents]
print(f"有效的代理ID: {valid_ids}")
```

2. **检查Claude API密钥**
```bash
echo $ANTHROPIC_API_KEY
```

3. **查看日志**
```bash
tail -f backend/logs/bmad-orchestrator.log
```

4. **测试单个代理连接**
```python
# 测试脚本
from app.utils.claude_client import ClaudeCodeClient

client = ClaudeCodeClient(api_key, workspace_id)
session = client.create_session()
print(f"Session created: {session}")
```

---

通过以上方法，你可以灵活地选择和使用特定的BMAD子代理，避免运行完整的5代理工作流，提高效率和降低成本。