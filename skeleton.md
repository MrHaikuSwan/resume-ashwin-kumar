# Git + Resume Overleaf Version Manager Skeleton

## Operations:

- overleaf-push
- overleaf-pull
- overleaf-sync
- overleaf-check

## `overleaf-push`

- UNSAFE OPERATION -- REQUIRES CAUTION DURING DEVELOPMENT
- Must not overwrite new changes on remote, since Overleaf has bad version management
- Accomplishes this by locally maintaining a remote archive that is always up to date with the remote
- Pulls remote Overleaf content to a temporary local archive (as a .zip)
  - Note: Fails if a temporary local archive already exists
- Fails if remote archive doesn't match temporary archive
  - Note: This is a safeguard against accidentally overwriting remote Overleaf changes
- Pushes local content archive to remote Overleaf
- Pull updated remote Overleaf content to locally maintained remote archive
- Commits and pushes changes to GitHub repository

## `overleaf-pull`

- May overwrite changes on local, since local Git has good version management
- Avoids unnecessary overwriting by checking for discrepancies between local and remote archives
- Pulls remote Overleaf content to a temporary local archive (as a .zip)
- Overwrites locally maintained content and remote archives with remote Overleaf content
  - Note: Have to unzip temporary local archive before overwriting content archive
- Commits and pushes changes to GitHub repository

## `overleaf-sync`

- Mirrors the remote Overleaf project to the locally maintained remote archive
- Creates a remote archive stored on local (as a .zip)
  - Note: Fails if a remote archive already exists
- Pulls remote Overleaf content into remote archive
- Throws INFO to user if content archive doesn't exist yet
- Informs user if content archive exists but doesn't match remote archive

## `overleaf-check`

- SAFELY checks for synchronicity between the remote Overleaf project to the locally maintained remote archive
- Pulls remote Overleaf content to a temporary local archive (as a .zip)
- Informs user if remote Overleaf content doesn't match remote archive
