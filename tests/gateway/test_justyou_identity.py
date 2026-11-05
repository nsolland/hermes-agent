"""JustYou candidate projection must never become admission or execution authority."""
import sqlite3
from types import SimpleNamespace

import pytest

from gateway.justyou_identity import annotate_admitted_event, annotate_if_configured


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "bindings.sqlite"
    con = sqlite3.connect(path)
    con.execute(
        "CREATE TABLE bindings (binding_id INTEGER PRIMARY KEY, channel TEXT, "
        "scope TEXT, address TEXT, principal_id TEXT, relationship_id TEXT, "
        "proof_ref TEXT, active INTEGER)"
    )
    con.execute(
        "INSERT INTO bindings VALUES (1,'telegram','default','u1','principal-1',"
        "'relation-1','proof:operator',1)"
    )
    con.commit()
    con.close()
    return path


def event(channel="telegram", scope="default", sender="u1", internal=False):
    source = SimpleNamespace(platform=SimpleNamespace(value=channel), profile=scope, user_id=sender)
    return SimpleNamespace(source=source, internal=internal, metadata={})


def test_enrolled_is_only_candidate(db):
    msg = event()
    assert annotate_admitted_event(msg, db)
    identity = msg.metadata["justyou_identity_candidate_v1"]
    assert identity["principal_id"] == "principal-1"
    assert identity["relationship_id"] == "relation-1"
    assert not identity["sender_authenticated"]
    assert not identity["execution_authorized"]


@pytest.mark.parametrize("kwargs", [
    {"channel": "signal"}, {"scope": "secondary"},
    {"sender": "attacker"}, {"internal": True},
])
def test_channels_profiles_and_internal_are_isolated(db, kwargs):
    msg = event(**kwargs)
    assert not annotate_admitted_event(msg, db)
    assert not msg.metadata


def test_revocation(db):
    con = sqlite3.connect(db)
    con.execute("UPDATE bindings SET active=0")
    con.commit()
    con.close()
    assert not annotate_admitted_event(event(), db)


def test_missing_configured_database_fails_closed(tmp_path):
    with pytest.raises(sqlite3.OperationalError):
        annotate_admitted_event(event(), tmp_path / "missing.sqlite")


def test_opt_in_disabled(monkeypatch):
    monkeypatch.delenv("JUSTYOU_COMM_BINDINGS_DB", raising=False)
    msg = event()
    assert not annotate_if_configured(msg)
    assert not msg.metadata
