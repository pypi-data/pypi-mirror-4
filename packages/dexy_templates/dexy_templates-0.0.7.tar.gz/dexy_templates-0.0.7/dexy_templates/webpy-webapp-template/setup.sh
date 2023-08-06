### @export "info"
tree -n

### @export "load-sql"
sqlite3 todo.sqlite3 < schema.sql

### @export "start-server"
nohup python todo.py &
echo $! > pidfile
sleep 2
cat nohup.out
curl -I http://localhost:8080
