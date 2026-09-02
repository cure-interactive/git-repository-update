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
3. Optionally set a default SSH key.
4. Save or allow auto-save.
5. Run Refresh to scan repositories.
6. Review the table.
7. Run Pull with dry-run enabled first.

## Runtime Files

The app may create:

- `config.json`
- `config_restore.json`
- `repository_manifest.json`
- log files

These are local runtime files and are ignored by Git.

## Vendored Helper

`packages_custom/cure-repo-manifest.py` is included in this repository so the app does not depend on any sibling repository.
