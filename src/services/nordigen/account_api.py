import asyncio
import os

import aiohttp
from loguru import logger
from pathlib import Path

# nordigen components
from nordigen import NordigenClient
from nordigen.types.types import Requisition
from services.nordigen import config
import utils


class CustomAccountApi:
    def __init__(self, access_token: str, account_id: str):
        logger.debug(f"Initialising API")
        self.access_token = access_token
        self.account_id = account_id

    async def get_transactions(self):
        logger.debug(f"Getting transactions for {self.account_id}")
        return await self.api_call(
            self.access_token,
            self.account_id,
            config.transactions_endpoint(self.account_id),
        )

    async def get_balances(self):
        logger.debug(f"Getting balances for {self.account_id}")
        return await self.api_call(
            self.access_token,
            self.account_id,
            config.balances_endpoint(self.account_id),
        )

    async def get_metadata(self):
        logger.debug(f"Getting account metadata for {self.account_id}")

    @staticmethod
    async def api_call(access_token, account_id, url: str):
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
            logger.debug(f"completed acc {account_id}, {url}")
            return data


def initialise_client() -> NordigenClient:
    """
    return: Gets an initialised and credentialed Nordigen client
    """
    # get dev credentials

    # intialise client
    client = NordigenClient(
        secret_id=os.environ.get("nordigen_id"),
        secret_key=os.environ.get("nordigen_key"),
    )

    # exchange token
    token_data = client.generate_token()
    new_token = client.exchange_token(token_data["refresh"])

    # logger.debug(f"new token: {new_token}")
    # logger.debug(f"refresh: {token_data['refresh']}")
    return client


def get_requisition(requisition_id: str) -> Requisition:
    """
    return: a Nordigen Requisition
    """
    client = initialise_client()
    return client.requisition.get_requisition_by_id(requisition_id=requisition_id)


async def fetch_account_data(account_id, client):
    """
    Fetch account transactions and balances from Nordigen API for a given account ID.

    Args:
        account_id (str): The account ID to fetch data for.
        api_client (nordigen_api.NordigenClient): The initialized Nordigen API client.

    Returns:
        list: A list containing the account_id and the results (transactions and balances).
    """
    accounts_api = CustomAccountApi(client.token, account_id)
    transactions_and_balances = await asyncio.gather(
        accounts_api.get_transactions(), accounts_api.get_balances()
    )
    return [account_id, transactions_and_balances]


async def fetch_all_nordigen_data(requisition_id: str):
    """
    Fetch data for all accounts from Nordigen API using an initialized Nordigen API client.

    Returns:
        dict: A dictionary containing the fetched data.
    """
    # main
    api_client: NordigenClient = initialise_client()
    requisition: Requisition = get_requisition(requisition_id=requisition_id)
    accounts = requisition.get("accounts")

    if not accounts:
        logger.warning("no accounts found")
        raise Exception("no accounts found")

    # fetch data for all accounts
    # event_loop = asyncio.get_event_loop()
    fetched_data = await asyncio.gather(
        *(
            fetch_account_data(account_id, api_client)
            for account_id in requisition["accounts"]
        ),
        # loop=event_loop,
    )

    return {"data": fetched_data}


def parse_data(data):
    """
    Parse the fetched data from Nordigen API.

    Args:
        data (dict): The fetched data from Nordigen API.

    Returns:
        dict: A dictionary containing the parsed data.
    """
    balance_data = {}
    transaction_data = {}
    for account_id, results in data["data"]:
        transactions, balances = results
        balance_data[account_id] = balances
        transaction_data[account_id] = transactions

    return balance_data, transaction_data


def fetch_account_details(account_ids) -> dict[str, dict]:
    client = initialise_client()
    account_details = {}
    for account_id in account_ids:
        account = client.account_api(id=account_id)
        # parent
        details = account.get_details()
        account_details[account_id] = details
    return account_details


def load_acount_details(account_ids: list[str], overwrite=False):
    account_details_path = Path("../data/fetched/accounts.json")
    if overwrite or not account_details_path.is_file():
        logger.debug("fetching account details")
        account_details_dict = fetch_account_details(account_ids)
        utils.save_data_to_json(account_details_dict, account_details_path)

    return utils.read_json(account_details_path)


def fetch_account_metadata(account_ids):
    client = initialise_client()
    metadata = {}
    for account_id in account_ids:
        account = client.account_api(id=account_id)
        # parent
        data = account.get_metadata()
        # missing metadata key in api
        metadata[account_id] = {"metadata": data}
    return metadata


def load_account_metadata(account_ids: list[str], overwrite=False):
    metadata_path = Path("../data/fetched/metadata.json")
    if overwrite or not metadata_path.is_file():
        logger.debug("fetching account metadata")
        metadata_dict = fetch_account_metadata(account_ids)
        utils.save_data_to_json(metadata_dict, metadata_path)
    return utils.read_json(metadata_path)


async def load_latest_account_data(requisition_id, overwrite=False):
    path_balance = Path("../data/fetched/balances.json")
    path_transactions = Path("../data/fetched/transactions.json")

    if overwrite or (not path_balance.is_file() and not path_transactions.is_file()):
        logger.debug("fetching account data")

        data = await fetch_all_nordigen_data(requisition_id=requisition_id)
        balance_data, transaction_data = parse_data(data)
        utils.save_data_to_json(balance_data, path_balance)
        utils.save_data_to_json(transaction_data, path_transactions)

    return utils.read_json(path_balance), utils.read_json(path_transactions)


def load_requisition(requisition_id) -> dict:
    requisition_filepath = Path("../data/fetched/requisition.json")
    if not requisition_filepath.is_file():
        logger.debug("fetching requisition")
        requisition = {requisition_id: get_requisition(requisition_id)}
        utils.save_data_to_json(requisition, requisition_filepath)
    else:
        logger.debug("requisition already fetched")
    return utils.read_json(requisition_filepath)


async def get_latest_data(requisition_id: str):
    def get_output_filepath():
        output_directory = Path("../data/fetched")
        output_path = output_directory / f"{utils.today()}_data.json"
        return output_path

    if get_output_filepath().is_file():
        # do not requery today's data
        logger.info("today's data exists")
        return get_output_filepath()

    # get requisition
    requisition = load_requisition(requisition_id=requisition_id)
    account_ids = requisition.get(requisition_id, {}).get("accounts", [])

    if not account_ids:
        raise ValueError("no accounts found")

    # get static data
    account_details_dict = load_acount_details(account_ids=account_ids, overwrite=False)
    account_metadata_dict = load_account_metadata(
        account_ids=account_ids, overwrite=False
    )

    # load dynamic data for account
    (
        account_balances_dict,
        account_transactions_dict,
    ) = await load_latest_account_data(requisition_id=requisition_id, overwrite=True)

    # try:
    # package data
    data = {
        id: {
            **account_details_dict[id],
            **account_transactions_dict[id],
            **account_balances_dict[id],
            **account_metadata_dict[id],
        }
        for id in account_ids
    }

    # save
    utils.save_data_to_json(data, get_output_filepath())
    return get_output_filepath()

    # except Exception as e:
    #     logger.error(e)
    #     return (
    #         requisition,
    #         account_metadata_dict,
    #         account_balances_dict,
    #         account_transactions_dict,
    #         account_details_dict,
    #     )
