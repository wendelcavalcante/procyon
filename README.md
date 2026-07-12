# Adaptive Level Generation Framework

This project implements a modular software architecture for adaptive game level generation. The framework separates integration, orchestration, adaptation, generation, persistence, and domain-specific plugins into independent packages, allowing different techniques to be combined and replaced without redesigning the complete system.

The current prototype focuses on adaptive difficulty for puzzle games and includes example plugins for:

* Fifteen Puzzle
* Sudoku
* Sokoban

The implementation is intended as a research prototype and coding framework. It does not aim to provide state-of-the-art implementations for every component. Instead, it provides lightweight but complete implementations that demonstrate how adaptive generation workflows can be composed, executed, persisted, and extended.

---

## Main Features

* Layered architecture for adaptive level generation
* Plug-in generation pipelines
* Replaceable generators, validators, solvers, assessors, and selectors
* Replaceable player modeling and DDA strategies
* Stateful and stateless execution modes
* SQLite-based persistence adapter
* FastAPI integration adapter
* Candidate-level metadata for experimentation
* Support for returning all generated candidates or only the selected level
* Example pipelines for Fifteen Puzzle, Sudoku, and Sokoban

---

## Architecture Overview

The framework is organized into the following layers:

```text
Integration Layer
  Receives requests from a game runtime, simulation, API, file exchange, or other external adapter.

Orchestration Layer
  Coordinates the adaptive generation workflow.

Adaptation Core
  Processes telemetry, updates the player model, applies design goals, and produces adaptation decisions.

Generation Core
  Builds and executes configurable generation pipelines.

Persistence Layer
  Stores player states, telemetry summaries, performance observations, adaptation decisions, and generation metadata.

Plugins
  Provide domain-specific generators, validators, solvers, difficulty assessors, and candidate selectors.
```

The same workflow can be used in two execution modes:

```text
Stateless mode:
  The request provides the last player state.
  The response returns the updated player state.

Stateful mode:
  The request provides a player identifier.
  The framework retrieves the latest player state from persistence,
  updates it, and stores it again.
```

---

## Package Structure

A simplified package structure is shown below:

```text
src/procyon/
├── adaptation/
│   ├── engine.py
│   └── types.py
├── core/
│   └── types.py
├── generation/
│   ├── pipeline.py
│   ├── stages.py
│   └── types.py
├── integration/
│   └── fastapi/
│       ├── app.py
│       ├── dependencies.py
│       └── routes.py
├── orchestration/
│   ├── dto.py
│   ├── mappers.py
│   └── orchestrator.py
├── persistence/
│   ├── ports.py
│   ├── unit_of_work.py
│   └── sqlite/
│       ├── connection.py
│       ├── repositories.py
│       └── schema.py
├── player_modeling/
│   ├── probabilistic.py
│   ├── types.py
│   └── updaters.py
├── plugins/
│   └── puzzles/
│       ├── fifteen/
│       ├── sudoku/
│       └── sokoban/
└── telemetry/
    └── types.py
```

---

## Installation

Create a virtual environment and install the package in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate

pip install -e .
```

To use the FastAPI adapter:

```bash
pip install -e ".[api]"
```

---

## Running Tests

```bash
pytest
```

---

## Running the Case Study Examples

The repository includes three case study examples corresponding to the puzzle domains discussed in the paper:

```text
examples/
├── fifteen_case_study.py
├── sudoku_case_study.py
└── sokoban_case_study.py
```

Each example uses the stateful execution mode with SQLite persistence. The first execution creates the local database file under the `runtime/` directory. Subsequent executions reuse the persisted player state for the same player-domain pair.

Run the Fifteen Puzzle case study:

```bash
python examples/fifteen_case_study.py
```

Run the Sudoku case study:

```bash
python examples/sudoku_case_study.py
```

Run the Sokoban case study:

```bash
python examples/sokoban_case_study.py
```

To reset a case study, remove the corresponding SQLite database file:

```bash
rm runtime/fifteen_case_study.sqlite3
rm runtime/sudoku_case_study.sqlite3
rm runtime/sokoban_case_study.sqlite3
```

Each script prints the updated player state, the adaptation decision, the selected level, and the generation summary. These examples illustrate the same adaptive generation workflow using different generation strategies:

```text
Fifteen Puzzle → generate-and-test
Sudoku         → multi-stage generation
Sokoban        → reverse generation
```
---

## Generation Pipelines

Generation is organized as a pipeline of independent stages. A pipeline may include candidate generation, validation, difficulty assessment, and selection.

Example:

```python
from procyon.generation.pipeline import GenerationPipeline
from procyon.generation.stages import (
    GenerateCandidatesStage,
    ValidateCandidatesStage,
    AssessDifficultyStage,
    SelectClosestDifficultyCandidateStage,
)
from procyon.plugins.puzzles.fifteen.generators import FisherYatesFifteenGenerator
from procyon.plugins.puzzles.fifteen.validators import FifteenSolvabilityValidator
from procyon.plugins.puzzles.fifteen.assessors import FifteenManhattanDifficultyAssessor

