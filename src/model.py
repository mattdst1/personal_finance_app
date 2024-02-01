from dataclasses import dataclass
import dataclasses
import datetime
from enum import Enum
from copy import copy, deepcopy
from collections import OrderedDict
from dotenv import load_dotenv

from numpy import isin
import pandas as pd
from pydantic import BaseModel, Field

load_dotenv("user.env")


class TransactionType:
    booked_transaction = "booked"
    pending_transaction = "pending"


# Transaction class
@dataclass
class Transaction:
    # from api
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

    # from enrichment
    booking_year: int = None
    booking_month: int = None
    flow: str = None
    counterparty: str = None
    category: str = None
    year_month: str = None

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
    def from_dict(cls, data, **kwargs):
        return cls(**data)

    # return as dict
    def to_dict(self):
        # datetime to str

        copy_class = copy(self)
        copy_class.enforce_types()

        if copy_class.booking_date:
            copy_class.booking_date = copy_class.booking_date.strftime("%Y-%m-%d")
        if copy_class.value_date:
            copy_class.value_date = copy_class.value_date.strftime("%Y-%m-%d")
        if copy_class.quotation_date:
            copy_class.quotation_date = copy_class.quotation_date.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            # copy_class.quotation_date = datetime.strptime(
            #     copy_class.quotation_date, "%Y-%m-%dT%H:%M:%SZ"
            # ).date()
        if copy_class.value_date_time:
            copy_class.value_date_time = copy_class.value_date_time.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        if copy_class.booking_date_time:
            copy_class.booking_date_time = copy_class.booking_date_time.strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )

        # remove None values
        return copy(copy_class.__dict__)


class AccountMetadata(BaseModel):
    id: str
    created: str
    last_accessed: str
    iban: str
    institution_id: str
    status: str
    owner_name: str


class UserAccountMetadata(BaseModel):
    accounts: dict[str, AccountMetadata] = Field(default_factory={})

    def add_account(self, account_id: str, account_metadata: AccountMetadata):
        self.accounts[account_id] = account_metadata


