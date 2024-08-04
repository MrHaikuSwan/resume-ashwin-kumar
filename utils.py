import json
from typing import NamedTuple

import pyoverleaf
from tabulate import tabulate

from config import REMOTE_DIR, CONTENT_DIR


class OverleafLogin(NamedTuple):
    api: pyoverleaf.Api
    project: pyoverleaf.Project
    io: pyoverleaf.ProjectIO


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
