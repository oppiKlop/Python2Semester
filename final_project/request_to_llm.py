from google import genai
from google.genai import types

from config import AppConfig
from exceptions import LLMServiceError


def _build_client(config: AppConfig) -> genai.Client:
    return genai.Client(api_key=config.api_key)


def _generate_config(config: AppConfig) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        system_instruction=config.system_prompt,
        temperature=config.temperature,
    )


def _to_gemini_contents(history: list[dict[str, str]]) -> list[types.Content]:
    role_map = {
        'user': 'user',
        'assistant': 'model',
    }
    contents: list[types.Content] = []
    for msg in history:
        contents.append(
            types.Content(
                role=role_map[msg['role']],
                parts=[types.Part.from_text(text=msg['content'])],
            ),
        )
    return contents


def _generate_text(
    client: genai.Client,
    *,
    model: str,
    contents: list[types.Content],
    config: types.GenerateContentConfig,
) -> str | None:
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )
    except KeyboardInterrupt:
        return None
    except Exception as exc:
        raise LLMServiceError(message='Ошибка при обращении к Gemini API (Turn On vPN)') from exc
    return response.text or ''


def request_chat_completion(config: AppConfig, history: list[dict[str, str]]) -> str | None:
    client = _build_client(config)
    return _generate_text(
        client,
        model=config.model,
        contents=_to_gemini_contents(history),
        config=_generate_config(config),
    )


def request_chunk_completion(
    config: AppConfig,
    user_prompt: str,
    chunk_text: str,
) -> str | None:
    client = _build_client(config)
    contents = [
        types.Content(
            role='user',
            parts=[types.Part.from_text(text=f'{user_prompt}\n\n{chunk_text}')],
        ),
    ]
    return _generate_text(
        client,
        model=config.model,
        contents=contents,
        config=_generate_config(config),
    )
