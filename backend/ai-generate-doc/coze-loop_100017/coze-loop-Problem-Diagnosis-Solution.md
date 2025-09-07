# coze-loop 问题诊断与快速解决方案

基于复杂流程深度分析文档的结论，本文档为每个核心流程预测可能出现的问题并提供解决方案。

## 一、Prompt 模板执行引擎

| 序号 | 潜在问题现象 (用户视角) | 技术层面的根本原因 | 解决方案 |
|------|-------------------------|-------------------|----------|
| 1 | Prompt 执行时返回"模板渲染失败" | Jinja2 模板语法错误或变量缺失 | 1. 检查模板语法：`/backend/modules/prompt/pkg/template/` 下的 Jinja 解析器日志<br>2. 验证变量完整性：确保所有 {{variable}} 都有对应值<br>3. 使用 Playground 的调试模式逐步测试 |
| 2 | 流式响应突然中断，页面显示"连接已断开" | WebSocket 连接超时或 LLM 服务异常中断 | 1. 检查 `PROMPT_TIMEOUT_MS` 配置，默认 8 分钟可能不够<br>2. 查看 LLM 服务状态：`curl -X GET http://localhost:8080/health`<br>3. 检查 Nginx 超时配置：`proxy_read_timeout` 应 >= 480s |
| 3 | 多轮对话时前几轮内容丢失 | 消息历史记录超过模型上下文窗口限制 | 1. 检查模型的 max_tokens 配置<br>2. 实施消息裁剪策略：保留最近 N 轮对话<br>3. 使用摘要技术压缩历史消息 |
| 4 | Prompt 执行非常缓慢，响应时间超过 30 秒 | LLM 服务限流或网络延迟高 | 1. 检查限流配置：`redis-cli get rate_limit:*`<br>2. 测试网络延迟：`ping {llm_endpoint}`<br>3. 启用模型负载均衡，配置多个提供商 |
| 5 | 变量替换后出现乱码或特殊字符 | 字符编码问题或未正确转义 | 1. 确保所有输入使用 UTF-8 编码<br>2. 对特殊字符进行转义：`\n`、`"`、`'`<br>3. 检查数据库字符集：`SHOW VARIABLES LIKE 'character%'` |

## 二、实验运行调度器

| 序号 | 潜在问题现象 (用户视角) | 技术层面的根本原因 | 解决方案 |
|------|-------------------------|-------------------|----------|
| 6 | 实验一直显示"运行中"，长时间无进展 | 任务队列阻塞或 Worker 进程崩溃 | 1. 检查 RocketMQ 消费者状态：`sh mqadmin consumerProgress -g experiment_group`<br>2. 查看 Worker 日志：`docker logs coze-loop-app | grep ERROR`<br>3. 手动重启消费者：`curl -X POST /api/internal/consumer/restart` |
| 7 | 实验结果统计不准确，部分数据缺失 | 任务执行失败但未正确记录 | 1. 查询失败任务：`SELECT * FROM expt_run_task WHERE status='failed'`<br>2. 检查 ClickHouse 写入延迟：`SELECT count() FROM trace_spans WHERE expt_id=?`<br>3. 手动触发结果重新聚合：`POST /api/experiment/{id}/reaggregate` |
| 8 | 并发实验时系统变慢或崩溃 | 并发任务数超过系统处理能力 | 1. 调整并发限制：`EXPT_MAX_CONCURRENT_TASKS=50`<br>2. 增加 Worker 数量：`WORKER_POOL_SIZE=40`<br>3. 优化数据库连接池：`max_connections=200` |
| 9 | 实验无法启动，提示"资源锁定" | 分布式锁未正确释放 | 1. 检查 Redis 锁：`redis-cli keys expt_lock_*`<br>2. 手动释放死锁：`redis-cli del expt_lock_{id}`<br>3. 设置锁超时：`EXPIRE expt_lock_{id} 3600` |
| 10 | 大数据集实验内存溢出 | 一次性加载过多数据到内存 | 1. 启用分批处理：`EXPT_TASK_BATCH_SIZE=20`<br>2. 增加 JVM 堆内存：`-Xmx8g`<br>3. 使用流式处理替代批量加载 |

## 三、Trace 数据采集链路

