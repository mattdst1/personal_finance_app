from pathlib import Path

from services.nordigen import account_api, config


async def fetch_all_data(config_filepath: Path = "./config_2023_december.yaml"):
    if not config_filepath.is_file():
        raise FileNotFoundError(f"{config_filepath} not found")

    config_object = config.Config(config_filepath="./config_2023_december.yaml")
    data = await account_api.fetch_all_nordigen_data(config_object)
    return data