pipeline = (
    GenerationPipeline()
    .then(
        GenerateCandidatesStage(
            FisherYatesFifteenGenerator(
                seed=42,
                candidate_count=100,
            )
        )
    )
    .then(
        ValidateCandidatesStage(
            FifteenSolvabilityValidator()
        )
    )
    .then(
        AssessDifficultyStage(
            FifteenManhattanDifficultyAssessor()
        )
    )
    .then(
        SelectClosestDifficultyCandidateStage()
    )
)
```

The pipeline returns a `GenerationResult`, which contains all candidate records and, when selection is enabled, the selected candidate.

---

## Example: Stateless Execution

In stateless mode, the request provides the last known player state. The framework updates it and returns the new state in the response.

```python
from procyon.orchestration import (
    AdaptiveGenerationRequestDTO,
    create_default_orchestrator,
)

orchestrator = create_default_orchestrator()

request = AdaptiveGenerationRequestDTO.model_validate(
    {
        "session_id": "session_001",
        "player_id": "player_001",
        "runtime": {
            "source": "simulation",
            "game": "sokoban_prototype",
        },
        "last_player_state": {
            "skill": 0.50,
            "uncertainty": 0.50,
            "engagement": 0.60,
            "frustration": 0.10,
            "confidence": 0.50,
            "observations_count": 0,
        },
        "telemetry": {
            "level_id": "level_001",
            "estimated_difficulty": 0.40,
            "success": True,
            "solving_time": 65.0,
            "move_count": 42,
            "mistake_count": 2,
            "restart_count": 0,
            "hint_count": 0,
            "give_up": False,
        },
        "design_goals": {
            "target_experience": "balanced_challenge",
            "allowed_dimensions": ["difficulty"],
            "constraints": {
                "min_difficulty": 0.10,
                "max_difficulty": 0.90,
                "max_step_change": 0.10,
            },
        },
        "generation": {
            "domain": "sokoban",
            "strategy": "reverse_search",
            "candidate_count": 20,
            "include_candidates": False,
            "parameters": {
                "width": 9,
                "height": 9,
                "reverse_steps": 30,
                "wall_density": 0.12,
                "seed": 42,
                "select": True,
            },
        },
    }
)

response = orchestrator.generate_next(request)

print(response.updated_player_state)
print(response.adaptation_decision)
print(response.selected_level)
```

---

## Example: Stateful Execution with SQLite

In stateful mode, the framework retrieves the latest player state from persistence using the player identifier and requested domain.

The first request for a player-domain pair creates an initial state. Later requests reuse the persisted state.

```python
from procyon.orchestration import (
    AdaptiveGenerationRequestDTO,
    create_sqlite_orchestrator,
)

orchestrator = create_sqlite_orchestrator("runtime/procyon.sqlite3")

request = AdaptiveGenerationRequestDTO.model_validate(
    {
        "session_id": "session_001",
        "player_id": "player_001",
        "runtime": {
            "source": "simulation",
            "game": "sokoban_prototype",
        },
        "telemetry": {
            "level_id": "level_001",
            "estimated_difficulty": 0.40,
            "success": True,
            "solving_time": 65.0,
            "move_count": 42,
            "mistake_count": 2,
            "restart_count": 0,
            "hint_count": 0,
            "give_up": False,
        },
        "design_goals": {
            "target_experience": "balanced_challenge",
            "allowed_dimensions": ["difficulty"],
            "constraints": {
                "min_difficulty": 0.10,
                "max_difficulty": 0.90,
                "max_step_change": 0.10,
            },
        },
        "generation": {
            "domain": "sokoban",
            "strategy": "reverse_search",
            "candidate_count": 20,
            "include_candidates": False,
            "parameters": {
                "width": 9,
                "height": 9,
                "reverse_steps": 30,
                "wall_density": 0.12,
                "seed": 42,
                "select": True,
            },
        },
    }
)

