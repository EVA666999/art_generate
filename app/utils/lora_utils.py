"""
Utilities for working with LORA configurations.
"""
import json
import os
from typing import Dict, Any, Optional

import logging

logger = logging.getLogger(__name__)


def load_lora_config(config_path: str = "app/config/lora_config.json") -> Optional[Dict[str, Any]]:
    """
    Loads LORA configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dict with LORA configuration or None if error
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info("LORA configuration loaded")
            return config
        else:
            logger.warning("LORA configuration file not found")
            return None
    except Exception as e:
        logger.error(f"Error loading LORA configuration: {str(e)}")
        return None


class LoraManager:
    """Manager for LORA configurations and operations."""
    
    def __init__(self):
        self.config = load_lora_config()
    
    def get_lora_config(self) -> Optional[Dict[str, Any]]:
        """Get LORA configuration."""
        return self.config
    
    def is_enabled(self) -> bool:
        """Check if LORA is enabled."""
        return self.config is not None and self.config.get("enabled", False)


# Create global instance
lora_manager = LoraManager() 