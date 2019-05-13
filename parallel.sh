parallel ::: echo "1" echo "2" &
PID=$!
kill -TERM $PID
kill -TERM $PID