Manage the claude-gauge multi-project watch list and refresh the dashboard cache.

Usage:
- `/dashboard-refresh` — show current watched repos, hit the refresh endpoint
- `/dashboard-refresh --add <owner>/<repo>` — add a repo to watched-repos.json
- `/dashboard-refresh --remove <name>` — remove a repo by name or owner/repo

---

## Step 1: Load current config

Read `watched-repos.json` from the claude-gauge project root.

If the file does not exist, create it with an empty repos array:

```json
{
  "_comment": "Multi-project aggregator config. Add repos whose telemetry/**/*.jsonl should be pulled into the dashboard.",
  "repos": []
}
```

---

## Step 2: Handle the flag

### No flag — show status

Print the current watch list:

```
Watched repos (N):
  1. <name> — <owner>/<repo> @ <telemetry_path>
  ...
```

If the list is empty, print:
> "No repos currently watched. Use `/dashboard-refresh --add <owner>/<repo>` to add one."

Then proceed to Step 3 (cache refresh).

### `--add <owner>/<repo>`

Parse `<owner>` and `<repo>` from the argument.

Derive a default `name` from `<repo>` (repo name, lowercase, hyphens preserved).

Append to `repos` array:
```json
{
  "name": "<repo>",
  "owner": "<owner>",
  "repo": "<repo>",
  "telemetry_path": "telemetry"
}
```

If an entry with the same `owner/repo` already exists, print:
> "<owner>/<repo> is already in the watch list." and stop.

Write the updated `watched-repos.json`. Then proceed to Step 3.

### `--remove <name>`

Find the entry where `name` equals `<name>` OR where `<owner>/<repo>` equals `<name>`.

If not found, print:
> "No entry named '<name>' found in watched-repos.json." and stop.

Remove the entry, write the file. Then proceed to Step 3.

---

## Step 3: Refresh the dashboard cache

Determine the dashboard URL:

1. Check `config.json` for `dashboard.url`. Use it if present.
2. Fall back to `https://claude-gauge.vercel.app`.

Hit the refresh endpoint:

```bash
curl -s -X POST <dashboard_url>/refresh
```

Print the JSON response. If the curl fails, print a warning but do not error out — the cache is stateless on Vercel anyway.

---

## Step 4: Commit if changed

If `watched-repos.json` was modified, commit it:

```bash
git add watched-repos.json
git commit -m "chore(gauge): update watched-repos — <action> <target>"
```

Where `<action>` is `add` or `remove` and `<target>` is `<owner>/<repo>`.

Do not push. The user can push with the next `/checkpoint`.

---

## Output Format

```
Dashboard refresh complete.

Watched repos (N):
  1. <name> — <owner>/<repo> @ <telemetry_path>

Cache endpoint: <dashboard_url>/refresh → <status>

Next: push with /checkpoint to sync watched-repos.json to origin.
```
