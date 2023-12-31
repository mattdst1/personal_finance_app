from dataclasses import dataclass
import dataclasses
import datetime
from enum import Enum
from copy import copy

from dotenv import load_dotenv

load_dotenv("user.env")

BOOKED_TRANSACTION = "booked"
PENDING_TRANSACTION = "pending"


# Transaction class
@dataclass
class Transaction:
    booking_date: str = None
    booking_date_time: str = None
    remittance_information_unstructured: str = None
    proprietary_bank_transaction_code: str = None
    amount: float = None
    transaction_currency: str = None
    status: str = None
    transaction_id: str = None
    internal_transaction_id: str = None
    account_id: str = None
    account_type: str = None
    account_name: str = None
    creditor_name: str = None
    debtor_name: str = None
    merchant_category_code: str = None
    currency: str = None
    instructed_amount: float = None
    instructed_currency: str = None
    source_currency: str = None
    exchange_rate: float = None
    unit_currency: str = None
    target_currency: str = None
    quotation_date: str = None
    value_date: str = None
    value_date_time: str = None

    def enforce_types(self):
        # convert str to float
        if self.amount:
            self.amount = float(self.amount)
        if self.instructed_amount:
            self.instructed_amount = float(self.instructed_amount)
        if self.exchange_rate:
            self.exchange_rate = float(self.exchange_rate)

        # convert str to datetime, if not None
        if isinstance(self.booking_date, str):
            self.booking_date = datetime.datetime.strptime(
                self.booking_date, "%Y-%m-%d"
            ).date()
        if isinstance(self.value_date, str):
            self.value_date = datetime.datetime.strptime(
                self.value_date, "%Y-%m-%d"
            ).date()

        if isinstance(self.value_date_time, str):
            self.value_date_time = datetime.datetime.strptime(
                self.value_date_time, "%Y-%m-%dT%H:%M:%SZ"
            ).date()
        if isinstance(self.booking_date_time, str):
            self.booking_date_time = datetime.datetime.strptime(
                self.booking_date_time, "%Y-%m-%dT%H:%M:%SZ"
            ).date()

        if isinstance(self.quotation_date, str):
            self.quotation_date = datetime.datetime.strptime(
                self.quotation_date, "%Y-%m-%dT%H:%M:%SZ"
            ).date()

    def __post_init__(self):
        self.enforce_types()

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    # return as dict
    def to_dict(self):
        # datetime to str
        if self.booking_date:
            self.booking_date = self.booking_date.strftime("%Y-%m-%d")
        if self.value_date:
            self.value_date = self.value_date.strftime("%Y-%m-%d")
        if self.quotation_date:
            self.quotation_date = datetime.strptime(
                self.quotation_date, "%Y-%m-%dT%H:%M:%SZ"
            ).date()
        if self.value_date_time:
            self.value_date_time = self.value_date_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        if self.booking_date_time:
            self.booking_date_time = self.booking_date_time.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )

        # remove None values
        return copy(self.__dict__)


class Account:
    def __init__(
        self,
        account_name: str,
        account_type: str,
        currency: str,
        reference_date: str = None,
        interim_available_balance: float = None,
        interim_booked_balance: float = None,
        account_id: str = None,
        forward_available_balance: float = None,
        opening_cleared_balance: float = None,
        previously_closed_booked_balance: float = None,
        masked_pan: str = None,
    ):
        self.account_name = account_name
        self.account_id = account_id
        self.account_type = account_type
        self.interim_available = interim_available_balance
        self.currency = currency
        self.reference_date = reference_date
        self.interim_booked = interim_booked_balance
        self.forward_available = forward_available_balance
        self.opening_cleared = opening_cleared_balance
        self.previously_closed_booked = previously_closed_booked_balance
        self.masked_pan = masked_pan

        self.pending_transactions = []
        self.booked_transactions = []

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        dict_data = copy(self.__dict__)

        # turn each transaction into a dict
        dict_data["pending_transactions"] = [
            t.to_dict() for t in self.pending_transactions
        ]
        dict_data["booked_transactions"] = [
            t.to_dict() for t in self.booked_transactions
        ]
        return dict_data

    def __repr__(self):
        return f"Account='{self.account_name}' Id:={self.account_id} InterimBalance={self.interim_available} "

    def __str__(self) -> str:
        return f"Account: {self.account_name} Id: ({self.account_id}) Interim balance: {self.interim_available} "

    def add_transaction(self, transaction: Transaction):
        # check that account_id are same
        if transaction.account_id != self.account_id:
            raise ValueError(
                f"Transaction account_id {transaction.account_id} does not match account_id {self.account_id}"
            )

        # check transaction id: if exists, overwrite
        for t in self.pending_transactions:
            if t.transaction_id == transaction.transaction_id:
                self.pending_transactions.remove(t)
                break

        if transaction.status == BOOKED_TRANSACTION:
            self.booked_transactions.append(transaction)
        elif transaction:
            self.pending_transactions.append(transaction)
        else:
            raise ValueError(f"Transaction status {transaction.status} is not valid")

    def add_transactions(self, transactions: list):
        for transaction in transactions:
            self.add_transaction(transaction)


class User:
    def __init__(self):
        self.requisition_ids
        self.accounts = []

    def add_account(self, account: Account):
        self.accounts.append(account)

    def get_account(self, account_id: str):
        for account in self.accounts:
            if account.account_id == account_id:
                return account
