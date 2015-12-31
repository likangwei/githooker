ps aux|grep server.py|awk '{print $2}'|xargs kill -9
(python server.py > /dev/null 2>&1)&
