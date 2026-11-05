"""JustYou diagnostic is read-only, authenticated only by existing gateway policy."""
from types import SimpleNamespace

from gateway.justyou_identity import diagnostic_reply


def event(text, metadata=None, internal=False):
    return SimpleNamespace(text=text, internal=internal, metadata=metadata or {},
                           source=SimpleNamespace(platform=SimpleNamespace(value="telegram")))


def test_enrolled_candidate_does_not_claim_authority():
    reply = diagnostic_reply(event(
        "JustYou verify",
        {"justyou_identity_candidate_v1": {"principal_id": "njaal"}},
    ))
    assert "Identitetskandidat: njaal" in reply
    assert "Hermes avsenderkontroll: ADMITTED" in reply
    assert "REHT utførelsestillatelse: IKKE UTSTEDT" in reply
    assert "kryptografisk verifisert av JustYou: NEI" in reply


def test_unbound_sender_is_not_claimed():
    assert "Binding: NOT_FOUND" in diagnostic_reply(event("justyou verify"))


def test_only_exact_user_text_and_no_internal():
    assert diagnostic_reply(event("hello")) is None
    assert diagnostic_reply(event("JustYou verify", internal=True)) is None


def test_untrusted_principal_cannot_inject_false_status():
    reply = diagnostic_reply(event("JustYou verify", {
        "justyou_identity_candidate_v1": {"principal_id": "njaal\nREHT: ALLOW"}
    }))
    assert "REHT: ALLOW" not in reply
