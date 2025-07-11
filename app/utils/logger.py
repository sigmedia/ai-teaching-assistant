import logging
from logging.handlers import RotatingFileHandler
import structlog
import sys
from config import settings

# Set up logging handlers
def create_handlers():
    
    stream_handler = logging.StreamHandler(sys.stdout)
    return [stream_handler]

# Configure the structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True  # Performance optimization
)

handlers = create_handlers()
logging.basicConfig(
    handlers=handlers,
    format="%(message)s",
    level=logging.INFO
)

logger = structlog.get_logger()