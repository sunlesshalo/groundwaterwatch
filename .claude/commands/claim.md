Claim ownership of a feature and check out its branch.

Usage: `/claim <feature-id>`

---

## Prerequisites

Read `config.json`. If `team.enabled` is not `true`, print:

> "Team mode is not enabled. `claim` is a team-mode command. Set `team.enabled = true` in config.json to use it."

Then stop.

Identify:
- `GITHUB_USER` = `identity.github_username`
- Feature `<id>` = the integer passed as the argument (e.g. `/claim 14` → id = 14)

---

## Step 1: Verify the feature is claimable

Read `memory/STATE.json`. Find the feature with the matching `id`.

- If the feature does not exist: print "Feature #<id> not found in STATE.json." and stop.
- If `status = "passing"`: print "Feature #<id> is already passing. Nothing to claim." and stop.
- If `owner` is already set to another user: print "Feature #<id> is owned by <owner> since <owner_since>. Talk to them before claiming." and stop.
- If `owner` equals `GITHUB_USER`: print "You already own feature #<id>." and stop.

---

## Step 2: Update STATE.json

Set on the feature:
```json
"owner": "<GITHUB_USER>",
"owner_since": "<YYYY-MM-DD>",
"branch": "<GITHUB_USER>/feat-<id>"
```

Use today's date for `owner_since`. Do not change `status`, `verified`, or the `feature` description.

---

## Step 3: Create and check out the branch

```bash
git fetch origin

# Create locally (idempotent)
git checkout -B <GITHUB_USER>/feat-<id>

# If the branch already exists on origin, pull it
git pull --rebase origin <GITHUB_USER>/feat-<id> 2>/dev/null || true

# Push to establish tracking (safe even if branch already exists)
git push -u origin <GITHUB_USER>/feat-<id>
```

---

## Step 4: Commit the STATE.json update

```bash
git add memory/STATE.json
git commit -m "chore(team): claim feat-<id> for <GITHUB_USER>"
git push origin <GITHUB_USER>/feat-<id>
```

---

## Output Format

**Claimed:** Feature #<id> — <feature name>

**Branch:** `<GITHUB_USER>/feat-<id>` — created and checked out

**Next:** Work on this feature. Run `/checkpoint` when done to push progress.
