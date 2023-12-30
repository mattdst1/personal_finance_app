from dataclasses import dataclass
import datetime
from enum import Enum


from dotenv import load_dotenv

load_dotenv("user.env")


class TransactionStatus(Enum):
    """
    Transaction status: may be booked or pending

    """

    booked = "booked"
    pending = "pending"


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


class Account:
    def __init__(
        self,
        account_name: str,
        account_type: str,
        currency: str,
        reference_date: str = None,
        interim_available: float = None,
        interim_booked: float = None,
        account_id: str = None,
        forward_available: float = None,
        opening_cleared: float = None,
        previously_closed_booked: float = None,
        masked_pan: str = None,
    ):
        self.account_name = account_name
        self.account_id = account_id
        self.account_type = account_type
        self.interim_available = interim_available
        self.currency = currency
        self.reference_date = reference_date
        self.interim_booked = interim_booked
        self.forward_available = forward_available
        self.opening_cleared = opening_cleared
        self.previously_closed_booked = previously_closed_booked
        self.masked_pan = masked_pan

        self.pending_transactions = []
        self.booked_transactions = []

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

        if transaction.status == TransactionStatus.booked:
            self.booked_transactions.append(transaction)
        else:
            self.pending_transactions.append(transaction)

    def get_transactions(self, status: TransactionStatus):
        if status == TransactionStatus.booked:
            return self.booked_transactions
        else:
            return self.pending_transactions


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
