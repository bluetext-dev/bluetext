import yaml
from pathlib import Path
from typing import Dict, Any
from utils.logger import get_logger

class Config:
    """Manages configuration loading."""
    
    def __init__(self, config_dir: Path, environment: str):
        self.config_dir = config_dir
        self.environment = environment
        self._targets = None
        self.logger = get_logger('config')
    
    def load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load a YAML configuration file from the given path."""
        self.logger.debug(f"📄 Loading YAML file: {file_path}")
        
        # Check if the exact path exists first
        if file_path.exists():
            self.logger.info(f"✅ Found config file: {file_path}")
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
                return config
        return {}
    
    def get_targets(self) -> Dict[str, Path]:
        """Get available target config file paths by detecting existing files in config directory."""
        if self._targets is None:
            self.logger.info(f"🔍 Scanning for config files in {self.config_dir}")
            self._targets = {}
            
            # Check for couchbase config
            couchbase_opts = ['couchbase.yaml', 'couchbase.yml']
            for opt in couchbase_opts:
                path = self.config_dir / opt
                if path.exists():
                    self._targets['couchbase'] = path
                    break
            
            # Check for redpanda config
            redpanda_opts = ['redpanda.yaml', 'redpanda.yml']
            for opt in redpanda_opts:
                path = self.config_dir / opt
                if path.exists():
                    self._targets['redpanda'] = path
                    break

            # Check for postgres config
            postgres_opts = ['postgres.sql']
            for opt in postgres_opts:
                path = self.config_dir / opt
                if path.exists():
                    self._targets['postgres'] = path
                    break
        
        return self._targets
    
    def load_target_config(self, target_id: str) -> Any:
        """Load configuration for a specific service."""
        targets = self.get_targets()
        
        if target_id not in targets:
            self.logger.error(f"❌ No configured path found for target '{target_id}'")
            return None
        
        config_file_path = targets[target_id]
        
        if config_file_path.suffix == '.sql':
             self.logger.info(f"📄 Found SQL script for {target_id}: {config_file_path}")
             return str(config_file_path)

        self.logger.info(f"🎯 Loading target configuration: {target_id}")
        return self.load_yaml(config_file_path)

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
