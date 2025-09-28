# MySQL 重启后连接问题解决方案

## 问题描述
每次重启电脑后，MySQL数据库无法连接的问题。

## 问题分析
通过检查发现：
1. MySQL服务已正确配置为开机自启动（plist文件配置正确）
2. 服务能够启动，但可能存在启动时序问题
3. 应用程序在MySQL完全就绪前尝试连接导致失败

## 解决方案

### 1. 使用启动检查脚本
我们创建了两个脚本来解决这个问题：

#### `scripts/mysql_startup_check.sh`
- 检查MySQL是否完全启动并可接受连接
- 最多尝试30次，每次间隔2秒
- 连接成功后返回成功状态

#### `scripts/start_mysql_with_check.sh`
- 启动MySQL服务
- 调用检查脚本等待MySQL完全就绪
- 显示连接信息和可用数据库

### 2. 使用方法

#### 重启电脑后手动启动（推荐）
```bash
./scripts/start_mysql_with_check.sh
```

#### 仅检查MySQL状态
```bash
./scripts/mysql_startup_check.sh
```

#### 传统方式启动
```bash
brew services start mysql
# 然后等待几秒钟再尝试连接
```

### 3. 数据库连接信息
- **主机**: localhost
- **端口**: 3306
- **用户**: root
- **密码**: 123456

### 4. 可用数据库
- coderwiki
- coderwiki_dev
- datacloud_dev
- datacloud_integration_test
- datacloud_test
- docmgmt
- reportviewer
- slowsql

## 预防措施

1. **应用程序中添加重试机制**：在应用代码中添加数据库连接重试逻辑
2. **增加连接超时时间**：给MySQL更多时间完全启动
3. **使用健康检查**：在应用启动前检查数据库可用性

## 故障排除

如果仍然遇到连接问题：

1. 检查MySQL服务状态：
   ```bash
   brew services list | grep mysql
   ```

2. 查看MySQL错误日志：
   ```bash
   tail -50 /opt/homebrew/var/mysql/lshl124deMacBook-Pro.local.err
   ```

3. 手动重启MySQL服务：
   ```bash
   brew services restart mysql
   ```

4. 检查端口是否被占用：
   ```bash
   lsof -i :3306
   ```