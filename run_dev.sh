concurrently --restart-tries 1000 --restart-after 500 --names "docker,web_server,worker,front_end" "docker-compose -f docker-compose.dev.yml up" "cd server && python3 web_server.py" "cd server && celery -A worker.tasks worker --pool=solo" "cd client && npm run serve"