# AI Interactions Log

## Request and scope
The user asked Codex to complete and submit Weeks 7 and 8 and check every required item. Codex read the live course instructions and rubric, cloned the official starter, implemented the changes, and ran the logged commands. This log does not fabricate separate conversations, human manual corrections, or model comparisons.

## Agentic workflow
Task: complete the CLI-first content-based music simulation with an expanded catalog, explained ranking and behavior tests.
Files changed: src/recommender.py, src/main.py, src/__init__.py, data/songs.csv, tests/test_functional.py, pytest.ini, requirements.txt, README.md, model_card.md, evidence/*, diagrams/architecture.mmd.
Result: all three starter TODO functions and both OOP methods work; the module import was fixed; 20 rows load; 24 tests pass.
Validation was automated by Codex. No independent human manual code verification is claimed.

## Design pattern
A small Strategy mapping (MODES) selects genre-first, mood-first, or energy-first weights. The scorer is shared instead of duplicating three implementations. The CLI exposes --mode; the saved conflicting-profile experiment demonstrates that switching it changes the ranking.

## Diversity and formatting
The assistant implemented greedy artist-penalty selection and a plain ASCII table with exact reason strings. Output with and without penalty is saved in the README and evidence. This is artist variety, not a demonstrated solution to demographic bias.

## Decisions
Accepted: explain the contribution of each feature and use absolute energy distance.
Revised alternative: keep the application standard-library and CLI-only instead of adding a web UI or data-frame layer. This removes unused starter dependencies and makes reproduction easier.

## Evidence
See evidence/run-1.txt through evidence/run-5.txt for the actual commands, recommendations, weight shift, diversity run, and passing test output.
