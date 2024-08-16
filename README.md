# Git + Resume Overleaf Version Manager:

A Git-inspired tool to easily keep a GitHub repository and a Overleaf project in sync.

Feel free to use this for your own resume or adapt it for your own purposes! I wrote this exclusively to manage my LaTeX resume versions with Git without having to pay for Overleaf Premium's history feature or GitHub integration, but it should be easy to adapt for any Overleaf project! I plan to release this as a Python package with a CLI soon, so you can easily manage any Overleaf project's history with Git.

Eventually, I'd like to import the package here and take all the code out of this repository, but until I turn this code into a Python package, my resume will live among the source code keeping it in sync with Overleaf.

## Resume

If you legitimately just came here to find my resume, I'm 1) really impressed by your dedication and 2) [happy to share it](https://ashwinak-resume.tiiny.site/)! While you're at it, feel free to check out my [LinkedIn](https://www.linkedin.com/in/ashwinak/) and [website](https://ashwinak.com) as well (currently under construction)! Additionally, if you're technical and have ideas on how I can improve this, I'm all ears.

## Setup

1. Clone this repository.
2. Activate the virtual environment if it is not already activated with `source env/bin/activate`.
3. Make sure you are logged into Overleaf on your default browser.
4. Run `bin/configure` to select your desired project.
   - NOTE: The first time you run this, you may be asked to grant Python permissions a few times.
5. Run `bin/pull` to pull your current project into your local repo.

## Usage

- When you edit your Overleaf project locally, run `bin/push` to push your changes to Overleaf.
- When you edit your project on Overleaf, run `bin/pull` to pull your changes from Overleaf.
- Run `bin/sync` to mirror your Overleaf files to `REMOTE_DIR`, your local repository's replica of remote.
  - NOTE: This operation does not change any of your local files in `CONTENT_DIR`.
- Run `bin/check` to SAFELY check if your local files and Overleaf project are in sync.
  - NOTE: This operation will never change any files.
- If you ever want to change the project you are working on, run `bin/configure` to select a new project.

## Configuration

- `PROJECT_NAME`: The Overleaf project name. `overleaf-configure` will set this automatically.
- `PROJECT_ID`: The Overleaf project ID. `overleaf-configure` will set this automatically.
- `CONTENT_DIR`: The directory where your local files and changes are stored. Change files here to edit your project locally.
  - `overleaf-configure` will set this up automatically if you don't already have a `content` directory.
- `REMOTE_DIR`: The directory where your remote content on Overleaf is replicated. This determines if your local files are up to date with your remote content.
  - `overleaf-configure` will set this up automatically if you don't already have a `remote` directory.
  - `overleaf-sync` synchronizes this directory with your remote content on Overleaf.
- `TEMP_ARCHIVE`: The name used for temporary downloaded ZIP archives of your Overleaf project. Don't worry about this, just make sure it's unique.
