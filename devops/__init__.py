"""
DevOps package for Belgrano Ahorro
This package provides the main application factory and utilities.
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('devops')

# Export create_app
try:
    from .app import create_app
    __all__ = ['create_app']
except ImportError as e:
    logger.warning(f"⚠️ Could not import create_app in __init__: {e}")
