#!/usr/bin/env python3
"""
启动CoderWiki服务，支持外部访问

这个脚本会启动CoderWiki服务并配置为允许非本机访问。
会自动检测本机IP地址并提供访问信息。
"""

import os
import sys
import subprocess
import socket
import time
from pathlib import Path


def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 连接到一个外部地址来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # 备用方法
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception:
            return "127.0.0.1"


def check_port_available(port):
    """检查端口是否可用"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(('localhost', port))
        s.close()
        return result != 0  # 0表示端口被占用
    except Exception:
        return True


def stop_existing_service(port):
    """停止占用指定端口的服务"""
    try:
        # 查找占用端口的进程
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"🔄 发现端口 {port} 被以下进程占用: {', '.join(pids)}")

            for pid in pids:
                try:
                    subprocess.run(['kill', pid], check=True)
                    print(f"✅ 已停止进程 {pid}")
                    time.sleep(1)
                except subprocess.CalledProcessError:
                    print(f"⚠️  无法停止进程 {pid}")

    except Exception as e:
        print(f"⚠️  停止进程时出错: {e}")


def start_service():
    """启动CoderWiki服务"""

    # 检查项目目录
    project_root = Path(__file__).parent
    backend_dir = project_root / 'backend'

    if not backend_dir.exists():
        print("❌ 错误: 未找到backend目录")
        return False

    # 检查虚拟环境
    venv_dir = project_root / 'venv'
    if venv_dir.exists():
        python_path = venv_dir / 'bin' / 'python'
        if not python_path.exists():
            python_path = 'python'
    else:
        python_path = 'python'

    # 设置端口
    port = 5001

    # 检查端口可用性
    if not check_port_available(port):
        print(f"⚠️  端口 {port} 被占用，尝试停止现有服务...")
        stop_existing_service(port)
        time.sleep(2)

        if not check_port_available(port):
            print(f"❌ 端口 {port} 仍被占用，请手动停止相关服务")
            return False

    # 获取本机IP
    local_ip = get_local_ip()

    print("🚀 启动CoderWiki服务...")
    print(f"📍 本机IP地址: {local_ip}")
    print(f"🔌 服务端口: {port}")
    print("-" * 50)

    # 设置环境变量
    env = os.environ.copy()
    env['PORT'] = str(port)
    env['FLASK_DEBUG'] = 'True'
    env['FLASK_ENV'] = 'development'

    try:
        # 启动服务
        print("🎯 正在启动后端服务...")

        process = subprocess.Popen(
            [str(python_path), 'run.py'],
            cwd=str(backend_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # 等待服务启动
        print("⏳ 等待服务启动...")

        startup_timeout = 30
        start_time = time.time()

        while time.time() - start_time < startup_timeout:
            if process.poll() is not None:
                print("❌ 服务启动失败")
                if process.stdout:
                    output = process.stdout.read()
                    print(f"错误信息: {output}")
                return False

            # 检查端口是否开始监听
            if not check_port_available(port):
                break

            time.sleep(1)
        else:
            print("⏰ 服务启动超时")
            process.terminate()
            return False

        print("✅ 服务启动成功!")
        print("")
        print("🌐 访问信息:")
        print(f"   本机访问: http://localhost:{port}")
        print(f"   本机访问: http://127.0.0.1:{port}")
        print(f"   局域网访问: http://{local_ip}:{port}")
        print("")
        print("📋 主要页面:")
        print(f"   🏠 主页: http://{local_ip}:{port}/")
        print(f"   📊 仪表板: http://{local_ip}:{port}/dashboard")
        print(f"   🔐 登录: http://{local_ip}:{port}/api/auth/login")
        print("")
        print("🔑 默认账户:")
        print("   👑 管理员: admin / admin123")
        print("   👤 演示用户: demo / demo123")
        print("")
        print("💡 提示:")
        print("   - 按 Ctrl+C 停止服务")
        print("   - 确保防火墙允许端口访问")
        print("   - 其他设备需要连接到同一局域网")
        print("")

        # 保持服务运行
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 正在停止服务...")
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            print("✅ 服务已停止")

        return True

    except Exception as e:
        print(f"💥 启动服务时出错: {e}")
        return False


def main():
    """主函数"""
    print("🌟 CoderWiki 外部访问启动器")
    print("=" * 50)

    # 检查系统要求
    if sys.version_info < (3, 7):
        print("❌ 需要 Python 3.7 或更高版本")
        return False

    # 启动服务
    success = start_service()

    if success:
        print("\n🎉 服务已成功启动并可供外部访问!")
    else:
        print("\n❌ 服务启动失败")

    return success


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 再见!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 程序异常: {e}")
        sys.exit(1)

