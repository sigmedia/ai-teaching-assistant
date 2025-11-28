from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.logger import logger
from filelock import FileLock, Timeout
import os
import atexit
import traceback

class SchedulerManager:
    _instance = None
    _initialized = False
    _lock = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("Creating new SchedulerManager instance")
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not SchedulerManager._initialized:
            logger.info("Initializing SchedulerManager")
            self.scheduler = AsyncIOScheduler()
            SchedulerManager._initialized = True
            logger.info("SchedulerManager initialized successfully")

    @property
    def lock_file_path(self):
        # Get the lock file path, ensuring the directory exists
        logger.info("Finding appropriate lock file path")
        # Try common temp directories in order of preference
        temp_dirs = [
            os.getenv('TEMP'),  # Environment variable if set
            '/tmp',            # Unix standard temp directory
            os.path.expanduser('~/tmp'),  # User's home directory
            os.getcwd()        # Current working directory as fallback
        ]
        
        # Use the first available directory
        for temp_dir in temp_dirs:
            if temp_dir and os.path.exists(temp_dir):
                path = os.path.join(temp_dir, 'scheduler.lock')
                logger.info(f"Using lock file path: {path}")
                return path
            
        # If none exist, create a directory in current working directory
        tmp_dir = os.path.join(os.getcwd(), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        path = os.path.join(tmp_dir, 'scheduler.lock')
        logger.info(f"Created new directory for lock file: {path}")
        return path

    @classmethod
    def get_scheduler(cls):
        logger.info("Getting scheduler instance")
        scheduler = cls().scheduler
        logger.info(f"Current scheduler running status: {scheduler.running}")
        return scheduler

    @classmethod
    def should_start_scheduler(cls):
        instance = cls()
        logger.info("=== Starting Scheduler Check ===")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Attempting to start scheduler using lock file: {instance.lock_file_path}")
        
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(instance.lock_file_path), exist_ok=True)
            logger.info(f"Ensured directory exists: {os.path.dirname(instance.lock_file_path)}")
            
            # Try to open and lock the file
            cls._lock = FileLock(instance.lock_file_path, timeout=0)
            cls._lock.acquire()
            logger.info("Lock acquired successfully")
            
            # Write PID to a separate file (FileLock manages its own .lock file)
            pid_file = instance.lock_file_path + ".pid"
            with open(pid_file, 'w') as f:
                f.write(str(os.getpid()))
            
            logger.info(f"Scheduler lock acquired. PID: {os.getpid()}")
            return True
            
        except Timeout:
            logger.info("Could not acquire lock - another process holds it")
            cls._lock = None
            return False
        except Exception as e:
            logger.error("=== Scheduler Start Error ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.error("Traceback:")
            logger.error(traceback.format_exc())
            cls._lock = None
            return False

    @classmethod
    def cleanup(cls):
        instance = cls()
        logger.info("Starting scheduler cleanup")
        try:
            if cls._lock:
                cls._lock.release()
                cls._lock = None
                
                # Clean up lock file
                if os.path.exists(instance.lock_file_path):
                    os.remove(instance.lock_file_path)
                
                # Clean up PID file
                pid_file = instance.lock_file_path + ".pid"
                if os.path.exists(pid_file):
                    os.remove(pid_file)
                    
                logger.info("Scheduler lock released and file cleaned up")
        except Exception as e:
            logger.error(f"Error during scheduler cleanup: {str(e)}")
            logger.error(traceback.format_exc())