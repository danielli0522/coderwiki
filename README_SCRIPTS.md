# CoderWiki 启动脚本使用指南

## 📋 脚本概览

本项目提供了三个便捷的脚本来管理 CoderWiki 服务：

- `start_coderwiki.sh` - 启动服务
- `stop_coderwiki.sh` - 停止服务
- `status_coderwiki.sh` - 检查服务状态

## 🚀 启动服务

### 基本启动

```bash
./start_coderwiki.sh
```

使用默认端口 5001 启动服务

### 指定端口启动

```bash
./start_coderwiki.sh 8080
```

使用端口 8080 启动服务

### 启动脚本功能

- ✅ 自动检查 Python 环境
- ✅ 验证虚拟环境
- ✅ 检查端口占用
- ✅ 自动创建必要目录
- ✅ 设置环境变量
- ✅ 显示访问地址和用户信息

## 🛑 停止服务

### 停止默认端口服务

```bash
./stop_coderwiki.sh
```

### 停止指定端口服务

```bash
./stop_coderwiki.sh 8080
```

### 停止脚本功能

- ✅ 检查进程状态
- ✅ 显示运行中的进程
- ✅ 安全停止进程
- ✅ 确认操作

## 📊 检查服务状态

### 检查默认端口状态

```bash
./status_coderwiki.sh
```

### 检查指定端口状态

```bash
./status_coderwiki.sh 8080
```

### 状态检查功能

- ✅ 检查进程运行状态
- ✅ 测试服务响应
- ✅ 显示访问地址
- ✅ 显示默认用户信息

## 🌐 访问地址

启动成功后，可以通过以下地址访问：

### 本地访问

- **主页**: http://localhost:5001
- **登录页**: http://localhost:5001/login
- **仪表板**: http://localhost:5001/dashboard
- **系统状态**: http://localhost:5001/system-status

### 网络访问

- **主页**: http://10.11.75.81:5001
- **登录页**: http://10.11.75.81:5001/login
- **仪表板**: http://10.11.75.81:5001/dashboard

## 🔑 默认用户账户

系统预置了以下测试账户：

| 用户名   | 邮箱                | 密码  |
| -------- | ------------------- | ----- |
| admin    | admin@coderwiki.com | admin |
| demo     | demo@coderwiki.com  | demo  |
| testuser | test@example.com    | test  |
| test     | test@test.com       | test  |

## ⚙️ 环境变量

启动脚本会自动设置以下环境变量：

```bash
PORT=5001                    # 服务端口
FLASK_ENV=development        # Flask环境
FLASK_DEBUG=True            # 调试模式
FLASK_HOST=0.0.0.0          # 监听地址
```

## 🔧 故障排除

### 端口被占用

如果端口被占用，启动脚本会提示是否停止现有进程：

```bash
⚠️  警告: 端口 5001 已被占用
是否停止现有进程? (y/N): y
```

### 虚拟环境问题

确保虚拟环境已正确安装：

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 权限问题

确保脚本有执行权限：

```bash
chmod +x start_coderwiki.sh
chmod +x stop_coderwiki.sh
chmod +x status_coderwiki.sh
```

## 📝 使用示例

### 完整的使用流程

```bash
# 1. 检查服务状态
./status_coderwiki.sh

# 2. 启动服务
./start_coderwiki.sh

# 3. 在浏览器中访问
# http://localhost:5001

# 4. 停止服务
./stop_coderwiki.sh
```

### 开发环境快速重启

```bash
# 停止服务
./stop_coderwiki.sh

# 启动服务
./start_coderwiki.sh
```

## 🎯 注意事项

1. **网络访问**: 服务配置为监听所有网络接口，其他人可以通过网络 IP 访问
2. **安全考虑**: 当前配置适合开发环境，生产环境需要额外的安全配置
3. **端口冲突**: 如果端口被占用，脚本会提示处理
4. **虚拟环境**: 确保在正确的虚拟环境中运行

## 📞 技术支持

如果遇到问题，请检查：

1. Python 版本是否为 3.8+
2. 虚拟环境是否正确安装
3. 依赖包是否完整安装
4. 端口是否被其他程序占用
