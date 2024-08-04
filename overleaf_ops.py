from filecmp import dircmp
from pathlib import Path
from typing import NamedTuple
import json
import logging
import shutil
import sys
import zipfile

import pyoverleaf

logger = logging.getLogger(__name__)


class OverleafLogin(NamedTuple):
    api: pyoverleaf.Api
    project: pyoverleaf.Project
    io: pyoverleaf.ProjectIO


# Set global config variables from `state.json`
with open("config.json") as config_file:
    config = json.load(config_file)
    PROJECT_NAME = Path(config["project_name"])
    CONTENT_DIR = Path(config["content_dir"])
    REMOTE_DIR = Path(config["remote_dir"])
    TEMP_ARCHIVE = Path(config["temp_archive"])
    logging.debug(f"config:\n{json.dumps(config, indent=2)}")


def overleaf_login(project_name):
    """Logs into an Overleaf project and returns an OverleafLogin object."""
    api = pyoverleaf.Api()
    api.login_from_browser()
    projects = api.get_projects()
    for project in projects:
        if project.name == project_name:
            break
    io = pyoverleaf.ProjectIO(api, project.id)
    return OverleafLogin(api, project, io)


def overleaf_push(login: OverleafLogin):
    logging.debug("Pushing project...")
    assert not TEMP_ARCHIVE.exists()
    api, project, io = login
    api.download_project(project.id, TEMP_ARCHIVE)
    pass


def overleaf_pull(login: OverleafLogin):
    assert not TEMP_ARCHIVE.exists()
    assert REMOTE_DIR.exists() and REMOTE_DIR.is_dir()
    assert CONTENT_DIR.exists() and CONTENT_DIR.is_dir()

    temp_dir = Path(TEMP_ARCHIVE.stem)
    assert not temp_dir.exists()

    logging.debug("Pulling project...")

    # Download project, unzip to remote directory
    api, project, _ = login
    api.download_project(project.id, TEMP_ARCHIVE)
    temp_dir.mkdir()
    with zipfile.ZipFile(TEMP_ARCHIVE, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Compare remote/ and pulled content, notify user (diffs are expected)
    dcmp = dircmp(REMOTE_DIR, temp_dir)
    if dcmp.diff_files or dcmp.left_only or dcmp.right_only or dcmp.funny_files:
        print("Differences found between remote and pulled content:\n---")
        dcmp.report()
        print("---")

    # Safely overwrite REMOTE_DIR and CONTENT_DIR with pulled content
    with zipfile.ZipFile(TEMP_ARCHIVE, "r") as zip_ref:
        temp_remote_dir = Path(f"temp_{REMOTE_DIR}")
        temp_content_dir = Path(f"temp_{CONTENT_DIR}")
        shutil.move(REMOTE_DIR, temp_remote_dir, copy_function=shutil.copytree)
        shutil.move(CONTENT_DIR, temp_content_dir, copy_function=shutil.copytree)
        REMOTE_DIR.mkdir()
        CONTENT_DIR.mkdir()
        zip_ref.extractall(REMOTE_DIR)
        zip_ref.extractall(CONTENT_DIR)
        shutil.rmtree(temp_remote_dir)
        shutil.rmtree(temp_content_dir)

    logging.debug("Finished pulling project.")


def overleaf_sync(login: OverleafLogin):
    logging.debug("Syncing project...")

    # Download project, unzip to remote directory (create if DNE)
    api, project, _ = login
    api.download_project(project.id, TEMP_ARCHIVE)
    REMOTE_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(TEMP_ARCHIVE, "r") as zip_ref:
        zip_ref.extractall(REMOTE_DIR)

    # Create empty content directory if DNE (convenience)
    if not CONTENT_DIR.exists():
        logging.INFO(f"No content directory found -- creating {CONTENT_DIR}...")
        CONTENT_DIR.mkdir(parents=True)
        logging.INFO(
            f"Created empty {CONTENT_DIR} -- run `overleaf-pull` to populate the content directory with the current remote content"
        )


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
    if TEMP_ARCHIVE.exists():
        raise FileExistsError(
            f"{TEMP_ARCHIVE} already exists: Please rename or delete this leftover archive"
        )
    if command in ["push", "pull"] and not REMOTE_DIR.exists():
        raise FileNotFoundError(
            f"{REMOTE_DIR} does not exist: Please run `overleaf-sync` before pushing or pulling"
        )
    if command == "push" and not CONTENT_DIR.exists():
        raise FileNotFoundError(
            f"{CONTENT_DIR} does not exist: Please create a content directory before pushing"
        )

    # Execute Overleaf operation
    login = overleaf_login(PROJECT_NAME)
    overleaf_op(login)


if __name__ == "__main__":
    main()
