# Git Repository Update

CustomTkinter app for scanning local Git repositories and updating them in bulk.

## What It Does

- Scans configured roots for Git repositories
- Records repository status in `repository_manifest.json`
- Routes validated PuTTY and OpenSSH private keys by repository override, remote namespace, or global fallback
- Runs `git pull --ff-only` across selected repositories
- Supports dry-run workflows

This standalone repository includes the small `packages_custom/` helper module used by the app, so it does not require a sibling package checkout at runtime.

## Requirements

- Python 3.10+
- Git installed and available on `PATH`
- Dependencies from `requirements.txt`

## Install

```bash
python setup.py --venv
```

Or manually:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On Linux or macOS, activate the virtual environment with `source .venv/bin/activate`.

## Configure And Run

```bash
python git-repository-update.py
```

On first run, `config.json` is created from `config-default.json`. Add scan roots in the Config tab, run Refresh, then run Pull when the planned repository list looks correct.

See `wiki.md` for detailed workflow notes.
