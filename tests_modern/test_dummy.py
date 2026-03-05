def test_snapshot_smoke(snapshot):
    # Arrange
    payload = {
        "message": "modern test suite initialized",
        "status": "ok",
        "tools": ["pytest", "syrupy"],
    }

    # Act
    serialized_payload = payload

    # Assert
    assert serialized_payload == snapshot
