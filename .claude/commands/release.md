Release ownership of a feature after it has been merged or handed off.

Usage: `/release <feature-id>`

---

## Prerequisites

Read `config.json`. If `team.enabled` is not `true`, print:

> "Team mode is not enabled. `release` is a team-mode command. Set `team.enabled = true` in config.json to use it."

Then stop.

Identify:
- `GITHUB_USER` = `identity.github_username`
- Feature `<id>` = the integer passed as the argument

---

## Step 1: Verify the feature can be released

Read `memory/STATE.json`. Find the feature with the matching `id`.

- If the feature does not exist: print "Feature #<id> not found in STATE.json." and stop.
- If `owner` is not set or is empty: print "Feature #<id> has no owner — nothing to release." and stop.
- If `owner` does not equal `GITHUB_USER`: print "Feature #<id> is owned by <owner>, not you. Only the owner can release." and stop.

---

## Step 2: Update STATE.json

Remove the ownership fields from the feature:
- Delete `owner`
- Delete `owner_since`
- Delete `branch`

Do not change `status`, `verified`, or the `feature` description.

---

## Step 3: Commit the STATE.json update

```bash
git add memory/STATE.json
git commit -m "chore(team): release feat-<id> from <GITHUB_USER>"
git push origin <GITHUB_USER>/feat-<id>
```

---

## Step 4: Optional — switch back to default branch

If the current branch is `<GITHUB_USER>/feat-<id>`, offer to switch back:

```bash
git checkout <DEFAULT_BRANCH>
git pull --rebase origin <DEFAULT_BRANCH>
```

Only do this if the user confirms or passes `--switch` flag.

---

## Output Format

**Released:** Feature #<id> — <feature name>

**Owner fields cleared** in STATE.json.

**Next:** The feature is now unclaimed. Either merge the branch via PR, or leave it for the other team member to pick up with `/claim <id>`.