response = orchestrator.generate_next(request)

print(response.updated_player_state)
print(response.adaptation_decision)
print(response.selected_level)
```

In the current prototype, persisted player states are separated by player and domain. Internally, an identifier such as the following may be derived:

```text
player_001::sokoban
player_001::sudoku
player_001::fifteen
```

This prevents a player state learned in one puzzle domain from being automatically reused in another unrelated domain.

---

## Persistence

The persistence layer uses ports and adapters.

The core workflow depends on persistence ports, not on SQLite directly. SQLite is only the default adapter used in the prototype.

Persisted data includes:

```text
player_states
telemetry_summaries
performance_observations
adaptation_decisions
```

The SQLite database is initialized automatically when using:

```python
create_sqlite_orchestrator("runtime/procyon.sqlite3")
```

If the target directory does not exist, the SQLite connection factory creates it automatically.

---

## Dynamic Difficulty Adjustment

The current prototype implements a lightweight probabilistic player model updater.

The updater estimates the expected probability of success from:

```text
current player skill
previous level difficulty
```

After receiving telemetry, it updates the skill estimate according to the prediction error between expected and observed success.

Conceptually:

```text
expected_success = sigmoid((skill - difficulty) / temperature)

prediction_error = observed_success - expected_success

new_skill = skill + learning_rate * prediction_error * uncertainty
```

The model also updates uncertainty, confidence, engagement, and frustration.

This implementation is intentionally simple and replaceable. Other DDA approaches can implement the same player modeling interface, including:

```text
rule-based methods
probabilistic methods
dynamic scripting
reinforcement learning
bandit-based methods
neural models
```

---

## Running the FastAPI Adapter

Install the API dependencies:

```bash
pip install -e ".[api]"
```

Run:

```bash
uvicorn procyon.integration.fastapi.app:app --reload
```

By default, the API uses a local SQLite database:

```text
procyon.sqlite3
```

To change the database path:

```bash
PROCYON_SQLITE_PATH=runtime/procyon.sqlite3 \
uvicorn procyon.integration.fastapi.app:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/v1/health
```

Adaptive generation endpoint:

```text
POST /v1/generate-next
```

---

## Example API Request

```bash
curl -X POST http://127.0.0.1:8000/v1/generate-next \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_001",
    "player_id": "player_001",
    "runtime": {
      "source": "simulation",
      "game": "sokoban_prototype"
    },
    "telemetry": {
      "level_id": "level_001",
      "estimated_difficulty": 0.40,
      "success": true,
      "solving_time": 65.0,
      "move_count": 42,
      "mistake_count": 2,
      "restart_count": 0,
      "hint_count": 0,
      "give_up": false
    },
    "design_goals": {
      "target_experience": "balanced_challenge",
      "allowed_dimensions": ["difficulty"],
      "constraints": {
        "min_difficulty": 0.10,
        "max_difficulty": 0.90,
        "max_step_change": 0.10
      }
    },
    "generation": {
      "domain": "sokoban",
      "strategy": "reverse_search",
      "candidate_count": 20,
      "include_candidates": false,
      "parameters": {
        "width": 9,
        "height": 9,
        "reverse_steps": 30,
        "wall_density": 0.12,
        "seed": 42,
        "select": true
      }
    }
  }'
