import json


def test_load_missing_file(state_store):
    assert state_store.load() == ""


def test_load_reads_existing(state_store):
    state_store.path.write_text(json.dumps({"last_ip": "1.2.3.4"}))
    assert state_store.load() == "1.2.3.4"


def test_load_corrupt_json(state_store):
    state_store.path.write_text("not json{{{")
    assert state_store.load() == ""


def test_save_writes_correctly(state_store):
    state_store.save("1.2.3.4")
    assert json.loads(state_store.path.read_text()) == {"last_ip": "1.2.3.4"}


def test_save_is_atomic(state_store):
    """Temp file must not linger after a successful save."""
    state_store.save("1.2.3.4")
    assert not state_store.path.with_suffix(".tmp").exists()
