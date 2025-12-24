"""Initialize system directories and environment."""

import sys
from pathlib import Path
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import settings
from src.utils import ensure_directories


def setup_logging():
    """Configure logging system."""
    # Remove default handler
    logger.remove()
    
    # Add console handler with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
    )
    
    # Add file handler
    log_file = Path(settings.log_dir) / "system_{time}.log"
    logger.add(
        str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="DEBUG",
        rotation="100 MB",
        retention="7 days",
        compression="zip",
    )
    
    logger.info("Logging system initialized")
    logger.info("Log file: {}", log_file)


def check_environment():
    """Check if environment is properly configured."""
    logger.info("Checking environment...")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning(".env file not found, using .env.example as template")
        logger.warning("Please copy .env.example to .env and configure your API keys")
        return False
    
    # Check API key
    if not settings.openai_api_key or settings.openai_api_key == "your-api-key-here":
        logger.error("OpenAI API key not configured in .env file")
        return False
    
    logger.success("Environment check passed")
    return True


def init_system():
    """Initialize the entire system."""
    logger.info("=" * 60)
    logger.info("Initializing Data Synthesis System")
    logger.info("=" * 60)
    
    # Setup logging
    setup_logging()
    
    # Ensure directories
    logger.info("Creating required directories...")
    ensure_directories()
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed. Please configure .env file.")
        sys.exit(1)
    
    logger.success("System initialization complete")
    logger.info("=" * 60)


if __name__ == "__main__":
    init_system()
