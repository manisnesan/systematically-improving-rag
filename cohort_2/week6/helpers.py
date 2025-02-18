from pydantic import BaseModel, field_validator, ValidationInfo, computed_field
import json


class Command(BaseModel):
    extension_name: str
    command_name: str
    command_description: str

    @computed_field
    def key(self) -> str:
        return f"{self.extension_name}.{self.command_name}"


class UserCommandArgument(BaseModel):
    title: str
    value: str


class UserCommand(BaseModel):
    key: str
    arguments: list[UserCommandArgument]


class SelectedCommands(BaseModel):
    selected_commands: list[UserCommand]

    @field_validator("selected_commands")
    def validate_selected_commands(cls, v, info: ValidationInfo):
        commands: list[Command] = info.context["commands"]
        valid_command_keys = [command.key for command in commands]
        invalid_keys = [
            command.key for command in v if command.key not in valid_command_keys
        ]
        if invalid_keys:
            raise ValueError(
                f"Commands {invalid_keys} are not valid commands. Valid commands that can be used are {valid_command_keys}"
            )

        if len(v) > 4:
            raise ValueError(
                f"{len(v)} commands selected, maximum is 4. Please reduce the number of commands selected to 4."
            )

        return v


def calculate_precision(model_tool_call, expected_tool_call):
    """
    Calculate precision: (true positives) / (true positives + false positives)
    Precision = (relevant tools called) / (total tools called)
    """
    if len(model_tool_call) == 0:
        return 0.0  # Changed from 1 since no tools called means no true positives

    relevant_results = sum(1 for tool in model_tool_call if tool in expected_tool_call)
    return round(relevant_results / len(model_tool_call), 2)


def calculate_recall(model_tool_call, expected_tool_call):
    """
    Calculate recall: (true positives) / (true positives + false negatives)
    Recall = (relevant tools called) / (total relevant tools)
    """
    if len(expected_tool_call) == 0:
        return 1.0  # Perfect recall if no tools were expected

    if len(model_tool_call) == 0:
        return 0.0  # No recall if no tools were called

    relevant_results = sum(1 for tool in expected_tool_call if tool in model_tool_call)
    return round(relevant_results / len(expected_tool_call), 2)


def load_commands(file_path: str) -> list[Command]:
    with open(file_path, "r") as file:
        return [
            Command(
                extension_name=command["extension_name"],
                command_name=command["source_name"],
                command_description=command["description"],
            )
            for command in json.load(file)
        ]


def load_queries(commands: list[Command], query_path: str):
    valid_commands = set(command.key for command in commands)
    with open(query_path, "r") as f:
        queries = [json.loads(line) for line in f]
        for query in queries:
            for label in query["labels"]:
                if label not in valid_commands:
                    raise ValueError(f"Command {label} not found in commands")
    return queries
