from stockgod.data.config import load_provider_config


def test_provider_config_loads_env_without_requiring_keys():
    config = load_provider_config({"MARKET_DATA_PROVIDER": "massive", "YAHOO_FALLBACK_ENABLED": "false"})
    assert config.market_data_provider == "massive"
    assert config.massive_api_key == ""
    assert config.yahoo_fallback_enabled is False
