from dataclasses import dataclass
import dataclasses
import datetime
from enum import Enum
from copy import copy
from collections import OrderedDict

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
        self.currency = currency
        self.reference_date = reference_date
        # all
        self.pending_transactions = []
        self.booked_transactions = []
        # bank account
        self.interim_booked = interim_booked_balance
        self.interim_available = interim_available_balance
        # credit card
        self.forward_available = forward_available_balance
        self.opening_cleared = opening_cleared_balance
        self.previously_closed_booked = previously_closed_booked_balance
        self.masked_pan = masked_pan
        self.enforce_types()

    # enforce types

    def enforce_types(self):
        # if available and not right type, turn strings into appropriate types
        if self.interim_available and not isinstance(self.interim_available, float):
            self.interim_available = float(self.interim_available)
        if self.interim_booked and not isinstance(self.interim_booked, float):
            self.interim_booked = float(self.interim_booked)
        if self.forward_available and not isinstance(self.forward_available, float):
            self.forward_available = float(self.forward_available)
        if self.opening_cleared and not isinstance(self.opening_cleared, float):
            self.opening_cleared = float(self.opening_cleared)
        if self.previously_closed_booked and not isinstance(
            self.previously_closed_booked, float
        ):
            self.previously_closed_booked = float(self.previously_closed_booked)

    # return as dict

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
        return f"Account='{self.account_name}' AccountType={self.account_type} Id:={self.account_id} InterimBalance={self.interim_available} "

    def __str__(self) -> str:
        return f"Account: {self.account_name} Id: ({self.account_id}) Interim balance: {self.interim_available} "

    def add_transaction(self, transaction: Transaction):
        # check that account_id are same
        if transaction.account_id != self.account_id:
            raise ValueError(
                f"Transaction account_id {transaction.account_id} does not match account_id {self.account_id}"
            )
        # add metadata to transaction
        transaction.account_name = self.account_name
        transaction.account_type = self.account_type

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


class BankAccount(Account):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.overdraft_limit = None

    def __repr__(self):
        return f"Account='{self.account_name}' AccountType={self.account_type} Id:={self.account_id} InterimBalance={self.interim_available} OverdraftLimit={self.overdraft_limit}"

    def __str__(self) -> str:
        return f"Account: {self.account_name} Id: ({self.account_id}) Interim balance: {self.interim_available} Overdraft Limit: {self.overdraft_limit}"


class CreditCard(Account):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # calculate credit limit
        if self.forward_available and self.opening_cleared:
            self.credit_limit = self.forward_available - self.opening_cleared
        else:
            self.credit_limit = None

        self.interest_rate = None
        self.minimum_payment = None

    def __repr__(self):
        return f"Account='{self.account_name}' AccountType={self.account_type} Id:={self.account_id} InterimBalance={self.interim_available} CreditLimit={self.credit_limit}"

    def __str__(self) -> str:
        return f"Account: {self.account_name} Id: ({self.account_id}) Interim balance: {self.interim_available} Credit Limit: {self.credit_limit}"


