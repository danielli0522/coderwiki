# Quickstart: 代码质量分析模块增强

## 功能验证流程

### 前置条件
1. CoderWiki系统正常运行
2. `coderwiki-output-docs/repos/` 目录存在
3. 目录中至少有一个代码仓库（用于测试）
4. 用户已登录系统

### 验证步骤

#### 1. 验证本地仓库发现功能
**步骤**:
1. 访问仓库列表页面 `http://localhost:5001/repositories`
2. 点击"刷新本地仓库"按钮
3. 观察页面响应和新增仓库

**预期结果**:
- 页面显示发现的本地仓库数量
- 新仓库出现在列表中
- 每个仓库显示"本地"来源标识

**验证API**:
```bash
curl -X POST http://localhost:5001/api/repositories/discover \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>"
```

#### 2. 验证仓库来源标识显示
**步骤**:
1. 在仓库列表中查看所有仓库
2. 确认每个仓库都有来源类型标识
3. 测试按来源类型筛选功能

**预期结果**:
- Git仓库显示"Git"标识
- 本地仓库显示"本地"标识
- 筛选功能正常工作

**验证API**:
```bash
# 获取所有仓库
curl http://localhost:5001/api/repositories

# 只获取本地仓库
curl "http://localhost:5001/api/repositories?source_type=local_output"

# 只获取Git仓库
curl "http://localhost:5001/api/repositories?source_type=git_remote"
```

#### 3. 验证本地仓库代码质量分析
**步骤**:
1. 选择一个本地仓库
2. 启动代码质量分析
3. 等待分析完成
4. 查看分析结果

**预期结果**:
- 分析启动成功
- 分析进度正常显示
- 生成完整的质量报告
- 报告格式与Git仓库一致

**验证API**:
```bash
# 启动分析
curl -X POST http://localhost:5001/api/analysis/start \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": 123,
    "analysis_types": ["structure", "complexity", "quality"]
  }'

# 检查分析状态
curl http://localhost:5001/api/analysis/status/456

# 获取分析结果
curl http://localhost:5001/api/analysis/results/123
```

#### 4. 验证路径变化处理
**步骤**:
1. 临时移动或重命名 `coderwiki-output-docs/repos/` 中的一个仓库目录
2. 访问仓库列表页面
3. 尝试分析被移动的仓库
4. 恢复仓库位置并刷新

**预期结果**:
- 被移动的仓库标记为"不可用"状态
- 分析请求返回适当的错误信息
- 恢复后刷新可以重新识别仓库

#### 5. 验证重复仓库处理
**步骤**:
1. 确保同一个仓库既存在于Git来源又存在于本地输出目录
2. 观察仓库列表中的显示方式
3. 测试对该仓库的分析功能

**预期结果**:
- 仓库合并显示为一个条目
- 显示"多来源"标识
- 可以选择分析来源

### 性能验证

#### 响应时间测试
**目标**: 验证API响应时间符合要求
```bash
# 仓库列表响应时间 (<200ms)
time curl http://localhost:5001/api/repositories

# 发现功能响应时间
time curl -X POST http://localhost:5001/api/repositories/discover
```

#### 大量仓库测试
**目标**: 验证系统处理多个本地仓库的能力
1. 在 `coderwiki-output-docs/repos/` 中放置20+个仓库目录
2. 执行发现功能
3. 验证分页和筛选功能

### 错误场景测试

#### 权限错误
```bash
# 未登录访问
curl http://localhost:5001/api/repositories/discover
# 应返回 401 Unauthorized
```

#### 路径错误
```bash
# 访问不存在的分析结果
curl http://localhost:5001/api/analysis/results/999999
# 应返回 404 Not Found
```

#### 无效参数
```bash
# 无效的source_type
curl "http://localhost:5001/api/repositories?source_type=invalid"
# 应返回 400 Bad Request
```

### 数据完整性验证

#### 数据库检查
```sql
-- 验证新字段
SELECT id, name, source_type, local_source_path
FROM repositories
WHERE source_type = 'local_output';

-- 验证数据一致性
SELECT COUNT(*) FROM repositories
WHERE source_type = 'local_output'
AND local_source_path IS NULL;
-- 应该返回 0
```

#### 备份兼容性
1. 创建数据库备份
2. 恢复到新版本
3. 验证所有现有仓库自动设置为 `git_remote` 类型

### 回归测试

#### 现有功能验证
1. Git仓库克隆功能正常
2. 现有分析功能不受影响
3. 用户权限控制正常
4. 现有API端点功能完整

### 成功标准

所有验证步骤通过后，确认：
- ✅ 本地仓库发现和管理功能正常
- ✅ 来源标识显示和筛选功能正常
- ✅ 本地仓库分析功能完整
- ✅ 错误处理和边缘情况处理正确
- ✅ 性能指标符合要求
- ✅ 现有功能向后兼容
- ✅ 数据完整性得到保证

### 故障排除

#### 常见问题
1. **发现功能无响应**: 检查目录权限和路径
2. **分析失败**: 验证仓库路径存在且可读
3. **来源标识不显示**: 检查前端模板更新
4. **数据库错误**: 验证迁移脚本执行