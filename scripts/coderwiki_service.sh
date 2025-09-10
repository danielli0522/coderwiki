#!/bin/bash

set -euo pipefail

ACTION=${1:-start}
PORT=${2:-5001}

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOG_DIR/coderwiki.pid"

ensure_env() {
  if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "❌ backend/venv 不存在，请先创建虚拟环境:"
    echo "   cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r ../requirements.txt"
    exit 1
  fi
  mkdir -p "$LOG_DIR"
}

running_pid() {
  if [ -f "$PID_FILE" ]; then
    local pid
    pid=$(cat "$PID_FILE" || true)
    if [ -n "$pid" ] && ps -p "$pid" > /dev/null 2>&1; then
      echo "$pid"
      return 0
    fi
  fi
  # fallback by port
  lsof -ti :$PORT | head -n1 || true
}

start() {
  ensure_env
  local pid
  pid=$(running_pid)
  if [ -n "$pid" ]; then
    echo "✅ 已在端口 $PORT 运行 (PID: $pid)"
    exit 0
  fi

  echo "🚀 启动 CoderWiki (production, port=$PORT) ..."
  (
    source "$BACKEND_DIR/venv/bin/activate"
    export PORT=$PORT
    export FLASK_ENV=production
    export FLASK_DEBUG=False
    cd "$PROJECT_ROOT"
    nohup python run.py >> "$LOG_DIR/server.log" 2>&1 & echo $! > "$PID_FILE"
  )

  sleep 2
  pid=$(running_pid)
  if [ -n "$pid" ]; then
    echo "✅ 启动成功 (PID: $pid)"
    echo "🔗 http://localhost:$PORT"
  else
    echo "❌ 启动失败，查看日志: $LOG_DIR/server.log"
    exit 1
  fi
}

stop() {
  local pid
  pid=$(running_pid)
  if [ -z "$pid" ]; then
    echo "ℹ️ 未发现运行中的进程"
    rm -f "$PID_FILE"
    exit 0
  fi
  echo "🛑 停止进程 $pid ..."
  kill "$pid" 2>/dev/null || true
  sleep 1
  if ps -p "$pid" > /dev/null 2>&1; then
    echo "⚠️ 正在强制终止..."
    kill -9 "$pid" 2>/dev/null || true
  fi
  rm -f "$PID_FILE"
  echo "✅ 已停止"
}

status() {
  local pid
  pid=$(running_pid)
  if [ -n "$pid" ]; then
    echo "✅ 运行中 (PID: $pid, 端口: $PORT)"
    if curl -s "http://localhost:$PORT/api/system/health" >/dev/null; then
      echo "🌐 本地健康检查: OK"
    else
      echo "🌐 本地健康检查: FAIL"
    fi
  else
    echo "❌ 未运行"
  fi
}

case "$ACTION" in
  start) start ;;
  stop) stop ;;
  restart) stop || true; start ;;
  status) status ;;
  *) echo "用法: $0 {start|stop|restart|status} [port]"; exit 1 ;;
esac




