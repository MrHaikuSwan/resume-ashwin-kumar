import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Set directory pathing variables
ROOT_DIR = Path(__file__).parent.parent
CONFIG_PATH = ROOT_DIR / "config.json"

# Set global config variables from `state.json`
with open(CONFIG_PATH) as config_file:
    config = json.load(config_file)
    logger.debug(f"config:\n{json.dumps(config, indent=2)}")
    # Project Specifications
    PROJECT_NAME = config["project_name"]
    PROJECT_ID = config["project_id"]
    # Path Specifications
    CONTENT_DIR = ROOT_DIR / Path(config["content_dir"])
    REMOTE_DIR = ROOT_DIR / Path(config["remote_dir"])
    TEMP_ARCHIVE = ROOT_DIR / Path(config["temp_archive"])
