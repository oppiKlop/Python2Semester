from dataclasses import dataclass, field


@dataclass
class ChatContext:
    limit_message: int | None
    limit_chars: int | None
    messages: list[dict[str, str]] = field(default_factory=list)

    def _total_chars(self, messages: list[dict[str, str]]) -> int:
        return sum(len(msg['content']) for msg in messages)

    def _trim_by_message_count(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        if self.limit_message is None:
            return messages
        while len(messages) > self.limit_message:
            messages.pop(0)
        return messages

    def _trim_by_char_count(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        if self.limit_chars is None:
            return messages
        while messages and self._total_chars(messages) > self.limit_chars:
            if len(messages) == 1:
                excess = self._total_chars(messages) - self.limit_chars
                messages[0]['content'] = messages[0]['content'][excess:]
                break
            messages.pop(0)
        return messages

    def prepare_with_user_message(self, content: str) -> list[dict[str, str]]:
        pending = [*self.messages, {'role': 'user', 'content': content}]
        pending = self._trim_by_message_count(pending)
        pending = self._trim_by_char_count(pending)
        return pending

    def add_user_message(self, content: str) -> None:
        self.messages = self.prepare_with_user_message(content)

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({'role': 'assistant', 'content': content})
        self.messages = self._trim_by_message_count(self.messages)
        self.messages = self._trim_by_char_count(self.messages)

    def reset(self) -> None:
        self.messages.clear()
