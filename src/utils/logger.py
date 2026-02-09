"""
Configuration centralisée des logs.
"""

from loguru import logger
import sys
from pathlib import Path


def setup_logging(level: str = "INFO", log_file: str = None):
    """
    Configure le système de logging.
    
    Args:
        level: Niveau de log ("DEBUG", "INFO", "WARNING", "ERROR")
        log_file: Chemin vers le fichier de log (None pour stdout uniquement)
    """
    # Supprimer le handler par défaut
    logger.remove()
    
    # Ajouter le handler console
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # Ajouter le handler fichier si spécifié
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
            level=level,
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )
