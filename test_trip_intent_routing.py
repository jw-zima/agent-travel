from agent.core import detect_search_scope


def test_detects_flight_only_request():
    scope = detect_search_scope("Find me flights from WAW to FCO on 2026-09-15")
    assert scope == "flights"


def test_detects_hotel_only_request():
    scope = detect_search_scope("Find me hotels in Rome from 2026-09-15 to 2026-09-18")
    assert scope == "hotels"


def test_detects_both_request():
    scope = detect_search_scope("Find me flights and hotels for Warsaw to Rome from 2026-09-15 to 2026-09-18")
    assert scope == "both"


def test_defaults_to_both_when_request_is_ambiguous():
    scope = detect_search_scope("Plan my trip to Rome")
    assert scope == "both"
