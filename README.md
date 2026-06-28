# Procyon

Prototype architecture for adaptive game level design generation.

Procyon is organized around a composable generation pipeline inspired by modular ML pipelines.
The architecture is intended to support multiple adaptive game level design dimensions, such as difficulty, gameplay, layout, assets, soundtrack, and narrative.

Current prototype scope:

```text
difficulty adaptation in puzzle games using simulated telemetry
```

## Architectural flow

```text
Game Runtime / Simulated Player
→ Telemetry Collector
→ Player Model
→ Adaptation Engine
→ Adaptation Request
→ Pipeline Builder
→ Configured Generation Pipeline
→ Validator / Solver
→ Difficulty Assessor
→ Candidate Evaluator / Selector
→ Adapted Level Design
```

## Initial Fifteen Puzzle components

- `FisherYatesFifteenGenerator`
- `ReverseShuffleFifteenGenerator`
- `FifteenSolvabilityValidator`
- `FifteenManhattanDifficultyAssessor`

The Fisher-Yates generator produces candidate boards without checking solvability. Solvability is handled by a pluggable validator stage.

The Reverse Shuffle generator produces boards by legal moves from the solved state. It does not call a validator internally, but a validator may still be plugged into a pipeline.

## Setup

```bash
pyenv local 3.11.12
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python examples/fifteen_basic.py
```
