import copy

import pandas as pd

import model
import utils


def parse_current_account_details(details):
    adjusted_details = copy.deepcopy(details)
    adjusted_details = utils.rename_keys(
        adjusted_details,
        {
            "resourceId": utils.to_snake_case_with_dots("resourceId"),
            "bban": utils.to_snake_case_with_dots("bban"),
            "currency": utils.to_snake_case_with_dots("currency"),
            "name": utils.to_snake_case_with_dots("name"),
            "cashAccountType": utils.to_snake_case_with_dots("cashAccountType"),
        },
    )
    adjusted_details = model.CurrentAccountDetails.model_validate(adjusted_details)
    return adjusted_details


def parse_card_details(details):
    adjusted_details = copy.deepcopy(details)
    adjusted_details = utils.rename_keys(
        adjusted_details,
        {
            "resourceId": utils.to_snake_case_with_dots("resourceId"),
            "currency": utils.to_snake_case_with_dots("currency"),
            "cashAccountType": utils.to_snake_case_with_dots("cashAccountType"),
            "maskedPan": utils.to_snake_case_with_dots("maskedPan"),
            "details": utils.to_snake_case_with_dots("details"),
        },
    )
    credit_card_details = model.CreditCardDetails.model_validate(adjusted_details)
    return credit_card_details


def parse_account_details(account_data):
    details = account_data.get("account")
    if details.get("cashAccountType") == "CACC":
        account_details = parse_current_account_details(details)
        return account_details

    if details.get("cashAccountType") == "CARD":
        card_details = parse_card_details(details)
        return card_details


def parse_metadata(data):
    account_metadata = model.AccountMetadata.model_validate(data.get("metadata"))
    return account_metadata


def parse_account_balances(account_data):
    def get_balances(balance_data: list[dict]):
        return {
            b.get(
                utils.to_snake_case_with_dots("balanceType")
            ): model.Balance.model_validate(b)
            for b in balance_data
        }

    balance_data = copy.deepcopy(account_data.get("balances"))
    balance_data = utils.rename_keys(
        balance_data,
        {
            "balanceAmount": utils.to_snake_case_with_dots("balanceAmount"),
            "balanceType": utils.to_snake_case_with_dots("balanceType"),
            "referenceDate": utils.to_snake_case_with_dots("referenceDate"),
        },
    )
    return model.AccountBalances(balances=get_balances(balance_data))


def parse_account_transactions(
    account_data, account_id, account_name=None, account_type=None
):
    """
    Process account level transactions where account_data = data.get(account_id)

    """
    account_transactions = account_data.get("transactions")
    booked = pd.json_normalize(account_transactions.get("booked"))
    pending = pd.json_normalize(account_transactions.get("pending"))
    if len(booked) != 0:
        booked["status"] = "booked"

    if len(pending) != 0:
        pending["status"] = "pending"
    df = pd.concat([booked, pending])
    df["account_id"] = account_id
    if account_type:
        df["account_type"] = account_type

    if account_name:
        df["account_name"] = account_name

    account_transactions = df.to_dict(orient="records")
    account_transactions = utils.clean_column_names(account_transactions)
    account_transactions = [
        model.Transaction(**element) for element in account_transactions
    ]
    return account_transactions
