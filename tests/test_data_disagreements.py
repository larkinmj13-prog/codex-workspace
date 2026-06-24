from stockgod.analysis.data_disagreements import detect_data_disagreements


def test_edgar_overrides_fmp_for_insider_code_conflict():
    alerts = detect_data_disagreements(
        {"provider": "fmp", "transaction_code": "P"},
        {"provider": "edgar", "transaction_code": "M"},
        "insider_verification",
    )
    assert alerts[0]["severity"] == "high"
    assert alerts[0]["resolved_value_source"] == "edgar"


def test_fmp_remains_primary_for_fundamentals_unless_conflict_severe():
    alerts = detect_data_disagreements(
        {"provider": "fmp", "forward_pe": 20},
        {"provider": "yahoo", "forward_pe": 27},
        "fundamentals",
    )
    assert alerts[0]["severity"] == "medium"
    assert alerts[0]["resolved_value_source"] == "fmp"


def test_price_timestamp_mismatch_creates_warning():
    alerts = detect_data_disagreements(
        {"provider": "massive", "price": 100, "timestamp": "2026-06-23T14:00:00Z"},
        {"provider": "yahoo", "price": 100.5, "timestamp": "2026-06-23T13:55:00Z"},
        "price",
    )
    assert any(alert["severity"] == "low" for alert in alerts)


def test_earnings_date_mismatch_inside_five_days_high_severity():
    alerts = detect_data_disagreements(
        {"provider": "fmp", "earnings_date": "2026-06-25", "within_5_days": True},
        {"provider": "yahoo", "earnings_date": "2026-07-02", "within_5_days": False},
        "earnings",
    )
    assert alerts[0]["severity"] == "high"
