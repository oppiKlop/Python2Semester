import os
from dataclasses import dataclass
from pathlib import Path

import yaml

CONFIG_FILE = Path(__file__).resolve().parent / 'config.yaml'


@dataclass
class AppConfig:
    api_key: str
    temperature: float
    limit_message: int | None
    limit_chars: int | None
    system_prompt: str | None
    model: str


def _parse_int(value: str | int | None, name: str) -> int | None:
    if value is None or value == '':
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'Некорректное значение {name}: {value!r}') from exc


def _parse_float(value: str | float | None, name: str) -> float:
    if value is None or value == '':
        raise ValueError(f'Не задан обязательный параметр {name}')
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'Некорректное значение {name}: {value!r}') from exc
    if not 0 <= result <= 1:
        raise ValueError(f'{name} должен быть от 0 до 1, получено: {result}')
    return result


def _load_yaml() -> dict[str, object]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with CONFIG_FILE.open(encoding='utf-8') as file:
            data = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise ValueError(f'Некорректный YAML в {CONFIG_FILE.name}: {exc}') from exc
    except OSError as exc:
        raise ValueError(f'Не удалось прочитать {CONFIG_FILE.name}: {exc}') from exc
    return data if isinstance(data, dict) else {}


def _get_value(env_name: str, yaml_data: dict[str, object], yaml_key: str) -> str | None:
    env_value = os.environ.get(env_name)
    if env_value is not None and env_value != '':
        return env_value
    yaml_value = yaml_data.get(yaml_key)
    if yaml_value is None:
        return None
    return str(yaml_value)


def load_config() -> AppConfig | None:
    yaml_data = _load_yaml()
    has_env = any(
        os.environ.get(name)
        for name in ('API_KEY', 'LIMIT_MESSAGE', 'LIMIT_CHARS', 'TEMPERATURE', 'MODEL')
    )
    has_yaml = CONFIG_FILE.exists()

    if not has_env and not has_yaml:
        return None

    api_key = _get_value('API_KEY', yaml_data, 'api_key')
    temperature_raw = _get_value('TEMPERATURE', yaml_data, 'temperature')
    limit_message_raw = _get_value('LIMIT_MESSAGE', yaml_data, 'limit_message')
    limit_chars_raw = _get_value('LIMIT_CHARS', yaml_data, 'limit_chars')
    model = _get_value('MODEL', yaml_data, 'model') or 'gemini-2.5-flash'

    if not api_key:
        raise ValueError(
            'Укажите api_key через переменную окружения API_KEY '
            'или в config.yaml (api_key).',
        )

    system_prompt = yaml_data.get('system_prompt')
    if system_prompt is not None:
        system_prompt = str(system_prompt).strip() or None

    return AppConfig(
        api_key=api_key,
        temperature=_parse_float(temperature_raw, 'temperature'),
        limit_message=_parse_int(limit_message_raw, 'limit_message'),
        limit_chars=_parse_int(limit_chars_raw, 'limit_chars'),
        system_prompt=system_prompt,
        model=model,
    )