| 序号 | 潜在问题现象 (用户视角) | 技术层面的根本原因 | 解决方案 |
|------|-------------------------|-------------------|----------|
| 11 | Trace 数据查询不到或延迟很高 | ClickHouse 写入积压或索引失效 | 1. 检查写入队列：`SELECT count() FROM system.asynchronous_inserts`<br>2. 优化表结构：`OPTIMIZE TABLE trace_spans FINAL`<br>3. 重建索引：`ALTER TABLE trace_spans UPDATE idx = idx WHERE 1` |
| 12 | SDK 上报失败，返回 "Payload too large" | 单次上报数据超过 1MB 限制 | 1. 启用批量上报：`sdk.setBatchSize(100)`<br>2. 压缩上报数据：`sdk.enableCompression(true)`<br>3. 增加限制：`TRACE_MAX_PAYLOAD_SIZE=5MB` |
| 13 | ClickHouse 磁盘空间快速增长 | 数据保留策略未生效或压缩率低 | 1. 检查 TTL 设置：`SHOW CREATE TABLE trace_spans`<br>2. 手动清理过期数据：`ALTER TABLE DELETE WHERE timestamp < now() - 30`<br>3. 调整压缩级别：`TRACE_COMPRESSION_LEVEL=9` |
| 14 | Trace 树状结构显示错误 | Span 父子关系错误或时间戳不一致 | 1. 验证 trace_id 和 parent_span_id 关系<br>2. 检查时钟同步：`ntpdate -q pool.ntp.org`<br>3. 修复孤儿 Span：`UPDATE spans SET parent_id=NULL WHERE parent_id NOT IN (SELECT span_id FROM spans)` |
| 15 | 高并发时大量数据丢失 | 写入缓冲区溢出 | 1. 增加缓冲区大小：`TRACE_BUFFER_SIZE=10000`<br>2. 减少批处理超时：`TRACE_BATCH_TIMEOUT_MS=1000`<br>3. 启用持久化队列：使用 Kafka 替代内存缓冲 |

## 四、LLM 模型路由系统

| 序号 | 潜在问题现象 (用户视角) | 技术层面的根本原因 | 解决方案 |
|------|-------------------------|-------------------|----------|
| 16 | 模型调用失败："认证失败" | API Key 过期或配置错误 | 1. 验证 API Key：`curl -H "Authorization: Bearer {key}" {endpoint}/models`<br>2. 检查配置文件：`/conf/model_config.yaml`<br>3. 重新加载配置：`POST /api/internal/config/reload` |
| 17 | 响应极慢或超时 | 模型服务过载或网络问题 | 1. 切换备用模型：修改 `primary_provider` 配置<br>2. 检查网络连通性：`traceroute {model_endpoint}`<br>3. 启用本地缓存：`MODEL_CACHE_ENABLED=true` |
| 18 | 成本异常增高 | Token 计算错误或使用了昂贵模型 | 1. 审计 Token 使用：`SELECT SUM(tokens) FROM model_usage WHERE date=today()`<br>2. 设置成本预警：`COST_ALERT_THRESHOLD=100`<br>3. 限制模型选择：只允许使用指定模型列表 |
| 19 | 模型切换失败，一直使用故障模型 | 健康检查机制失效 | 1. 手动标记不健康：`redis-cli set model:{name}:health unhealthy`<br>2. 调整检查间隔：`MODEL_HEALTH_CHECK_INTERVAL_S=10`<br>3. 查看健康检查日志：`grep "health check" /var/log/app.log` |
| 20 | 不同模型返回格式不一致 | 响应格式转换器配置错误 | 1. 统一响应格式：实现 `ResponseTransformer` 接口<br>2. 添加格式验证：`validateResponse(response, schema)`<br>3. 配置模型特定转换器：`model_transformers.yaml` |

## 五、评测器执行引擎

| 序号 | 潜在问题现象 (用户视角) | 技术层面的根本原因 | 解决方案 |
|------|-------------------------|-------------------|----------|
| 21 | 自定义评测器执行失败 | 脚本语法错误或安全沙箱限制 | 1. 本地测试脚本：`python evaluator_script.py test_input.json`<br>2. 检查沙箱日志：`/var/log/sandbox/evaluator.log`<br>3. 放宽沙箱限制（谨慎）：`EVALUATOR_SANDBOX_ENABLED=false` |
| 22 | 评分结果全部为 0 或 100 | 评分逻辑错误或阈值设置不当 | 1. 审查评测逻辑：检查条件判断和计算公式<br>2. 调试模式运行：`EVALUATOR_DEBUG=true`<br>3. 添加中间日志：在关键步骤输出中间结果 |
| 23 | 评测超时导致实验失败 | 评测逻辑复杂度过高 | 1. 增加超时时间：`EVALUATOR_TIMEOUT_MS=10000`<br>2. 优化评测算法：避免嵌套循环和递归<br>3. 异步执行评测：将评测任务放入队列 |
| 24 | LLM 评测器成本过高 | 每个样本都调用 LLM 评测 | 1. 实施采样策略：只评测 10% 的样本<br>2. 使用更便宜的模型：配置专门的评测模型<br>3. 缓存评测结果：相同输入使用缓存结果 |
| 25 | 评测结果不稳定，相同输入不同分数 | LLM 评测的随机性或并发问题 | 1. 设置温度参数：`temperature=0`<br>2. 使用种子值：`seed=42`<br>3. 实施重试机制：多次评测取平均值 |

