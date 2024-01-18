import re
from datetime import datetime
from loguru import logger
from typing import List
import math

import pandas as pd

DATE_STR_FORMAT = "%d%m%Y"
OUTPUT_DATE_STR_FORMAT = "%d %B %Y"
INPUT_DATE_STR_FORMAT = "%d/%m/%Y"

from enrich.mappings import DESCRIPTION, CODE, COUNTERPARTY, EMPLOYERS, CREDITOR_NAME


def postprocess_counterparty(counterparty: str) -> str:
    if counterparty is None:
        return "none"

    if isinstance(counterparty, str):
        pass
    else:
        raise TypeError(f"error: {counterparty}, {type(counterparty)}")
    if "*" in counterparty:
        return "".join(counterparty.split("*")[0].strip())

    else:
        return counterparty


def get_dates(input_string: str) -> List[str]:
    return re.findall(r"\d{2}/\d{2}/\d{4}", input_string)


def account_date(input_string: str, input_str_format) -> str:
    dates = get_dates(input_string)
    if len(dates) == 2:
        start_date = datetime.strptime(dates[0], input_str_format).strftime(
            OUTPUT_DATE_STR_FORMAT
        )
        end_date = datetime.strptime(dates[1], input_str_format).strftime(
            OUTPUT_DATE_STR_FORMAT
        )
        return start_date, end_date
    else:
        raise ValueError("Invalid date string")


def format_date(input_string, input_date_format: None or str = None):
    input_date_format = input_date_format or DATE_STR_FORMAT
    return datetime.strptime(input_string, input_date_format).strftime(
        OUTPUT_DATE_STR_FORMAT
    )


def parse_description_debit_payment_method(description: str) -> str:
    # Extract payment type
    if re.search("card payment", description):
        payment_method = "card"
    elif re.search("direct debit payment", description):
        payment_method = "direct_debit"
    elif re.search("cash withdrawal", description):
        payment_method = "cash_withdrawal"
    elif re.search("cheque deposit", description):
        payment_method = "cheque_deposit"
    elif re.search("standing order", description):
        payment_method = "standing_order"
    elif re.search("faster payment", description):
        payment_method = "transfer.fasterpayments"
    elif re.search("credit card paym", description):
        payment_method = "transfer"
    elif re.search("transfer to", description):
        payment_method = "transfer"
    elif re.search("faster payment", description):
        payment_method = "transfer.fasterpayments"
    elif re.search("bill payment to ", description):
        # assume that bill payment is a faster payment
        payment_method = "transfer.fasterpayments"

    else:
        return "none"
    return payment_method


def parse_description_credit_payment_method(description: str) -> str:
    # Extract payment type
    if re.search("bank giro", description):
        payment_method = "transfer.bankgiro"
    elif re.search("transfer", description):
        payment_method = "transfer.transfer"
    elif re.search("faster payments", description):
        payment_method = "transfer.fasterpayments"
    elif re.search("(cashback)", description):
        payment_method = "cash_back"
    elif re.search("interest paid", description):
        payment_method = "interest_paid"
    elif re.search("cheque deposit", description):
        payment_method = "cheque_deposit"
    else:
        return "none"
    return payment_method


def set_debit_counterparty_creditcard_payment(description: str):
    if description.lower() == "credit card payment".lower():
        return "own_account"


def set_debit_counterparty_transfer(description: str):
    pattern = re.search(r"transfer to\s(.*)", description)
    if pattern:
        return pattern.group(1)


def set_debit_counterparty(description: str):
    pattern = re.search(r"to\s+(.*?)\s+(reference|on|,|ref)", description)
    if pattern:
        return pattern.group(1)


def set_credit_counterparty(description: str):
    pattern = re.search(r"(?:from|ref.)\s+(.*?)\s+(?:reference|ref)", description)
    if pattern:
        return pattern.group(1)


def set_credit_counterparty_fasterpayments(description: str) -> str or None:
    pattern = re.search(r"(?:from|ref.)\s+(.*?)\s+(?:reference|ref)", description)
    if pattern:
        return pattern.group(1)

    pattern = re.search(r"from\s+(.+)", description)
    if pattern:
        return pattern.group(1)


def set_credit_counterparty_giro_credit(description: str) -> str or None:
    pattern = re.search(r"ref\s(.*),", description)
    if pattern:
        return pattern.group(1)


def reference_star(description: str):
    """
    Finds reference where it is split by the "*" character
    """
    description = description.replace("*", "_")
    result = re.search("_(.*) on", description)
    if result:
        return result.group(1)


def reference_comma(description: str, ref_str: str = None):
    """
    Finds the reference where the reference is after ref_str but before comma character ","
    """
    if ref_str is None:
        ref_str = "reference"
    description = description.replace(" ,", ",").split(",")[0]
    result = re.search(f"{ref_str} (.*)", description)
    if result:
        return result.group(1)