```

---

### Fifteen Puzzle

Example strategy:

```text
random candidate generation
solvability validation
Manhattan-distance difficulty assessment
closest-difficulty candidate selection
```

Typical pipeline:

```text
GenerateCandidatesStage
→ ValidateCandidatesStage
→ AssessDifficultyStage
→ SelectClosestDifficultyCandidateStage
```

Run the corresponding example:

```bash
python examples/fifteen_pipeline_example.py
```

Or, if the example is organized as a module:

```bash
python -m examples.fifteen_pipeline_example
```

---

### Sudoku

Example strategy:

```text
solved-grid generation
clue removal
unique-solution validation
search-based difficulty assessment
closest-difficulty candidate selection
```

Typical pipeline:

```text
GenerateCandidatesStage
→ RemoveSudokuCluesStage
→ ValidateCandidatesStage
→ AssessDifficultyStage
→ SelectClosestDifficultyCandidateStage
```

Run the corresponding example:

```bash
python examples/sudoku_pipeline_example.py
```

Or, if the example is organized as a module:

```bash
python -m examples.sudoku_pipeline_example
```

---

### Sokoban

Example strategy:

```text
reverse generation from a solved state
construction-based solvability
metadata-based difficulty assessment
closest-difficulty candidate selection
```

Typical pipeline:

```text
GenerateCandidatesStage
→ AssessDifficultyStage
→ SelectClosestDifficultyCandidateStage
```

Run the corresponding example:

```bash
python examples/sokoban_pipeline_example.py
```

Or, if the example is organized as a module:

```bash
python -m examples.sokoban_pipeline_example
```

---

## Returning All Candidates

For experimental analysis, set:

```json
"include_candidates": true
```

The response will include candidate summaries, enabling analyses such as:

```text
difficulty distribution
solvability rate
generation cost
candidate diversity
selection behavior
```

Example:

```python
response = orchestrator.generate_next(request)

for candidate in response.generation_result.candidates:
    print(candidate.candidate_id)
    print(candidate.is_active)
    print(candidate.difficulty_score)
```

---

## Creating a Difficulty Histogram

```python
import matplotlib.pyplot as plt

result = pipeline.run(adaptation_request)

difficulties = [
    candidate.difficulty.score
    for candidate in result.active_candidates
    if candidate.difficulty is not None
]

plt.figure(figsize=(8, 5))
plt.hist(difficulties, bins=10, edgecolor="black")
plt.title("Difficulty Distribution of Valid Generated Candidates")
plt.xlabel("Difficulty score")
plt.ylabel("Number of candidates")
plt.xlim(0.0, 1.0)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()
```

---

## Extending the Framework

The framework can be extended by implementing new components.

Examples:

```text
new generators
new validators
new solvers
new difficulty assessors
new candidate selectors
new player model updaters
new adaptation engines
new persistence adapters
new integration adapters
```

---

### Implementing a New Player Model Updater

```python
from procyon.player_modeling.types import PlayerModelState, PerformanceObservation
from procyon.player_modeling.updaters import PlayerModelUpdater
from procyon.telemetry.types import TelemetrySummary


class CustomPlayerModelUpdater(PlayerModelUpdater):
    def update(
        self,
        previous_state: PlayerModelState,
        telemetry: TelemetrySummary | None,
    ) -> tuple[PlayerModelState, PerformanceObservation | None]:
        # Implement a custom DDA/player modeling strategy here.
        return previous_state, None
```

---

### Implementing a New Persistence Adapter

```python
from procyon.persistence.ports import PlayerStateRepository
from procyon.player_modeling.types import PlayerModelState


class CustomPlayerStateRepository(PlayerStateRepository):
    def get(self, player_id: str) -> PlayerModelState | None:
        # Load state from another backend.
        return None

    def save(self, player_id: str, state: PlayerModelState) -> None:
        # Save state to another backend.
        pass
```

---

### Implementing a New Pipeline Stage

```python
from dataclasses import dataclass

from procyon.generation.pipeline import PipelineStage
from procyon.generation.types import GenerationContext


@dataclass(slots=True)
class CustomStage(PipelineStage):
    def process(self, context: GenerationContext) -> GenerationContext:
        # Modify candidates, metadata, selection, or context state here.
        return context
```

---

## Current Limitations

The current prototype intentionally uses lightweight implementations.

Known limitations include:

```text
player modeling is simple and probabilistic
difficulty metrics are proxies
Sokoban generation is limited to small maps and simple configurations
Sudoku difficulty is based on search effort rather than human solving techniques
SQLite persistence is intended for prototyping, not production deployment
```

These limitations are intentional and reflect the goal of demonstrating the architecture as an extensible framework rather than optimizing every individual component.

---

## Research Usage

The prototype can be used to study:

```text
adaptive generation workflows
DDA strategies
difficulty assessment methods
generation pipeline composition
domain-specific plugin design
stateful versus stateless execution
candidate-level analysis
```

The framework is especially suitable for experiments in which different generation strategies, difficulty metrics, player models, and adaptation policies must be compared under the same orchestration workflow.