## 六、用户认证授权

| 序号 | 潜在问题现象 (用户视角) | 技术层面的根本原因 | 解决方案 |
|------|-------------------------|-------------------|----------|
| 26 | 登录后立即被踢出 | Token 过期时间设置过短或时钟不同步 | 1. 检查 Token TTL：`JWT_ACCESS_TOKEN_TTL=7200`<br>2. 同步系统时间：`ntpdate -s time.nist.gov`<br>3. 检查客户端时间：浏览器控制台 `new Date()` |
| 27 | 权限正确但访问被拒绝 | 权限缓存未更新或 RBAC 配置错误 | 1. 清除权限缓存：`redis-cli del permissions:*`<br>2. 重新加载权限：`POST /api/auth/reload-permissions`<br>3. 检查角色权限：`SELECT * FROM role_permissions WHERE role_id=?` |
| 28 | 账号被锁定无法登录 | 密码错误次数过多触发锁定 | 1. 解锁账号：`UPDATE users SET locked=0 WHERE email=?`<br>2. 清除失败计数：`redis-cli del login_attempts:{email}`<br>3. 调整锁定策略：`MAX_LOGIN_ATTEMPTS=10` |
| 29 | Token 刷新失败 | Refresh Token 已使用或过期 | 1. 检查 Token 状态：`SELECT * FROM refresh_tokens WHERE token=?`<br>2. 延长有效期：`JWT_REFRESH_TOKEN_TTL=604800`<br>3. 实施滑动过期：每次使用更新过期时间 |
| 30 | 会话串号，看到别人的数据 | Session 管理错误或缓存键冲突 | 1. 检查 Session ID 生成：确保使用 UUID<br>2. 隔离用户缓存：`cache_key = f"{user_id}:{resource}"`<br>3. 审计会话日志：`grep "session conflict" /var/log/auth.log` |

## 七、实验结果聚合分析

| 序号 | 潜在问题现象 (用户视角) | 技术层面的根本原因 | 解决方案 |
|------|-------------------------|-------------------|----------|
| 31 | 统计指标计算错误 | 聚合算法实现有误或数据不完整 | 1. 验证算法：对比手动计算结果<br>2. 检查数据完整性：`SELECT COUNT(*) vs SUM(score) != NULL`<br>3. 使用成熟统计库：numpy, pandas |
| 32 | 报告生成失败或格式错误 | 模板渲染错误或依赖服务不可用 | 1. 检查模板文件：`/templates/report.html`<br>2. 验证 PDF 服务：`curl http://pdf-service/health`<br>3. 降级到简单格式：先生成 JSON，再转换 |
| 33 | 聚合过程内存溢出 | 一次性加载过多数据 | 1. 分批聚合：`AGGREGATION_BATCH_SIZE=5000`<br>2. 使用流式聚合：逐条处理而非全量加载<br>3. 增加内存限制：`-Xmx16g` |
| 34 | 百分位数计算耗时过长 | 数据量大且算法复杂度高 | 1. 使用近似算法：T-Digest 或 HyperLogLog<br>2. 预计算常用百分位：50, 90, 95, 99<br>3. 并行计算：按评测器分组并行处理 |
| 35 | 对比分析显示异常差异 | 基线选择错误或数据对齐问题 | 1. 验证基线实验 ID 正确<br>2. 确保相同的评测数据集<br>3. 检查版本兼容性：评测器版本是否一致 |

## 八、消息队列消费处理

