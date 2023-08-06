### @export "kill"
kill -TERM `cat pidfile`

### @export "check-killed"
curl -I http://localhost:8080 || echo "killed"
