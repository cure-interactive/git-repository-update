from __future__ import annotations

import datetime as _dt
import json
import os
import typing as t

__version__ = "0.1.0"


class RepoState(t.TypedDict, total=False):
  """
  Minimal per-repo status persisted in repository_manifest.json (v2).

  Notes:
  - `path` must be absolute (as produced by repository_bulk).
  - `seen_at` / `pulled_at` are ISO timestamps (timespec="seconds").
  - `index` is 1-based display ordering (stable sort by path lowercased).
  """
  index: int
  path: str
  ssh_key: str
  ssh_key_source: str
  remote_url: str
  pull_disabled: bool

  phase: str        # idle | queued | scanning | pulling | done | error | skipped | stopped
  message: str      # short label shown in the table

  seen_at: str      # ISO timestamp
  pulled_at: str    # ISO timestamp

  last_error: str


class ManifestV2(t.TypedDict, total=False):
  version: int
  last_sync_at: str
  repos: t.List[RepoState]


# =============================================================================
# Time helpers
# =============================================================================

def now_iso() -> str:
  return _dt.datetime.now().isoformat(timespec="seconds")


def ts_short(iso_ts: str) -> str:
  """
  Short, UI-friendly timestamp. Tooltip can show the raw ISO.
  """
  if not iso_ts:
    return "-"
  try:
    dt = _dt.datetime.fromisoformat(iso_ts)
    return dt.strftime("%Y-%m-%d %H:%M")
  except Exception:
    return iso_ts


# =============================================================================
# JSON IO (atomic write)
# =============================================================================

def _read_json(path: str) -> t.Any:
  with open(path, "r", encoding="utf-8") as f:
    return json.load(f)


def _atomic_write_json(path: str, data: t.Any, *, indent: int = 2, sort_keys: bool = True) -> None:
  root = os.path.dirname(path)
  if root:
    os.makedirs(root, exist_ok=True)

  tmp = path + ".tmp"
  with open(tmp, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=indent, sort_keys=sort_keys)
    f.write("\n")

  os.replace(tmp, path)


# =============================================================================
# Manifest v2 normalization
# =============================================================================

def load_manifest_v2(path: str) -> ManifestV2:
  """
  Loads repository_manifest.json and normalizes to v2 format.

  Supported inputs:
  - v2: { "version": 2, "repos": [ {RepoState}, ... ] }
  - v1: { "<repo_path>": "<ssh_key>", ... }
  - legacy list: [ [ "<repo_path>", "<ssh_key>" ], ... ]
  """
  if not os.path.exists(path):
    return ManifestV2(version=2, repos=[])

  raw = _read_json(path)

  # v2
  if isinstance(raw, dict) and raw.get("version") == 2 and isinstance(raw.get("repos"), list):
    m: ManifestV2 = t.cast(ManifestV2, raw)
    repos = m.get("repos", []) or []
    _index_repos(repos)
    m["version"] = 2
    m["repos"] = repos
    return m

  # v1 mapping
  if isinstance(raw, dict):
    repos: t.List[RepoState] = []
    for repo_path, ssh_key in raw.items():
      p = str(repo_path) if repo_path else ""
      if not p:
        continue
      repos.append(RepoState(
        path=p,
        ssh_key=str(ssh_key) if ssh_key else "",
        phase="idle",
        message="Idle",
        seen_at="",
        pulled_at="",
      ))
    _index_repos(repos)
    return ManifestV2(version=2, repos=repos)

  # legacy list of pairs
  if isinstance(raw, list):
    repos = []
    for row in raw:
      if isinstance(row, (list, tuple)) and len(row) >= 1:
        p = str(row[0]) if row[0] else ""
        k = str(row[1]) if (len(row) >= 2 and row[1]) else ""
        if not p:
          continue
        repos.append(RepoState(
          path=p,
          ssh_key=k,
          phase="idle",
          message="Idle",
          seen_at="",
          pulled_at="",
        ))
    _index_repos(repos)
    return ManifestV2(version=2, repos=repos)

  # unknown
  return ManifestV2(version=2, repos=[])


def save_manifest_v2(path: str, manifest: ManifestV2, *, dry_run: bool) -> None:
  """
  Persists manifest v2. Always updates last_sync_at.
  """
  repos = manifest.get("repos", []) or []
  _index_repos(repos)
  manifest["version"] = 2
  manifest["repos"] = repos
  manifest["last_sync_at"] = now_iso()

  if dry_run:
    return

  _atomic_write_json(path, manifest, indent=2, sort_keys=True)


def _index_repos(repos: t.List[RepoState]) -> None:
  repos.sort(key=lambda r: (str(r.get("path", "")).lower()))
  for i, r in enumerate(repos, start=1):
    r["index"] = i


def repos_by_path(manifest: ManifestV2) -> t.Dict[str, RepoState]:
  out: t.Dict[str, RepoState] = {}
  for r in (manifest.get("repos", []) or []):
    p = str(r.get("path", "") or "")
    if p:
      out[p] = r
  return out


def upsert_repo(
  manifest: ManifestV2,
  repo_path: str,
  *,
  ssh_key: str | None = None,
  phase: str | None = None,
  message: str | None = None,
  seen_at: str | None = None,
  pulled_at: str | None = None,
  last_error: str | None = None,
) -> RepoState:
  """
  Upserts one repo by absolute path.
  """
  repo_path = str(repo_path or "")
  if not repo_path:
    raise ValueError("repo_path is required")

  repos = manifest.setdefault("repos", [])
  byp = repos_by_path(manifest)

  r = byp.get(repo_path)
  if r is None:
    r = RepoState(
      path=repo_path,
      ssh_key="",
      phase="idle",
      message="Idle",
      seen_at="",
      pulled_at="",
    )
    repos.append(r)

  if ssh_key is not None:
    r["ssh_key"] = ssh_key
  if phase is not None:
    r["phase"] = phase
  if message is not None:
    r["message"] = message
  if seen_at is not None:
    r["seen_at"] = seen_at
  if pulled_at is not None:
    r["pulled_at"] = pulled_at
  if last_error is not None:
    r["last_error"] = last_error

  return r
