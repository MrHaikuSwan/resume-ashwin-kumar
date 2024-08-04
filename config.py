import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Set global config variables from `state.json`
with open("config.json") as config_file:
    config = json.load(config_file)
    logger.debug(f"config:\n{json.dumps(config, indent=2)}")
    # Project Specifications
    PROJECT_NAME = config["project_name"]
    PROJECT_ID = config["project_id"]
    # Path Specifications
    CONTENT_DIR = Path(config["content_dir"])
    REMOTE_DIR = Path(config["remote_dir"])
    TEMP_ARCHIVE = Path(config["temp_archive"])
