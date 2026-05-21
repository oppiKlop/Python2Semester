from config import load_config
from exceptions import TokenError


def get_llm_token() -> str:
    config = load_config()
    if config is None:
        raise TokenError(message='Конфигурация не найдена')
    return config.api_key
