import yaml
import os
from pathlib import Path
from typing import Dict, Any, List
from utils.logger import get_logger

class Config:
    """Manages configuration loading."""
    
    def __init__(self, config_dir: Path, environment: str):
        self.config_dir = config_dir
        self.environment = environment
        self.logger = get_logger('config')
    
    def load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load a YAML configuration file from the given path."""
        self.logger.debug(f"📄 Loading YAML file: {file_path}")
        
        if file_path.exists():
            self.logger.info(f"✅ Found config file: {file_path}")
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
                return config
        return {}

    def load_managed_services(self) -> List[Dict[str, str]]:
        """Load the list of managed services from the manifest file."""
        manifest_path = self.config_dir / 'service-config-manager' / 'managed-services.yaml'
        
        if not manifest_path.exists():
            self.logger.warning(f"⚠️ Managed services manifest not found at {manifest_path}")
            return []
            
        self.logger.info(f"📋 Loading managed services manifest: {manifest_path}")
        with open(manifest_path, 'r') as f:
            services = yaml.safe_load(f)
            return services or []
    
    def load_service_config(self, service_config_dir: str, service_type: str) -> Any:
        """Load configuration for a specific service from its directory."""
        config_path = self.config_dir / service_config_dir
        
        if not config_path.exists():
            self.logger.error(f"❌ Config directory not found: {config_path}")
            return None

        file_path = None
        if service_type == 'couchbase':
            file_path = config_path / 'couchbase.yaml'
        elif service_type == 'redpanda':
            file_path = config_path / 'redpanda.yaml'
        elif service_type == 'postgres':
            # Check for SQL file
            file_path = config_path / 'postgres.sql'
            if file_path.exists():
                self.logger.info(f"📄 Found SQL script for {service_type}: {file_path}")
                return str(file_path)
            # Fallback or check for other types if needed
        
        if file_path and file_path.exists():
            self.logger.info(f"🎯 Loading service configuration: {file_path}")
            return self.load_yaml(file_path)
            
        self.logger.warning(f"⚠️ No configuration file found for {service_type} in {config_path}")
        return None

    def merge_settings(self, global_defaults: Dict[str, Any], 
                      item_defaults: Dict[str, Any], 
                      env_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Merge settings with precedence: env_settings > item_defaults > global_defaults."""
        result = {}
        
        # Start with global defaults
        if global_defaults:
            result.update(global_defaults)
        
        # Apply item defaults
        if item_defaults:
            result.update(item_defaults)
        
        # Apply environment-specific settings
        if env_settings:
            result.update(env_settings)
        
        return result