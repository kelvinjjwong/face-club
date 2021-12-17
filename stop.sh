ps -ef | grep -e '/bin/flask run$'
pid=`ps -ef | grep -e '/bin/flask run$' | awk -F' ' '{print $2}'`
if [[ "$pid" != "" ]]; then
  kill -15 $pid
  echo "killed pid $pid"
else
  echo "it's not running"
fi