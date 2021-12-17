source ./query.sh
pid=`ps -ef | grep '/bin/flask run' | grep -v grep | awk -F' ' '{print $2}'`
if [[ "$pid" != "" ]]; then
  kill -15 $pid
  echo "killed pid $pid"
else
  echo "it's not running"
fi