| 序号 | 潜在问题现象 (用户视角) | 技术层面的根本原因 | 解决方案 |
|------|-------------------------|-------------------|----------|
| 36 | 任务长时间未执行 | 消息积压或消费者停止 | 1. 查看积压情况：`sh mqadmin consumerProgress -g {group}`<br>2. 增加消费者：`CONSUMER_POOL_SIZE=20`<br>3. 重置消费位点：`sh mqadmin resetOffset -g {group} -t {topic}` |
| 37 | 任务重复执行 | 消息重复投递或幂等性失效 | 1. 检查幂等键：`SELECT * FROM processed_messages WHERE msg_id=?`<br>2. 启用消息去重：`rocketmq.consumer.consumeMessageBatchMaxSize=1`<br>3. 加强幂等逻辑：使用数据库唯一索引 |
| 38 | 死信队列堆积 | 处理逻辑有 bug 导致持续失败 | 1. 分析死信原因：`SELECT * FROM dlq_messages ORDER BY created_at DESC`<br>2. 修复 bug 后重新投递：`sh mqadmin sendMessage -t {topic} -b {body}`<br>3. 设置告警：死信数量 > 100 时通知 |
| 39 | 消费者频繁重启 | 内存泄漏或未捕获异常 | 1. 分析堆转储：`jmap -dump:format=b,file=heap.bin {pid}`<br>2. 查看错误日志：`grep "FATAL" /var/log/consumer.log`<br>3. 添加全局异常处理：`try-catch` 包裹消费逻辑 |
| 40 | 消息乱序处理 | 并发消费导致顺序错乱 | 1. 使用顺序消息：`producer.send(msg, messageQueueSelector)`<br>2. 单线程消费：`consumeThreadMin=1, consumeThreadMax=1`<br>3. 基于业务键分区：确保相同键的消息进入同一队列 |

## 九、限流熔断机制

| 序号 | 潜在问题现象 (用户视角) | 技术层面的根本原因 | 解决方案 |
|------|-------------------------|-------------------|----------|
| 41 | 正常请求被限流 | 限流阈值设置过低或计算错误 | 1. 调整限流阈值：`RATE_LIMIT_MAX_REQUESTS=200`<br>2. 检查限流键：`redis-cli keys rate_limit:*`<br>3. 使用滑动窗口：避免突发流量误判 |
| 42 | 服务熔断后无法恢复 | 熔断恢复机制失效 | 1. 手动关闭熔断：`redis-cli set circuit:{service}:state CLOSED`<br>2. 调整恢复时间：`CIRCUIT_TIMEOUT_S=10`<br>3. 检查健康检查：确保测试请求能成功 |
| 43 | 限流不均匀，某些用户总是被限 | 限流键设计不合理 | 1. 优化限流键：结合 user_id + api_path<br>2. 实施分级限流：VIP 用户更高配额<br>3. 使用令牌桶算法：平滑限流 |
| 44 | 熔断误判，健康服务被熔断 | 错误率统计窗口过小或阈值过低 | 1. 增加统计窗口：`CIRCUIT_WINDOW_SIZE=100`<br>2. 提高阈值：`CIRCUIT_ERROR_THRESHOLD=70`<br>3. 区分错误类型：4xx 不计入熔断统计 |
| 45 | 限流后用户体验差 | 直接拒绝请求，没有降级方案 | 1. 实施降级策略：返回缓存数据<br>2. 队列缓冲：将请求放入队列延迟处理<br>3. 友好提示：返回预计等待时间 |

## 十、API 网关路由

| 序号 | 潜在问题现象 (用户视角) | 技术层面的根本原因 | 解决方案 |
|------|-------------------------|-------------------|----------|
| 46 | API 404 错误，路由找不到 | 路由配置错误或未注册 | 1. 检查路由注册：`/api/router.go` 和 `router_gen.go`<br>2. 验证路径匹配：注意大小写和尾部斜杠<br>3. 查看路由表：`GET /api/internal/routes` |
| 47 | 请求超时 | 后端服务响应慢或网关超时设置过短 | 1. 增加超时：`GATEWAY_TIMEOUT_S=60`<br>2. 检查后端延迟：启用慢查询日志<br>3. 添加超时控制：`context.WithTimeout()` |
| 48 | 中间件执行顺序错误 | 中间件注册顺序不当 | 1. 检查中间件顺序：认证应在业务逻辑前<br>2. 显式指定顺序：`middleware.Order()`<br>3. 添加依赖检查：确保前置中间件已执行 |
| 49 | 大文件上传失败 | 请求体超过大小限制 | 1. 增加限制：`GATEWAY_MAX_REQUEST_SIZE=100MB`<br>2. 使用分片上传：客户端分块传输<br>3. 配置 Nginx：`client_max_body_size 100M` |
| 50 | CORS 跨域错误 | CORS 头配置不正确 | 1. 配置允许的源：`Access-Control-Allow-Origin: *`<br>2. 处理预检请求：`OPTIONS` 方法返回正确头<br>3. 允许认证信息：`Access-Control-Allow-Credentials: true` |

## 十一、分布式事务处理

