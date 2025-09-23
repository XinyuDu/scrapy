#!/bin/zsh

# 设置端口和PID文件路径
PORT=8080
PID_FILE="server.pid"

function start_server() {
    # 检查PID文件是否存在，并且进程是否仍在运行
    if [ -f "$PID_FILE" ]; then
        if ps -p $(cat $PID_FILE) > /dev/null 2>&1; then
            echo "Web server is already running (PID: $(cat $PID_FILE))."
            return 1
        else
            # 进程不存在，删除旧的PID文件
            rm -f $PID_FILE
        fi
    fi

    # 启动Python HTTP服务器在后台，并将进程ID保存到文件
    cd /Users/duxinyu/PythonProjects/web2api
    nohup /Users/duxinyu/miniconda3/bin/python -u /Users/duxinyu/PythonProjects/web2api/server.py > /Users/duxinyu/PythonProjects/scrapy/toutiao/web2api.log 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > $PID_FILE
    echo "Python web server started on port $PORT (PID: $SERVER_PID)."
}

function stop_server() {
    if [ -f "$PID_FILE" ]; then
        # 发送TERM信号尝试优雅终止进程
        if kill -TERM $(cat $PID_FILE) 2>/dev/null; then
            echo "Web server (PID: $(cat $PID_FILE)) stopped."
        else
            echo "Could not stop web server. Process might not be running."
        fi
        # 删除PID文件
        rm -f $PID_FILE
    else
        echo "PID file not found. Is the server running?"
    fi
}

start_server
sleep 5
cd /Users/duxinyu/PythonProjects/scrapy/toutiao
/Users/duxinyu/miniconda3/bin/python -u /Users/duxinyu/PythonProjects/scrapy/toutiao/main.py > /Users/duxinyu/PythonProjects/scrapy/toutiao/scrape.log 2>&1
sleep 5
cd /Users/duxinyu/PythonProjects/web2api
stop_server
