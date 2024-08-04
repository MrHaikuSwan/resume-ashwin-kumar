# Git + Resume Overleaf Version Manager:

A Git-inspired tool to easily keep a GitHub repository and a Overleaf project in sync.

Feel free to use this for your own resume or adapt it for your own purposes!
I wrote this exclusively to manage my LaTeX resume versions with Git without
having to pay for Overleaf Premium's history feature or GitHub integration,
but it should be easy to adapt for any Overleaf project! I plan to release
this as a Python package with a CLI soon, so you can easily manage any Overleaf
project's history with Git.

Eventually, I'd like to import the package here and take all the code out of
this repository, but until I turn this code into a Python package, my resume
will live among the source code keeping it in sync with Overleaf and GitHub.

## Setup

1. Clone this repository.
2. Make sure you are logged into Overleaf on your default browser.
3. Run `python3 overleaf_ops.py configure` to select your desired project.
4. Run `python3 overleaf_ops.py pull` to pull your current project into this repository.

## Usage

- When you edit your Overleaf project locally, run `python3 overleaf_ops.py push` to push your changes to Overleaf.
- When you edit your project on Overleaf, run `python3 overleaf_ops.py pull` to pull your changes from Overleaf.
- Run `python3 overleaf_ops.py sync` to mirror your Overleaf files to `REMOTE_DIR`, your local repository's replica of remote.
  - NOTE: This operation does not change any of your local files in `CONTENT_DIR`.
- Run `python3 overleaf_ops.py check` to SAFELY check if your local files and Overleaf project are in sync.
  - NOTE: This operation will never change any files.
- If you ever want to change the project you are working on, run `python3 overleaf_ops.py configure` to select a new project.

## Configuration

- `PROJECT_NAME`: The Overleaf project name. `overleaf-configure` will set this automatically.
- `PROJECT_ID`: The Overleaf project ID. `overleaf-configure` will set this automatically.
- `CONTENT_DIR`: The directory where your local files and changes are stored. Change files here to edit your project locally.
  - `overleaf-configure` will set this up automatically if you don't already have a `content` directory.
- `REMOTE_DIR`: The directory where your remote content on Overleaf is replicated. This determines if your local files are up to date with your remote content.
  - `overleaf-configure` will set this up automatically if you don't already have a `remote` directory.
  - `overleaf-sync` synchronizes this directory with your remote content on Overleaf.
- `TEMP_ARCHIVE`: The name used for temporary downloaded ZIP archives of your Overleaf project. Don't worry about this, just make sure it's unique.
