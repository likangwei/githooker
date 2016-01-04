netstat -anp 2>/dev/null|grep "0.0.0.0:9003"|awk '{print $7}'|awk -F "/" '{print $1}'|xargs kill -9
nohup python hookserver.py &
