---
name: Risk Assessment
description: Evaluates operation risk and recommends safeguards before execution. Use before any operation that modifies a target system, when assessing incoming tasks, or when deciding whether to proceed. Also defines the risk field for operational skills.
---

# Risk Assessment

## Risk Matrix

| Level | Criteria | Required Safeguards |
|-------|----------|-------------------|
| **LOW** | Read-only, content edits, status checks | Audit log only |
| **MEDIUM** | Config changes, package updates, user management | Backup recommended, test after |
| **HIGH** | DB changes, migrations, bulk ops, multi-system | Backup required, staging test, explicit approval |
| **CRITICAL** | Data deletion, prod deploys, credential rotation | Full backup verified, rollback plan documented, explicit approval |

## Risk Escalation

If during execution you discover the actual risk is higher than assessed: **STOP immediately.** Re-assess before continuing. Never continue a CRITICAL operation that was originally assessed as MEDIUM.

## Batch Risk

Operations on multiple targets compound risk:
- 10 LOW operations = **MEDIUM** overall
- Any single HIGH in a batch = **HIGH** overall
- CRITICAL operations are never batched without per-target approval

## Time-of-Day Risk

Production changes during business hours: **+1 risk level.** A MEDIUM operation during peak traffic becomes HIGH. Prefer maintenance windows.

## Communication

Always explain risk in terms the supervisor understands:

| Don't Say | Say Instead |
|-----------|-------------|
| "CRITICAL risk level" | "This could take the site offline for 5 minutes" |
| "Requires rollback plan" | "If something goes wrong, here's how we undo it in 2 minutes" |
| "Database migration" | "Changing how the data is organized — like reorganizing a filing cabinet" |

## Operational Skill Frontmatter

Skills that describe operational procedures should include a `risk` field:

```yaml
---
name: Update WordPress Plugins
description: Safe plugin update with backup and verification.
risk: MEDIUM
---
```

This allows `/assess` to automatically determine risk level when matching a task to a skill.

## Before Every Operation

1. **State the risk level** — even for LOW operations
2. **Explain what could go wrong** — in plain English
3. **Describe the safeguards** — what you'll do to prevent or recover from failure
4. **Get approval for MEDIUM+** — never assume consent for risky operations
5. **Log the assessment** — append to AUDIT.md