class Requisition(BaseModel):
    id: str
    created: str
    redirect: str
    accounts: list[str]
    status: str
    institution_id: str
    agreement: str
    reference: str
    link: str

    @property
    def expiry_date(self):
        # permissions expire 90 days after creation
        # need to turn created into datetime

        date = datetime.datetime.strptime(
            "2023-12-25T09:33:37.022127Z", "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        return date + datetime.timedelta(days=90)

    @property
    def link_expired(self):
        return datetime.datetime.now() > self.expiry_date

    @property
    def is_live(self):
        return not self.link_expired


def find_common_dicts(*lists):
    def dict_to_ordered_tuple(d):
        return tuple(OrderedDict(sorted(d.items())).items())

    sets = [set(dict_to_ordered_tuple(d) for d in lst) for lst in lists]

    common_set = set.intersection(*sets)

    result = [dict(t) for t in common_set]
    return result


class CurrentAccountDetails(BaseModel):
    """
    Model for current account details.

    Args:
        resource_id (str): The resource ID of the current account.
        bban (str): The BBAN of the current account.
        currency (str): The currency of the current account.
        name (str): The name of the current account.
        cash_account_type (str): The cash account type of the current account.
        account_id (str): The account ID of the current account (key from nordigen: data).
    """

    resource_id: str
    bban: str
    currency: str
    name: str
    cash_account_type: str
    account_id: str = Field(default_factory=lambda: None)


class CreditCardDetails(BaseModel):
    """
    Model for credit card details.

    Args:
        resource_id (str): The resource ID of the credit card.
        currency (str): The currency of the credit card.
        masked_pan (str): The masked PAN of the credit card.
        details (str): The details of the credit card (key from nordigen: data)..
    """

    resource_id: str
    currency: str
    masked_pan: str
    details: str
    account_id: str = Field(default_factory=lambda: None)
    cash_account_type: str = "CARD"


class UserAccountDetails(BaseModel):
    """
    Model for user account details.

    Args:
        credit_cards (dict[CreditCardDetails]): A dict of credit card details.
        current_accounts (dict[CurrentAccountDetails]): A dict of current account details.
    """

    credit_cards: dict[str, CreditCardDetails] = Field(default_factory=dict)
    current_accounts: dict[str, CurrentAccountDetails] = Field(default_factory=dict)

    def add_account(
        self, account_id, account: CurrentAccountDetails | CreditCardDetails
    ):
        if not isinstance(account, CurrentAccountDetails) and not isinstance(
            account, CreditCardDetails
        ):
            raise TypeError(
                "account must be of type CurrentAccountDetails or CreditCardDetails"
            )
        if isinstance(account, CurrentAccountDetails):
            account.account_id = account_id
            self._add_current_account(account_id, account)
        elif isinstance(account, CreditCardDetails):
            account.account_id = account_id
            self._add_credit_card(account_id, account)

    def _add_credit_card(self, account_id, credit_card: CreditCardDetails):
        if not isinstance(credit_card, CreditCardDetails):
            raise TypeError("credit_card must be of type CreditCardDetails")
        self.credit_cards[account_id] = credit_card

    def _add_current_account(self, account_id, current_account: CurrentAccountDetails):
        if not isinstance(current_account, CurrentAccountDetails):
            raise TypeError("current_account must be of type CurrentAccountDetails")
        self.current_accounts[account_id] = current_account

    def get_account_details_by_id(
        self, account_id: str
    ) -> CurrentAccountDetails | CreditCardDetails | None:
        account = self.current_accounts.get(account_id, None)
        if account:
            return account

        account = self.credit_cards.get(account_id, None)
        if account:
            return account

        return None

    def fetch_account_details_by_name(
        self, account_name: str
    ) -> CurrentAccountDetails | CreditCardDetails | None:
        for account in self.current_accounts.values():
            if account.name == account_name:
                return account

        for account in self.credit_cards.values():
            if account.name == account_name:
                return account

        return None


class BalanceAmount(BaseModel):
    amount: str
    currency: str


class Balance(BaseModel):
    balance_amount: BalanceAmount
    balance_type: str
    reference_date: str


class AccountBalances(BaseModel):
    account_name: str = None
    account_id: str = None
    balances: dict[str, Balance]


class UserAccountBalances(BaseModel):
    balances: dict[str, AccountBalances] = Field(default_factory=dict)

    def set_account_balances(
        self, account_id, balance: AccountBalances, account_name: str = None
    ):
        def preprocess(balance):
            balance_to_set = deepcopy(balance)
            balance_to_set.account_id = account_id
            if account_name:
                balance_to_set.account_name = account_name
            return balance_to_set

        if not isinstance(balance, AccountBalances):
            raise TypeError("balances must be of type AccountBalances")

        self.balances[account_id] = preprocess(balance)

    def get_balances(self) -> list[AccountBalances]:
        return list(self.balances.values())

    def get_balances_by_account_id(self, account_id: str) -> AccountBalances | None:
        return self.balances.get(account_id, None)

    def to_dict(self, account_id):
        data = deepcopy(
            self.get_balances_by_account_id(account_id).model_dump().get("balances")
        )
        for d in data:
            d["account_id"] = account_id
        return data

    def to_dataframe(self, account_id: str) -> pd.DataFrame:
        balances = self.to_dict(account_id)
        if balances:
            return pd.json_normalize(balances)
        return None



class UserData(BaseModel):
    requisition: Requisition
    account_metadata: UserAccountMetadata = None
    account_details: UserAccountDetails = None
    account_balances: UserAccountBalances = None
    transactions: list[Transaction] = Field(default_factory=lambda: [])

    def get_account_transactions(self, account_id: str) -> list[Transaction]:
        return [
            transaction
            for transaction in self.transactions
            if transaction.account_id == account_id
        ]

    def query_transactions_by_transaction_code(
        self, proprietary_bank_transaction_code: str
    ):
        records = [
            d
            for d in self.transactions
            if d.proprietary_bank_transaction_code == proprietary_bank_transaction_code
        ]

        print(f"Found {len(records)} records")
        return records


class CurrentAccountBalanceTypes:
    interim_available = "interimAvailable"
    interim_booked = "interimBooked"
