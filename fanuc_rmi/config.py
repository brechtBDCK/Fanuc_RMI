import tomllib
from pathlib import Path


def load_config(path: str = "config.toml") -> dict:
    config_path = Path(path)
    with config_path.open("rb") as file:
        return tomllib.load(file)
