from pathlib import Path

from utils import log

logger = log.get_logger(__name__)


def get_app_version() -> str:
    """Read version from pyproject.toml."""
    try:
        current_path = Path(__file__).resolve()
        for parent in [current_path] + list(current_path.parents):
            pyproject_path = parent / "pyproject.toml"
            if pyproject_path.exists():
                content = pyproject_path.read_text()
                for line in content.split('\n'):
                    if line.strip().startswith('version = '):
                        return line.split('=')[1].strip().strip('"\'')
                break
        return "unknown"
    except Exception as e:
        logger.warning(f"Failed to read version from pyproject.toml: {e}")
        return "unknown"