class User:
    def __init__(self, name: str = "Matthew Stewart"):
        self.bank_accounts: list[BankAccount] = []
        self.credit_cards: list[CreditCard] = []
        self.name = name

    def add_account(self, account: Account):
        if isinstance(account, BankAccount):
            self.bank_accounts.append(account)
        elif isinstance(account, CreditCard):
            self.credit_cards.append(account)
        else:
            raise ValueError(f"Account type {type(account)} is not valid")

    def add_accounts(self, accounts: list):
        for account in accounts:
            self.add_account(account)

    @property
    def accounts(self):
        return self.bank_accounts + self.credit_cards

    @property
    def name(self):
        return self.bank_accounts[0].account_name

    @property
    def currency(self):
        return self.bank_accounts[0].currency

    @property
    def reference_date(self):
        return self.bank_accounts[0].reference_date

    def get_account(self, account_id: str):
        for account in self.accounts:
            if account.account_id == account_id:
                return account
        return None

    def __repr__(self):
        return f"User: {self.name} Accounts: {self.accounts}"

    def __str__(self) -> str:
        return f"User: {self.name} Accounts: {self.accounts}"

    def to_dict(self):
        # need to copy each account into  a dict

        return_data = copy(self.__dict__)
        # turn each copy of account in return data to dict
        return_data["bank_accounts"] = [a.to_dict() for a in copy(self.bank_accounts)]
        return_data["credit_cards"] = [a.to_dict() for a in copy(self.credit_cards)]

    # get net balance (available balance in card + net position in credit card)
    def get_net_balance(self):
        net_balance = 0
        for account in self.accounts:
            if isinstance(account, BankAccount):
                net_balance += account.interim_available
            elif isinstance(account, CreditCard):
                net_balance += account.forward_available - account.credit_limit
        return net_balance

    # suggest new funcs
    def get_transactions_by_date(self, start_date, end_date):
        transactions = []
        for account in self.accounts:
            for transaction in account.booked_transactions:
                if (
                    transaction.booking_date >= start_date
                    and transaction.booking_date <= end_date
                ):
                    transactions.append(transaction)
        return transactions

    def get_transactions_by_amount(self, min_amount, max_amount):
        transactions = []
        for account in self.accounts:
            for transaction in account.booked_transactions:
                if (
                    transaction.amount >= min_amount
                    and transaction.amount <= max_amount
                ):
                    transactions.append(transaction)
        return transactions

    # def get_transactions_by_category(self, category):
    #     transactions = []
    #     for account in self.accounts:
    #         for transaction in account.booked_transactions:
    #             if transaction.merchant_category_code == category:
    #                 transactions.append(transaction)
    #     return transactions

    def get_transactions_by_status(self, status):
        transactions = []
        for account in self.accounts:
            for transaction in account.booked_transactions:
                if transaction.status == status:
                    transactions.append(transaction)
        return transactions

    def get_transactions_by_currency(self, currency):
        transactions = []
        for account in self.accounts:
            for transaction in account.booked_transactions:
                if transaction.currency == currency:
                    transactions.append(transaction)
        return transactions

    def get_transactions_by_account(self, account_id):
        transactions = []
        for account in self.accounts:
            if account.account_id == account_id:
                transactions.append(account.booked_transactions)
        return transactions

    def get_transactions_by_date_range(self, start_date, end_date):
        transactions = []
        for account in self.accounts:
            for transaction in account.booked_transactions:
                if (
                    transaction.booking_date >= start_date
                    and transaction.booking_date <= end_date
                ):
                    transactions.append(transaction)
        return transactions

    def get_transactions_by_amount_range(self, min_amount, max_amount):
        transactions = []
        for account in self.accounts:
            for transaction in account.booked_transactions:
                if (
                    transaction.amount >= min_amount
                    and transaction.amount <= max_amount
                ):
                    transactions.append(transaction)
        return transactions

    def get_transactions(self):
        transactions = []
        for account in self.accounts:
            transactions.extend(account.booked_transactions)
        return transactions

    def handle_multiple_queries(self, *queries):
        # add docstring
        """
        Handle multiple queries by finding the common transactions between them.

        Args:
            *queries: A list of queries to handle.

        Returns:
            A list of transactions that are common to all queries.
        """
        dicts = [[d.to_dict() for d in query] for query in queries]
        common_dicts = find_common_dicts(*dicts)
        transactions = [Transaction(t) for t in common_dicts]
        return transactions


def find_common_dicts(*lists):
    def dict_to_ordered_tuple(d):
        return tuple(OrderedDict(sorted(d.items())).items())

    sets = [set(dict_to_ordered_tuple(d) for d in lst) for lst in lists]

    common_set = set.intersection(*sets)

    result = [dict(t) for t in common_set]
    return result
