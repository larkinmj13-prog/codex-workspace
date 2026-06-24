from stockgod.data.config import load_provider_config


def test_provider_config_loads_env_without_requiring_keys():
    config = load_provider_config({"MARKET_DATA_PROVIDER": "massive", "YAHOO_FALLBACK_ENABLED": "false"})
    assert config.market_data_provider == "massive"
    assert config.massive_api_key == ""
    assert config.yahoo_fallback_enabled is False


def test_provider_config_strips_whitespace_from_secrets():
    config = load_provider_config({
        "FMP_API_KEY": "  abc123\n",
        "MASSIVE_API_KEY": "def456\t",
        "FRED_API_KEY": "\n ghi789 ",
        "SEC_USER_AGENT": " Michael app@example.com \n",
    })
    assert config.fmp_api_key == "abc123"
    assert config.massive_api_key == "def456"
    assert config.fred_api_key == "ghi789"
    assert config.sec_user_agent == "Michael app@example.com"
