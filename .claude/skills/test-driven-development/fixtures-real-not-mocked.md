# Fixtures: real, not mocked

**Rule:** For parser, aggregator, or transformation tests, use a **real excerpt** of production data as the fixture. Never fabricate synthetic data that conforms to your mental model of the schema.

## Why

Fabricated fixtures encode your *assumptions* about the data. Real fixtures encode the data's *actual shape*, including edge cases you didn't think of.

**Evidence (claude-gauge, 2026-04-11):** The JSONL parser tests used a real excerpt from `~/.claude/projects/.../*.jsonl`. The tests caught a dedup bug where two messages shared the same `requestId` (a case not in the spec). A synthetic fixture — built from the documented schema — would have passed silently and shipped the bug to production.

## How to apply

- **Parsing code:** pull 5–20 real records from the production source. Redact PII but preserve structure.
- **Aggregation code:** take a real time window (e.g., one day of real telemetry).
- **API response shapes:** save a real response body from a curl/httpie call.

## When it's OK to fabricate

- Unit tests for pure functions with no external data dependency.
- Property-based tests (the generator itself is the "fixture").
- Error-path tests where you need malformed input that doesn't exist in prod.
