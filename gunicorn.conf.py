# Gunicorn configuration file
import multiprocessing

# Worker processes
worker_class = "uvicorn.workers.UvicornWorker"
workers = (multiprocessing.cpu_count() * 2) + 1

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048  # Maximum number of pending connection - a common default that works well for many web applications

# Timeouts
timeout = 180  # seconds
graceful_timeout = 180
keepalive = 5

# Restart workers
max_requests = 1000
max_requests_jitter = 50

# Security
# Prevent server information leakage
server_tokens = False