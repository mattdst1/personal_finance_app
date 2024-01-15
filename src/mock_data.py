from typing import Any
import dataclasses
import datetime
import utils

from pydantic import BaseModel, Field, Json

import model


def get_requisition() -> model.Requisition:
    requisition: dict[str, Any] = {
        "id": "738d03c6-96fe-4b9e-a10c-b5befb1d02c8",
        "created": "2023-12-25T09:33:37.022127Z",
        "redirect": "https://gocardless.com",
        "status": "LN",
        "institution_id": "SANTANDER_GB_ABBYGB2L",
        "agreement": "71321e76-07d3-4438-ad18-d600ce91438c",
        "reference": "073127d2-2018-4a4a-b47e-1170d8616228",
        "accounts": [
            "590300bd-3daf-4d5e-9274-7a3782261f7e",
            "d2ff77d0-6c80-4580-95a5-e3e87a098db9",
            "e9e5f8b9-da61-49ce-bdae-56546ce4a1c9",
        ],
        "link": "https://ob.nordigen.com/psd2/start/738d03c6-96fe-4b9e-a10c-b5befb1d02c8/SANTANDER_GB_ABBYGB2L",
        "ssn": None,
        "account_selection": False,
        "redirect_immediate": False,
    }
    return model.Requisition.model_validate(requisition)


def load_data():
    return utils.read_json(filepath="../data/api_output_sample.json"), get_requisition()


