import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["LLM_PROVIDER"] = "mock"

from app.agent import _validate_and_ground, _turn_guidance, MAX_TURNS  # noqa: E402
from app.catalog import get_catalog  # noqa: E402


def test_drops_hallucinated_recommendation():
    catalog = get_catalog()
    raw = {
        "reply": "Here you go",
        "action": "recommend",
        "recommendations": [
            {"name": "Totally Made Up Test", "url": "https://www.shl.com/fake/", "test_type": "K"},
            {"name": catalog.items[0].name, "url": catalog.items[0].url, "test_type": "K"},
        ],
        "end_of_conversation": False,
    }
    result = _validate_and_ground(raw, catalog)
    assert len(result.recommendations) == 1
    assert result.recommendations[0].name == catalog.items[0].name


def test_truncates_to_ten():
    catalog = get_catalog()
    raw = {
        "reply": "Here you go",
        "action": "recommend",
        "recommendations": [
            {"name": a.name, "url": a.url, "test_type": a.test_type} for a in catalog.items[:15]
        ],
        "end_of_conversation": False,
    }
    result = _validate_and_ground(raw, catalog)
    assert len(result.recommendations) == 10


def test_matches_by_url_even_if_name_differs_slightly():
    catalog = get_catalog()
    item = catalog.items[0]
    raw = {
        "reply": "x",
        "action": "recommend",
        "recommendations": [{"name": "some other label", "url": item.url, "test_type": "K"}],
        "end_of_conversation": False,
    }
    result = _validate_and_ground(raw, catalog)
    assert len(result.recommendations) == 1
    assert result.recommendations[0].name == item.name  # canonicalized from catalog


def test_empty_reply_gets_fallback_text():
    catalog = get_catalog()
    raw = {"reply": "", "action": "clarify", "recommendations": [], "end_of_conversation": False}
    result = _validate_and_ground(raw, catalog)
    assert len(result.reply) > 0


def test_turn_guidance_forces_commitment_near_cap():
    guidance = _turn_guidance(MAX_TURNS)
    assert "MUST commit" in guidance


def test_turn_guidance_relaxed_early():
    guidance = _turn_guidance(1)
    assert "fine to clarify" in guidance


if __name__ == "__main__":
    import traceback

    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
