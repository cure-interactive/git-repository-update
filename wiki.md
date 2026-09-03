# Git Repository Update Wiki

Git Repository Update is a standalone desktop app for scanning local Git repositories and running safe bulk updates.

## Quick Start

```bash
python setup.py --venv
python git-repository-update.py
```

Manual install:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python git-repository-update.py
```

On Linux or macOS, use `source .venv/bin/activate`.

## First Run

On first run, `config.json` is created from `config-default.json`.

In the app:

1. Open the Config tab.
2. Add one or more scan roots, for example `D:\Repos`.
3. Optionally set a global fallback SSH key.
4. Add SSH routing rules for remote hosts or organization path prefixes that require different keys.
5. Save or allow auto-save.
6. Run Refresh to scan repositories.
7. Review the table, including the Key Source column.
8. Run Pull with dry-run enabled first.

## SSH Key Routing

The app resolves a private key in this order:

1. A key explicitly configured for the repository.
2. The most-specific enabled rule matching the normalized SSH remote host, optional port, and path prefix.
3. The global fallback key.
4. A TortoiseGit global key or the normal SSH configuration when no app key applies.

Both SCP-style remotes such as `git@github.com:cure-interactive/example.git` and `ssh://` remotes are normalized before matching. HTTPS remotes do not match SSH rules. Use **Preview Matches** to count matches against the current repository manifest before pulling.

## Repository Order

Refresh writes every discovered repository path to the top-level `repositories` list in `config.json`, sorted case-insensitively by full path. The GUI table uses that same order, and Pull processes the list strictly from first to last. A later Refresh removes paths that are no longer discovered and inserts newly discovered repositories into the deterministic order.

Repositories listed in `filters.pull_disabled` remain visible and ordered but are marked **Pull disabled** and skipped by both Pull All and Pull Selected. Use this for pinned releases, archived checkouts, and branches that require manual reconciliation.

Failed pulls retain the complete Git diagnostic in the log and manifest while the table shows a compact reason such as **Error (Auth)**, **Error (Diverged)**, **Error (Local Changes)**, or **Error (Network)**.

## Runtime Files

The app may create:

- `config.json`
- `config_restore.json`
- `repository_manifest.json`
- log files

These are local runtime files and are ignored by Git.

## Vendored Helper

`packages_custom/cure-repo-manifest.py` is included in this repository so the app does not depend on any sibling repository.