| 序号 | 潜在问题现象 (用户视角) | 技术层面的根本原因 | 解决方案 |
|------|-------------------------|-------------------|----------|
| 51 | 数据不一致，部分更新成功部分失败 | 事务协调器崩溃或网络分区 | 1. 执行补偿：`SELECT * FROM tx_log WHERE status='pending'`<br>2. 手动回滚：调用各服务的回滚接口<br>3. 启用自动补偿：`COMPENSATION_ENABLED=true` |
| 52 | 事务长时间处于待处理状态 | 死锁或资源等待超时 | 1. 检测死锁：`SHOW ENGINE INNODB STATUS`<br>2. 设置锁超时：`innodb_lock_wait_timeout=10`<br>3. 优化锁顺序：按固定顺序获取资源 |
| 53 | 补偿操作失败 | 补偿逻辑错误或数据已变更 | 1. 实施版本控制：乐观锁避免覆盖<br>2. 记录补偿日志：便于人工介入<br>3. 设计幂等补偿：多次执行结果一致 |
| 54 | 事务性能差，响应时间长 | 两阶段提交开销大 | 1. 使用 Saga 模式：避免锁定资源<br>2. 异步处理：将事务改为最终一致性<br>3. 减少参与者：合并服务减少协调开销 |
| 55 | 事务日志爆炸性增长 | 日志清理策略失效 | 1. 定期清理：`DELETE FROM tx_log WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)`<br>2. 归档历史数据：移到冷存储<br>3. 压缩日志：`OPTIMIZE TABLE tx_log` |

## 十二、安全防护机制

| 序号 | 潜在问题现象 (用户视角) | 技术层面的根本原因 | 解决方案 |
|------|-------------------------|-------------------|----------|
| 56 | 正常请求被误判为攻击 | WAF 规则过于严格 | 1. 白名单处理：添加可信 IP<br>2. 调整规则敏感度：降低误报率<br>3. 学习模式：收集正常流量特征 |
| 57 | SQL 注入攻击成功 | 参数化查询未正确使用 | 1. 审计所有 SQL：确保使用预编译语句<br>2. 启用 SQL 审计：`general_log=ON`<br>3. 部署数据库防火墙：如 GreenSQL |
| 58 | 敏感数据泄露 | 响应中包含内部信息 | 1. 实施数据脱敏：移除敏感字段<br>2. 错误信息标准化：不暴露技术细节<br>3. 审计日志：记录所有数据访问 |
| 59 | XSS 攻击成功 | 输出未正确转义 | 1. 使用模板引擎自动转义<br>2. 设置 CSP 头：`Content-Security-Policy`<br>3. 输入验证：拒绝包含脚本的输入 |
| 60 | 暴力破解攻击 | 缺少速率限制和账号锁定 | 1. 实施登录限流：每分钟最多 5 次<br>2. 启用验证码：连续失败后要求验证<br>3. IP 黑名单：自动封禁攻击 IP |

## 通用故障排查步骤

### 1. 日志分析
```bash
# 查看应用日志
docker logs coze-loop-app | grep ERROR | tail -100

# 查看 Nginx 日志
docker exec coze-loop-nginx tail -f /var/log/nginx/error.log

# 查看数据库慢查询
mysql -u root -p -e "SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10"
```

### 2. 性能监控
```bash
# 查看系统资源
docker stats

# 查看数据库连接
mysql -u root -p -e "SHOW PROCESSLIST"

# 查看 Redis 内存
redis-cli info memory
```

### 3. 服务健康检查
```bash
# 检查所有服务状态
curl http://localhost:8080/health

# 测试数据库连接
mysql -u root -p -e "SELECT 1"

# 测试 Redis 连接
redis-cli ping
```

### 4. 配置验证
```bash
# 验证环境变量
docker exec coze-loop-app env | grep COZE_LOOP

# 检查配置文件
docker exec coze-loop-app cat /app/conf/application.yaml

# 验证模型配置
curl http://localhost:8080/api/internal/config/models
```

### 5. 数据恢复
```bash
# 备份数据库
mysqldump -u root -p coze_loop > backup.sql

# 恢复数据库
mysql -u root -p coze_loop < backup.sql

# 清理缓存
redis-cli FLUSHDB
```

## 预防性维护建议

1. **定期备份**：每日备份数据库和配置文件
2. **监控告警**：设置关键指标阈值告警
3. **容量规划**：预估增长趋势，提前扩容
4. **安全审计**：定期进行安全扫描和渗透测试
5. **性能优化**：定期分析慢查询和性能瓶颈
6. **版本管理**：建立规范的版本发布流程
7. **灾难演练**：定期进行故障恢复演练
8. **文档更新**：保持运维文档与系统同步