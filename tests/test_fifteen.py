from procyon.core.artifacts import AdaptationRequest
from procyon.core.types import AdaptiveDimension
from procyon.plugins.puzzles.fifteen import FifteenManhattanDifficultyAssessor, FifteenSolvabilityValidator, FisherYatesFifteenGenerator, ReverseShuffleFifteenGenerator

def make_request() -> AdaptationRequest:
    return AdaptationRequest(dimensions={AdaptiveDimension.DIFFICULTY}, target_parameters={"target_difficulty": 0.5})

def test_fisher_yates_generates_candidates() -> None:
    candidates = FisherYatesFifteenGenerator(seed=42, candidate_count=3).generate(make_request())
    assert len(candidates) == 3
    assert candidates[0].content["puzzle"] == "fifteen"
    assert len(candidates[0].content["board"]) == 16

def test_reverse_shuffle_candidate_is_solvable() -> None:
    candidate = ReverseShuffleFifteenGenerator(seed=42, iterations=80).generate(make_request())[0]
    assert FifteenSolvabilityValidator().validate(candidate).is_valid

def test_manhattan_assessor_returns_normalized_score() -> None:
    candidate = ReverseShuffleFifteenGenerator(seed=42, iterations=80).generate(make_request())[0]
    report = FifteenManhattanDifficultyAssessor().assess(candidate)
    assert 0.0 <= report.score <= 1.0