def get_mocked_data():
    def get_metadata() -> model.UserAccountMetadata:
        # as dicts
        joint_account_metadata = {
            "id": "590300bd-3daf-4d5e-9274-7a3782261f7e",
            "created": "2023-03-13T17:58:53.898557Z",
            "last_accessed": "2023-12-30T14:42:46.907297Z",
            "iban": "GB52ABBY09012921263671",
            "institution_id": "SANTANDER_GB_ABBYGB2L",
            "status": "READY",
            "owner_name": "",
        }

        credit_card_metadata = {
            "id": "d2ff77d0-6c80-4580-95a5-e3e87a098db9",
            "created": "2023-03-13T17:58:53.845197Z",
            "last_accessed": "2023-12-30T14:40:20.696724Z",
            "iban": "**4572",
            "institution_id": "SANTANDER_GB_ABBYGB2L",
            "status": "READY",
            "owner_name": "",
        }

        single_account_metadata = {
            "id": "e9e5f8b9-da61-49ce-bdae-56546ce4a1c9",
            "created": "2023-03-13T17:58:53.874184Z",
            "last_accessed": "2023-12-30T14:53:28.379568Z",
            "iban": "GB31ABBY09012916688559",
            "institution_id": "SANTANDER_GB_ABBYGB2L",
            "status": "READY",
            "owner_name": "",
        }

        # as objects
        joint_account_metadata = model.AccountMetadata.model_validate(
            joint_account_metadata
        )
        credit_card_metadata = model.AccountMetadata.model_validate(
            credit_card_metadata
        )
        single_account_metadata = model.AccountMetadata.model_validate(
            single_account_metadata
        )

        accounts = {
            "joint_account": joint_account_metadata,
            "credit_card": credit_card_metadata,
            "single_account": single_account_metadata,
        }
        account_metadata = model.UserAccountMetadata(accounts=accounts)
        return account_metadata

    def get_details() -> model.UserAccountDetails:
        # as dicts
        joint_account_details = {
            "account": {
                "resourceId": "cbc85e1c-cdbc-4e3a-9918-03b74d79e719",
                "bban": "09012921263671",
                "currency": "GBP",
                "name": "joint account",
                "cashAccountType": "CACC",
            }
        }
        credit_card_details = {
            "account": {
                "resourceId": "c4e9a964-b676-43c1-81f9-5479f8894604",
                "currency": "GBP",
                "cashAccountType": "CARD",
                "maskedPan": "**4572",
                "details": "STAFF ALL IN ONE CREDIT CARD",
            }
        }

        single_account_details = {
            "account": {
                "resourceId": "a2b51663-5cf3-43d6-866e-65e5c63542bc",
                "bban": "09012916688559",
                "currency": "GBP",
                "name": "single account",
                "cashAccountType": "CACC",
            }
        }
        # rename
        joint_account_details = utils.rename_keys(
            joint_account_details.get("account"),
            {
                "resourceId": utils.to_snake_case_with_dots("resourceId"),
                "bban": utils.to_snake_case_with_dots("bban"),
                "currency": utils.to_snake_case_with_dots("currency"),
                "name": utils.to_snake_case_with_dots("name"),
                "cashAccountType": utils.to_snake_case_with_dots("cashAccountType"),
            },
        )
        credit_card_details = utils.rename_keys(
            credit_card_details.get("account"),
            {
                "resourceId": utils.to_snake_case_with_dots("resourceId"),
                "currency": utils.to_snake_case_with_dots("currency"),
                "cashAccountType": utils.to_snake_case_with_dots("cashAccountType"),
                "maskedPan": utils.to_snake_case_with_dots("maskedPan"),
                "details": utils.to_snake_case_with_dots("details"),
            },
        )
        single_account_details = utils.rename_keys(
            single_account_details.get("account"),
            {
                "resourceId": utils.to_snake_case_with_dots("resourceId"),
                "bban": utils.to_snake_case_with_dots("bban"),
                "currency": utils.to_snake_case_with_dots("currency"),
                "name": utils.to_snake_case_with_dots("name"),
                "cashAccountType": utils.to_snake_case_with_dots("cashAccountType"),
            },
        )

        # as objects
        joint_account_details = model.CurrentAccountDetails.model_validate(
            joint_account_details
        )
        credit_card_details = model.CreditCardDetails.model_validate(
            credit_card_details
        )
        single_account_details = model.CurrentAccountDetails.model_validate(
            single_account_details
        )

        account_details = model.UserAccountDetails()
        account_details._add_credit_card(credit_card_details)
        account_details._add_current_account(joint_account_details)
        account_details._add_current_account(single_account_details)
        return account_details

    def get_balances():
        # as dict
        def get_balances(balance_data):
            return [model.Balance.model_validate(balance) for balance in balance_data]

        class BalanceAmount(BaseModel):
            amount: str
            currency: str

        class Balance(BaseModel):
            balance_amount: BalanceAmount
            balance_type: str
            reference_date: str

        joint_account_balances = {
            "balances": [
                {
                    "balanceAmount": {"amount": "3700.80", "currency": "GBP"},
                    "balanceType": "forwardAvailable",
                    "referenceDate": "2023-12-30",
                },
                {
                    "balanceAmount": {"amount": "-1195.39", "currency": "GBP"},
                    "balanceType": "openingCleared",
                    "referenceDate": "2023-12-30",
                },
                {
                    "balanceAmount": {"amount": "-710.84", "currency": "GBP"},
                    "balanceType": "previouslyClosedBooked",
                    "referenceDate": "2023-12-26",
                },
            ]
        }

        credit_card_balances = {
            "balances": [
                {
                    "balanceAmount": {"amount": "3700.80", "currency": "GBP"},
                    "balanceType": "forwardAvailable",
                    "referenceDate": "2023-12-30",
                },
                {
                    "balanceAmount": {"amount": "-1195.39", "currency": "GBP"},
                    "balanceType": "openingCleared",
                    "referenceDate": "2023-12-30",
                },
                {
                    "balanceAmount": {"amount": "-710.84", "currency": "GBP"},
                    "balanceType": "previouslyClosedBooked",
                    "referenceDate": "2023-12-26",
                },
            ]
        }

        single_account_balances = {
            "balances": [
                {
                    "balanceAmount": {"amount": "1023.14", "currency": "GBP"},
                    "balanceType": "interimAvailable",
                    "referenceDate": "2023-12-30",
                },
                {
                    "balanceAmount": {"amount": "1023.14", "currency": "GBP"},
                    "balanceType": "interimBooked",
                    "referenceDate": "2023-12-30",
                },
            ]
        }

        # rename

        joint_account_balances = utils.rename_keys(
            joint_account_balances.get("balances"),
            {
                "balanceAmount": utils.to_snake_case_with_dots("balanceAmount"),
                "balanceType": utils.to_snake_case_with_dots("balanceType"),
                "referenceDate": utils.to_snake_case_with_dots("referenceDate"),
            },
        )
        credit_card_balances = utils.rename_keys(
            credit_card_balances.get("balances"),
            {
                "balanceAmount": utils.to_snake_case_with_dots("balanceAmount"),
                "balanceType": utils.to_snake_case_with_dots("balanceType"),
                "referenceDate": utils.to_snake_case_with_dots("referenceDate"),
            },
        )
        single_account_balances = utils.rename_keys(
            single_account_balances.get("balances"),
            {
                "balanceAmount": utils.to_snake_case_with_dots("balanceAmount"),
                "balanceType": utils.to_snake_case_with_dots("balanceType"),
                "referenceDate": utils.to_snake_case_with_dots("referenceDate"),
            },
        )

        # as objects
        joint_account_balances = model.AccountBalances(
            balances=get_balances(joint_account_balances)
        )
        credit_card_balances = model.AccountBalances(
            balances=get_balances(credit_card_balances)
        )
        single_account_balances = model.AccountBalances(
            balances=get_balances(single_account_balances)
        )

        account_balances = model.UserAccountBalances(
            current_accounts=[single_account_balances, joint_account_balances],
            credit_cards=[credit_card_balances],
        )
        return account_balances

    def get_account_id_mapping():
        account_id_mapping = {
            "590300bd-3daf-4d5e-9274-7a3782261f7e": "joint account",
            "d2ff77d0-6c80-4580-95a5-e3e87a098db9": "STAFF ALL IN ONE CREDIT CARD",
            "e9e5f8b9-da61-49ce-bdae-56546ce4a1c9": "single account",
        }
        return account_id_mapping

    requisition = get_requisition()
    account_metadata = get_metadata()
    account_details = get_details()
    account_balances = get_balances()
    transactions_raw = utils.read_json("../data/output.json").get("data")
    # print(transactions_raw[0:1])
    # transactions = [
    #     model.Transaction.model_validate(transaction)
    #     for transaction in transactions_raw
    # ]

    account_id_mapping = get_account_id_mapping()

    user_data = model.UserData(
        requisition=requisition,
        account_metadata=account_metadata,
        account_details=account_details,
        account_balances=account_balances,
        # transactions=transactions_raw,
    )
    return user_data, transactions_raw, account_id_mapping
