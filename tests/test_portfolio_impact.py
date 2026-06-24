from stockgod.analysis.portfolio_impact import analyze_portfolio_impact


def test_missing_holdings_returns_limited_analysis():
    result = analyze_portfolio_impact({"ticker": "NVDA", "standalone_signal": "Buy Setup"})
    assert result["portfolio_read"] == "limited"
    assert result["diversification_benefit"] == "unknown"


def test_concentrated_sector_returns_size_smaller_or_watch():
    result = analyze_portfolio_impact({
        "ticker": "NVDA",
        "standalone_signal": "Buy Setup",
        "sector": "Technology",
        "factor_exposures": ["growth", "ai"],
        "holdings": [{"ticker": "MSFT", "weight": 0.2, "sector": "Technology", "factor_exposures": ["growth"]}],
    })
    assert result["portfolio_read"] in {"size_smaller", "watch"}
    assert result["concentration_flags"]


def test_risk_gate_active_returns_avoid():
    result = analyze_portfolio_impact({"standalone_signal": "Buy Setup", "risk_gate": "capped44", "holdings": [{"ticker": "A", "weight": 0.01}]})
    assert result["portfolio_read"] == "avoid"
    assert result["sizing_implication"] == "avoid_new_money"


def test_attractive_standalone_no_concentration_can_add():
    result = analyze_portfolio_impact({
        "ticker": "NVDA",
        "standalone_signal": "Buy Setup",
        "sector": "Technology",
        "factor_exposures": ["ai"],
        "holdings": [{"ticker": "JNJ", "weight": 0.04, "sector": "Healthcare", "factor_exposures": ["defensive"]}],
    })
    assert result["portfolio_read"] == "add"
    assert result["sizing_implication"] == "normal"


def test_output_separates_standalone_from_portfolio_read():
    result = analyze_portfolio_impact({"standalone_signal": "Buy Setup"})
    assert result["standalone_read"] == "Buy Setup"
    assert "portfolio_read" in result
