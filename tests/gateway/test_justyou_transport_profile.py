"""JustYou binds transport credential identity rather than routed runtime profile."""
import sqlite3
from pathlib import Path
from types import SimpleNamespace as N

from gateway.justyou_identity import annotate_admitted_event
from gateway.session_identity import RoutingIdentity


def _event(transport, runtime):
    source=N(platform=N(value="telegram"), user_id="u1", profile=runtime)
    source._identity=RoutingIdentity(
        transport_profile=transport, runtime_profile=runtime,
        authorization_home=Path("/tmp"), runtime_home=Path("/tmp"),
    )
    return N(source=source, metadata={}, internal=False)


def test_routed_runtime_uses_receiving_transport_scope(tmp_path):
    db=tmp_path/"bindings.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE bindings (binding_id INTEGER PRIMARY KEY,channel TEXT,scope TEXT,address TEXT,principal_id TEXT,relationship_id TEXT,active INTEGER)")
        conn.execute("INSERT INTO bindings VALUES (1,'telegram','default','u1','njaal',NULL,1)")
    routed=_event("default","valomarket")
    assert annotate_admitted_event(routed,db)
    assert routed.metadata["justyou_identity_candidate_v1"]["principal_id"]=="njaal"
    assert not annotate_admitted_event(_event("secondary","valomarket"),db)
