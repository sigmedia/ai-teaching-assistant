from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.logger import logger
import fcntl
import os
import atexit
import traceback

class SchedulerManager:
    _instance = None
    _initialized = False
    _lock_file_handle = None

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
            atexit.register(self.cleanup)
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
            cls._lock_file_handle = open(instance.lock_file_path, 'w')
            logger.info("Lock file opened successfully")
            
            # Try to acquire an exclusive lock without blocking
            fcntl.flock(cls._lock_file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.info("Lock acquired successfully")
            
            # Write PID to file
            cls._lock_file_handle.seek(0)
            cls._lock_file_handle.write(str(os.getpid()))
            cls._lock_file_handle.truncate()
            cls._lock_file_handle.flush()
            
            logger.info(f"Scheduler lock acquired. PID: {os.getpid()}")
            return True
            
        except Exception as e:
            logger.error("=== Scheduler Start Error ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.error("Traceback:")
            logger.error(traceback.format_exc())
            
            if cls._lock_file_handle:
                logger.info("Cleaning up lock file handle...")
                cls._lock_file_handle.close()
                cls._lock_file_handle = None
            return False

    @classmethod
    def cleanup(cls):
        instance = cls()
        logger.info("Starting scheduler cleanup")
        try:
            if cls._lock_file_handle:
                fcntl.flock(cls._lock_file_handle.fileno(), fcntl.LOCK_UN)
                cls._lock_file_handle.close()
                cls._lock_file_handle = None
                
                if os.path.exists(instance.lock_file_path):
                    os.remove(instance.lock_file_path)
                    
                logger.info("Scheduler lock released and file cleaned up")
        except Exception as e:
            logger.error(f"Error during scheduler cleanup: {str(e)}")
            logger.error(traceback.format_exc())