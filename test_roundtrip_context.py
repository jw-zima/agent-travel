from agent.core import extract_trip_context, detect_user_language


def test_extract_trip_context_detects_round_trip():
    text = (
        "Chcę zaplanować weekendowy wyjazd z Warszawy (WAW) do Rzymu (FCO) "
        "na daty od 2026-09-15 do 2026-09-18."
    )

    context = extract_trip_context(text)

    assert context["is_round_trip"] is True
    assert context["origin"] == "WAW"
    assert context["destination"] == "FCO"
    assert context["outbound_date"] == "2026-09-15"
    assert context["return_date"] == "2026-09-18"


def test_extract_trip_context_handles_non_round_trip():
    context = extract_trip_context("Chcę polecieć z WAW do FCO na 2026-09-15.")

    assert context["is_round_trip"] is False
    assert context["origin"] == "WAW"
    assert context["destination"] == "FCO"
    assert context["outbound_date"] == "2026-09-15"
    assert context["return_date"] is None


def test_detect_user_language_prefers_polish_for_polish_queries():
    assert detect_user_language("Chcę zaplanować wyjazd do Rzymu") == "polish"


def test_detect_user_language_defaults_to_english_for_english_queries():
    assert detect_user_language("Plan a trip to Rome") == "english"