def reference_between(description: str, start_str: str = None, end_str: str = None):
    """
    Finds the reference between start str and end str
    """
    if start_str is None:
        start_str = "reference"

    if end_str is None:
        end_str = "on"

    result = re.search(f"{start_str} (.*) {end_str}", description)
    if result:
        return result.group(1)


def reference_after(description: str, start_str: str = None):
    """
    Finds the reference after start str
    """
    if start_str is None:
        start_str = "reference"

    result = re.search(f"{start_str} (.*)", description)
    if result:
        return result.group(1)


def set_credit_counterparty_fasterpayments(description: str) -> str or None:
    pattern = re.search(r"(?:from|ref.)\s+(.*?)\s+(?:reference|ref)", description)
    if pattern:
        return pattern.group(1)

    pattern = re.search(r"from\s+(.+)", description)
    if pattern:
        return pattern.group(1)


def set_debit_cacc_recurrent_transaction(text):
    pattern = r"\bat\s+(.*?)\sof\b"
    match = re.search(pattern, text)
    # last 3 chars are country code, clean
    if match:
        return match.group(1)[:-3]


def get_counterparty(row, account_type) -> str:
    def bank_transfer_debit(description: str):
        if description == "credit card payment":
            return "Matthew Stewart"
        if "transfer to" in description:
            return set_debit_counterparty_transfer(description)
        else:
            return set_debit_counterparty(description)

    if account_type == "CACC":
        counterparty_mapping = {
            "CASHBACK": lambda x: "santander",
            "CREDIT INTEREST": lambda x: "santander",
            "DEBIT CARD CASH WITHDRAWAL": lambda x: "cash withdrawal",
            "CHEQUE DEPOSIT": lambda x: "cheque unknown",
            "FASTER PAYMENT RECEIPT": lambda x: set_credit_counterparty_fasterpayments(
                x
            ),
            "PURCHASE - DOMESTIC": lambda x: set_debit_cacc_recurrent_transaction(x),
            "RECURRENT TRANSACTION": lambda x: set_debit_cacc_recurrent_transaction(x),
            "APPLE PAY IN-APP": lambda x: set_debit_cacc_recurrent_transaction(x),
            "BANK TRANSFER CREDIT": lambda x: set_credit_counterparty_giro_credit(x),
            "EXTERNAL DIRECT DEBIT": lambda x: set_debit_counterparty(x),
            "OTT DEBIT": lambda x: set_debit_counterparty(x),
            "OTT CREDIT": lambda x: set_credit_counterparty(x),
            "BANK TRANSFER DEBIT": lambda x: bank_transfer_debit(x),
            "ACCOUNT CANCELLATION CREDIT": lambda x: "account closure transfer",
        }

        payment_type = row[CODE]
        if payment_type in counterparty_mapping.keys():
            description = row[DESCRIPTION]
            return counterparty_mapping[payment_type](description)
        else:
            logger.warning(f"unknown proprietaryBankTransactionCode: {payment_type} ")
            return f"unknown"
    elif account_type == "CARD":
        creditor_name = row[CREDITOR_NAME]
        if creditor_name is None or creditor_name == "unknown":
            return "unknown"
        elif not isinstance(row[CREDITOR_NAME], str):
            creditor_name = row[CREDITOR_NAME]
            raise TypeError(f"{creditor_name}, type {type(creditor_name)}")
        else:
            return row[CREDITOR_NAME].lower()
    else:
        raise NotImplementedError()


def clean_counterparty(counterparty: str):
    stem_counterparty: List[str] = [
        "airbnb",
        "amazon",
        "aviva",
        "vinted",
        "spectator",
        "mcdonalds",
        "dunelm",
        "ikea",
    ]

    after_star_counterparty: List[str] = ["zpos", "paypal"]
    if counterparty is None:
        return "n/a"
    elif isinstance(counterparty, str):
        # return mapped
        for item in stem_counterparty:
            if item in counterparty:
                return item

        for item in after_star_counterparty:
            if item in counterparty:
                return counterparty.split("*")[1]
            else:
                pass

        # trim whitespace
        counterparty = " ".join(counterparty.split())
        return counterparty
    else:
        raise TypeError(
            f"invalid counterparty type: {type(counterparty)} {counterparty}"
        )


def add_counterparties(df: pd.DataFrame):
    # process current account
    df.loc[df.account_type == "CACC", "counterparty"] = (
        df.loc[df.account_type == "CACC"]
        .apply(get_counterparty, **{"account_type": "CACC"}, axis=1)
        .fillna("unknown")
    )

    # process current account
    df.loc[df.account_type == "CARD", "counterparty"] = (
        df.loc[df.account_type == "CARD"]
        .apply(get_counterparty, **{"account_type": "CARD"}, axis=1)
        .fillna("unknown")
    )

    # counterparty info
    df["counterparty"] = df["counterparty"].apply(clean_counterparty)

    return df
