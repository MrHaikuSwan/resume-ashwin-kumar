from filecmp import dircmp
from pathlib import Path
from typing import NamedTuple
import json
import logging
import shutil
import sys
import zipfile

import pyoverleaf
from tabulate import tabulate

logger = logging.getLogger(__name__)


class OverleafLogin(NamedTuple):
    api: pyoverleaf.Api
    project: pyoverleaf.Project
    io: pyoverleaf.ProjectIO


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


def overleaf_configure():
    api = pyoverleaf.Api()
    api.login_from_browser()
    projects = [
        p for p in api.get_projects() if p.access_level == "owner"
    ]  # for safety, only expose owned projects

    # Display all project names and IDs
    print("Owned Projects:")
    table = [[i, p.name, p.id] for i, p in enumerate(projects, start=1)]
    print(tabulate(table, headers=["Index", "Name", "ID"]))
    print()

    # Get user project selection to configure
    config_index = input("Enter the index of the project to use: ")
    while config_index not in [str(i) for i in range(1, len(projects) + 1)]:
        print("Invalid index. Please try again.")
        config_index = input("Enter the index of the project to use: ")

    # Configure selected project
    config_index = int(config_index)
    config_project = projects[config_index - 1]
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    with open("config.json", "w") as config_file:
        config["project_name"] = config_project.name
        config["project_id"] = config_project.id
        json.dump(config, config_file, indent=2)
    print(f"Project {config_project.name} ({config_project.id}) configured.")

    # Set up directories
    if not REMOTE_DIR.exists():
        REMOTE_DIR.mkdir(parents=True)
    if not CONTENT_DIR.exists():
        CONTENT_DIR.mkdir(parents=True)
    print(f"Confirmed existence of {REMOTE_DIR} and {CONTENT_DIR} directories.")


def overleaf_login(project_name, project_id):
    """Logs into an Overleaf project and returns an OverleafLogin object."""
    api = pyoverleaf.Api()
    api.login_from_browser()
    projects = [
        p for p in api.get_projects() if p.access_level == "owner"
    ]  # for safety, only expose owned projects

    # Attempt to find specific project
    matching_projects = [
        p for p in projects if p.name == project_name and p.id == project_id
    ]
    if len(matching_projects) != 1:
        raise ValueError(f"Project {project_name} not found: {matching_projects}")
    project = matching_projects[0]
    assert project.name == project_name, f"Project {project_name} not found"
    io = pyoverleaf.ProjectIO(api, project.id)
    return OverleafLogin(api, project, io)


