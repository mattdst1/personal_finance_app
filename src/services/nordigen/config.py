from dataclasses import dataclass, field
import os

from dotenv import load_dotenv
from loguru import logger
from pathlib import Path

import utils


URL_PREFIX = "https://bankaccountdata.gocardless.com/api/v2"


def get_credentials(env_path: str = ".env") -> tuple[str, str]:
    load_dotenv(env_path)
    secret_id = os.environ["nordigen_id"]
    secret_key = os.environ["nordigen_key"]
    return secret_id, secret_key


@dataclass
class Config:
    config_filepath: Path = Path("./config.yaml")
    requisition_id: str = field(init=False)
    nordigen_id: str = field(init=False)
    nordigen_key: str = field(init=False)
    account_mapping: dict = field(init=False)
    institution_id: str = field(init=False)
    env_path: str = ".env"

    def __post_init__(self):
        logger.debug(f"loading config from {self.config_filepath}")
        if isinstance(self.config_filepath, str):
            self.config_filepath = Path(self.config_filepath)
        if not self.config_filepath.is_file():
            raise FileNotFoundError()

        logger.debug(f"config exists: {Path(self.config_filepath).is_file()}")
        config = utils.read_yaml(self.config_filepath)
        try:
            self.requisition_id = config["tokens"]["requisition_id"]
            self.account_mapping = config["account_mapping"]
            self.institution_id = config["institution"]["id"]
        except Exception as e:
            logger.error(f"Failed to get nordigen customer mapping")
            # raise e

        env_path = Path(self.env_path)
        logger.debug(f".env exists: {env_path.is_file()}")
        try:
            self.nordigen_id, self.nordigen_key = get_credentials(env_path=env_path)
        except Exception as e:
            logger.error(f"Failed to set credentials from .env")
            raise e


def transactions_endpoint(account_id):
    # return f"https://ob.nordigen.com/api/v2/accounts/{account_id}/transactions/"
    return f"{URL_PREFIX}/accounts/{account_id}/transactions"


def details_endpoint(account_id):
    return f"{URL_PREFIX}/accounts/{account_id}/details/"
    # return f"https://ob.nordigen.com/api/v2/accounts/{account_id}/details/"


def balances_endpoint(account_id):
    return f"{URL_PREFIX}/accounts/{account_id}/balances/"
    # return f"https://ob.nordigen.com/api/v2/accounts/{account_id}/balances/"
