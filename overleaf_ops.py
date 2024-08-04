import pyoverleaf
from pathlib import Path
import json
import sys
import logging

logger = logging.getLogger(__name__)


# Set global config variables from `state.json`
with open("config.json") as config_file:
    config = json.load(config_file)
    PROJECT_NAME = Path(config["project_name"])
    CONTENT_DIR = Path(config["content_dir"])
    REMOTE_DIR = Path(config["remote_dir"])
    TEMP_DIR = Path(config["temp_dir"])
    logging.debug(f"config: {json.dumps(config, indent=2)}")


def overleaf_push(io):
    pass


def overleaf_pull(io):
    pass


def overleaf_sync(io):
    pass


def main():
    logging.basicConfig(level=logging.INFO)

    # Get cmdline args
    if len(sys.argv) != 2 or sys.argv[1] not in ["push", "pull", "sync"]:
        raise ValueError(
            "Usage: python3 overleaf_ops.py <command> where <command> is one of: push, pull, sync"
        )
    overleaf_ops = {"push": overleaf_push, "pull": overleaf_pull, "sync": overleaf_sync}
    command = sys.argv[1]
    overleaf_op = overleaf_ops[command]

    # Validate folder setup
    if not REMOTE_DIR.exists():
        raise FileNotFoundError(
            f"{REMOTE_DIR} does not exist: Please run `overleaf-sync` first"
        )
    if TEMP_DIR.exists():
        raise FileExistsError(f"{TEMP_DIR} already exists: Please remove it first")
    if command in ["push", "pull"] and not CONTENT_DIR.exists():
        raise FileNotFoundError(
            f"{CONTENT_DIR} does not exist: Please create a content directory first"
        )

    # Login to Overleaf
    api = pyoverleaf.Api()
    api.login_from_browser()
    projects = api.get_projects()
    for project in projects:
        if project.name == PROJECT_NAME:
            break
    io = pyoverleaf.ProjectIO(api, project.id)
    overleaf_op(io)


if __name__ == "__main__":
    main()
