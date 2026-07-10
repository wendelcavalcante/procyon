from procyon.persistence.sqlite import (
    SQLiteConnectionFactory,
    SQLitePlayerStateRepository,
    initialize_sqlite_database,
)
from procyon.player_modeling.types import PlayerModelState


def test_sqlite_player_state_roundtrip(tmp_path) -> None:
    database_path = tmp_path / "procyon_test.sqlite3"
    factory = SQLiteConnectionFactory(database_path)
    initialize_sqlite_database(factory)

    repository = SQLitePlayerStateRepository(factory)

    state = PlayerModelState(
        skill=0.7,
        engagement=0.6,
        frustration=0.2,
        confidence=0.5,
        observations_count=3,
        metadata={"profile": "test"},
    )

    repository.save("player_001", state)

    loaded = repository.get("player_001")

    assert loaded is not None
    assert loaded.skill == 0.7
    assert loaded.engagement == 0.6
    assert loaded.frustration == 0.2
    assert loaded.confidence == 0.5
    assert loaded.observations_count == 3
    assert loaded.metadata["profile"] == "test"