def overleaf_push(login: OverleafLogin):
    api, project, io = login
    assert project.access_level == "owner", "Project must be owned"
    assert project.id == PROJECT_ID, "Project ID does not match"
    assert project.name == PROJECT_NAME, "Project name does not match"

    assert not TEMP_ARCHIVE.exists()
    assert REMOTE_DIR.exists() and REMOTE_DIR.is_dir()
    assert CONTENT_DIR.exists() and CONTENT_DIR.is_dir()

    temp_dir = Path(TEMP_ARCHIVE.stem)
    assert not temp_dir.exists()

    logger.info("Pushing project...")

    # Download project, unzip to temporary directory
    api.download_project(project.id, TEMP_ARCHIVE)
    temp_dir.mkdir()
    with zipfile.ZipFile(TEMP_ARCHIVE, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
    TEMP_ARCHIVE.unlink()

    # Verify remote/ and pulled content match -- avoid overwriting new remote Overleaf changes
    dcmp = dircmp(REMOTE_DIR, temp_dir)
    if dcmp.diff_files or dcmp.left_only or dcmp.right_only or dcmp.funny_files:
        print(f"Differences found between {REMOTE_DIR} and pulled content:\n---")
        dcmp.report()
        print("---")
        raise ValueError("Remote and pulled content differ, local state is out of sync")
    shutil.rmtree(temp_dir)

    # Overwrite remote Overleaf content with local content/ (UNSAFE -- BE CAUTIOUS)

    ## UNSAFE
    for fp in io.listdir("."):
        io.remove(fp)
    ## UNSAFE

    ## Create all remote files from content/
    content_paths = [Path(*p.parts[1:]) for p in CONTENT_DIR.rglob("*")]
    content_dir_paths = [p for p in content_paths if p.is_dir()]
    content_blob_paths = [p for p in content_paths if not p.is_dir()]
    for path in content_dir_paths:
        io.mkdir(path, exist_ok=True, parents=True)
    for path in content_blob_paths:
        with io.open(path, "wb") as outfile:
            outfile.write(path.read_bytes())

    # Re-synchronize remote/ with remote Overleaf content
    shutil.copytree(CONTENT_DIR, REMOTE_DIR, dirs_exist_ok=True)

    assert not TEMP_ARCHIVE.exists()
    assert not temp_dir.exists()
    logger.info("Finished pushing project.")


def overleaf_pull(login: OverleafLogin):
    api, project, _ = login
    assert project.access_level == "owner", "Project must be owned"
    assert project.id == PROJECT_ID, "Project ID does not match"
    assert project.name == PROJECT_NAME, "Project name does not match"

    assert not TEMP_ARCHIVE.exists()
    assert REMOTE_DIR.exists() and REMOTE_DIR.is_dir()
    assert CONTENT_DIR.exists() and CONTENT_DIR.is_dir()

    temp_dir = Path(TEMP_ARCHIVE.stem)
    assert not temp_dir.exists()

    logger.info("Pulling project...")

    # Verify remote/ and content/ match -- avoid overwriting new local content changes
    dcmp = dircmp(REMOTE_DIR, CONTENT_DIR)
    if dcmp.diff_files or dcmp.left_only or dcmp.right_only or dcmp.funny_files:
        print(f"Differences found between {REMOTE_DIR} and {CONTENT_DIR}:\n---")
        dcmp.report()
        print("---")
        raise ValueError("Remote and content differ, local state is out of sync")

    # Download project, unzip to temporary directory
    api.download_project(project.id, TEMP_ARCHIVE)
    temp_dir.mkdir()
    with zipfile.ZipFile(TEMP_ARCHIVE, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
    shutil.rmtree(temp_dir)

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
    TEMP_ARCHIVE.unlink()

    assert not TEMP_ARCHIVE.exists()
    assert not temp_dir.exists()
    logger.info("Finished pulling project.")


def overleaf_sync(login: OverleafLogin):
    api, project, _ = login
    assert project.access_level == "owner", "Project must be owned"
    assert project.id == PROJECT_ID, "Project ID does not match"
    assert project.name == PROJECT_NAME, "Project name does not match"

    logger.info("Syncing project...")

    # Download project, unzip to remote directory (create if DNE)
    api.download_project(project.id, TEMP_ARCHIVE)
    shutil.rmtree(REMOTE_DIR)
    REMOTE_DIR.mkdir(parents=True)
    with zipfile.ZipFile(TEMP_ARCHIVE, "r") as zip_ref:
        zip_ref.extractall(REMOTE_DIR)
    TEMP_ARCHIVE.unlink()

    # Create empty content directory if DNE (convenience)
    if not CONTENT_DIR.exists():
        logger.info(f"No content directory found -- creating {CONTENT_DIR}...")
        CONTENT_DIR.mkdir(parents=True)
        logger.info(
            f"Created empty {CONTENT_DIR} -- run `overleaf-pull` to populate the content directory with the current remote content"
        )
    else:
        # Compare remote/ and content/, notify user (diffs are expected)
        dcmp = dircmp(REMOTE_DIR, CONTENT_DIR)
        if dcmp.diff_files or dcmp.left_only or dcmp.right_only or dcmp.funny_files:
            print(f"Differences found between {REMOTE_DIR} and {CONTENT_DIR}:\n---")
            dcmp.report()
            print("---")

    assert not TEMP_ARCHIVE.exists()
    logger.info("Finished syncing project.")


def overleaf_check(login: OverleafLogin):
    api, project, _ = login
    assert project.access_level == "owner", "Project must be owned"
    assert project.id == PROJECT_ID, "Project ID does not match"
    assert project.name == PROJECT_NAME, "Project name does not match"

    logger.info("Checking for synchronicity...")

    temp_dir = Path(TEMP_ARCHIVE.stem)
    assert not temp_dir.exists()

    # Download project, unzip to temporary directory
    api.download_project(project.id, TEMP_ARCHIVE)
    temp_dir.mkdir()
    with zipfile.ZipFile(TEMP_ARCHIVE, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
    TEMP_ARCHIVE.unlink()

    # Compare remote/ and pulled content, notify user (diffs are expected)
    dcmp = dircmp(REMOTE_DIR, temp_dir)
    if dcmp.diff_files or dcmp.left_only or dcmp.right_only or dcmp.funny_files:
        print(f"Differences found between {REMOTE_DIR} and pulled content:\n---")
        dcmp.report()
        print("---")
    shutil.rmtree(temp_dir)

    assert not TEMP_ARCHIVE.exists()
    logger.info("Synchronization check complete.")


def main():
    logging.basicConfig(level=logging.INFO)

    # Get cmdline args
    allowed_ops = ["push", "pull", "sync", "check", "configure"]
    if len(sys.argv) != 2 or sys.argv[1] not in allowed_ops:
        print(f"\nUsage: python3 overleaf_ops.py [{'|'.join(allowed_ops)}]")
        return
    if sys.argv[1] == "configure":
        overleaf_configure()
        return

    overleaf_ops = {
        "push": overleaf_push,
        "pull": overleaf_pull,
        "sync": overleaf_sync,
        "check": overleaf_check,
    }
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
    login = overleaf_login(PROJECT_NAME, PROJECT_ID)
    overleaf_op(login)


if __name__ == "__main__":
    main()
