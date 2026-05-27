import pytest

import config as config_module


@pytest.fixture(autouse=True)
def clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ('API_KEY', 'TEMPERATURE', 'LIMIT_MESSAGE', 'LIMIT_CHARS', 'MODEL'):
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def isolated_config(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setattr(config_module, 'CONFIG_FILE', tmp_path / 'config.yaml')


def test_load_config_from_env_without_api_host(
    monkeypatch: pytest.MonkeyPatch,
    isolated_config: None,
) -> None:
    monkeypatch.setenv('API_KEY', 'key')
    monkeypatch.setenv('TEMPERATURE', '0.5')

    config = config_module.load_config()

    assert config is not None
    assert config.api_key == 'key'
    assert config.temperature == 0.5


def test_load_config_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
    isolated_config: None,
) -> None:
    monkeypatch.setenv('TEMPERATURE', '0.5')

    with pytest.raises(ValueError):
        config_module.load_config()


def test_load_config_validates_temperature(
    monkeypatch: pytest.MonkeyPatch,
    isolated_config: None,
) -> None:
    monkeypatch.setenv('API_KEY', 'key')
    monkeypatch.setenv('TEMPERATURE', '2.0')

    with pytest.raises(ValueError):
        config_module.load_config()


def test_load_config_raises_value_error_for_invalid_yaml(
    monkeypatch: pytest.MonkeyPatch,
    isolated_config: None,
    tmp_path,
) -> None:
    config_path = tmp_path / 'config.yaml'
    config_path.write_text('api_key: [', encoding='utf-8')
    monkeypatch.setattr(config_module, 'CONFIG_FILE', config_path)

    with pytest.raises(ValueError):
        config_module.load_config()
