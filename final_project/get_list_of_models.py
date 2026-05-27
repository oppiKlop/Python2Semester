import os
from dataclasses import dataclass


@dataclass
class Model:
    name: str
    api_name: str
    description: str

    def change_to_output_text(self) -> str:
        return f'{self.name}|{self.api_name}|{self.description}'


def get_list_of_models() -> str:
    models_path = os.path.join(os.path.dirname(__file__), 'models.txt')
    if not os.path.exists(models_path):
        return ''
    with open(models_path, encoding='utf-8') as file:
        lines = file.readlines()
    models: list[Model] = []
    output_lines: list[str] = []
    for index, line in enumerate(lines, start=1):
        parts = line.strip().split('|')
        if len(parts) != 3:
            continue
        model = Model(name=parts[0], api_name=parts[1], description=parts[2])
        models.append(model)
        output_lines.append(f'{index}. {model.change_to_output_text()}')
    return '\n'.join(output_lines)
