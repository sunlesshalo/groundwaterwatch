Optimize a skill using auto-research: iterative eval loops that make the prompt better over time.

## Usage

```
/optimize-skill [skill-path] [--runs N] [--iterations N]
```

- `skill-path`: Path to the skill directory (e.g., `.claude/skills/diagram-generator`)
- `--runs`: Outputs per iteration (default: 5)
- `--iterations`: Max iterations (default: 10)

If no arguments provided, ask the user for the skill path.

## Step 1: Load the Skill

Read the SKILL.md from the provided path:

```bash
cat [skill-path]/SKILL.md
```

Understand what the skill does and what "good output" looks like.

## Step 2: Define Eval Criteria

Ask the user:

> **What makes this skill's output good?**
> Give me 3-6 binary (yes/no) criteria. Examples:
> - "Is the output under 200 words?"
> - "Does it contain a specific call-to-action?"
> - "Is the code syntactically valid?"

If the user has already provided criteria (in their message or in a file), use those.

Save the eval criteria to `.tmp/experiments/[skill-name]/eval-criteria.md`:

```markdown
# Eval Criteria for [skill-name]

1. [criterion 1] (yes/no)
2. [criterion 2] (yes/no)
3. [criterion 3] (yes/no)
...
```

## Step 3: Set Up Experiment Tracking

```bash
SKILL_NAME=$(basename [skill-path])
mkdir -p .tmp/experiments/$SKILL_NAME/versions .tmp/experiments/$SKILL_NAME/results
```

Copy the current SKILL.md as the baseline:

```bash
cp [skill-path]/SKILL.md .tmp/experiments/$SKILL_NAME/versions/v000-baseline.md
echo '0' > .tmp/experiments/$SKILL_NAME/best-score.txt
```

## Step 4: Run the Optimization Loop

For each iteration (0 to max_iterations):

### 4a. Execute the Skill

Run the skill N times with varied inputs. Collect all outputs.

How you run it depends on the skill:
- **Text skills**: Generate the output directly using the skill's instructions
- **Code skills**: Run the generated code and capture results
- **Image skills**: Call the image generation API/tool
- **External tool skills**: Execute the tool and capture output

### 4b. Evaluate Each Output

For each output, evaluate against every criterion. Use this format:

```
Output 1:
  [criterion 1]: PASS / FAIL
  [criterion 2]: PASS / FAIL
  ...

Output 2:
  [criterion 1]: PASS / FAIL
  ...
```

Be honest and strict. A "maybe" is a FAIL.

### 4c. Score

```
Score = total PASS count
Max Score = runs × criteria_count
Percentage = (Score / Max Score) × 100
```

### 4d. Log the Iteration

Append to `.tmp/experiments/[skill-name]/experiment-log.jsonl`:

```bash
echo '{"iteration": N, "score": S, "max_score": M, "pct": P, "is_best": true/false, "changes": "description of changes", "timestamp": "YYYY-MM-DDTHH:MM:SS"}' >> .tmp/experiments/$SKILL_NAME/experiment-log.jsonl
```

Save detailed results to `.tmp/experiments/[skill-name]/results/run-NNN.json`.

### 4e. Check for Improvement

```bash
BEST=$(cat .tmp/experiments/$SKILL_NAME/best-score.txt)
```

If current score > best:
- Update `best-score.txt`
- Copy current SKILL.md to `best-prompt.md`
- Save version to `versions/vNNN.md`

### 4f. Mutate the Prompt

If not the final iteration:

1. Identify which criteria failed most frequently
2. Read the current SKILL.md
3. Make ONE targeted change to address the most common failure
4. Write the mutated version back to `[skill-path]/SKILL.md`
5. Save a copy to `versions/vNNN.md`

**Mutation rules:**
- Change ONE thing per iteration
- Be specific (replace vague with concrete)
- Preserve instructions that score 100%
- Log exactly what you changed and why

### 4g. Stop Conditions

Stop early if:
- Score reaches 95%+ (or user's target)
- 3 consecutive iterations with no improvement
- User interrupts

## Step 5: Report Results

After all iterations (or early stop), output:

```
## Optimization Results: [skill-name]

**Iterations:** N
**Starting score:** X/M (P%)
**Final best score:** Y/M (P%)
**Improvement:** +Z points (+P%)

### Score Progression
| Iteration | Score | % | Best? | Change Made |
|-----------|-------|---|-------|-------------|
| 0 | X/M | P% | yes | baseline |
| 1 | X/M | P% | yes/no | [change] |
| ... | | | | |

### Key Mutations That Helped
1. [change description] → +N points
2. ...

### Best Prompt Version
Saved to: .tmp/experiments/[skill-name]/best-prompt.md

### Experiment Log
Full log: .tmp/experiments/[skill-name]/experiment-log.jsonl
```

## Step 6: Apply or Revert

Ask the user:

> **Apply the best version to the skill?**
> - Yes → Copy `best-prompt.md` back to `[skill-path]/SKILL.md`
> - No → Keep the original, results are saved for reference

## Notes

- The experiment log is valuable even if improvements are small — it records what was tried
- For skills that call external APIs (image generation, etc.), be mindful of costs
- Binary evals only. No scales. No "rate 1-7".
- If a skill has no clear eval criteria, help the user define them before starting
