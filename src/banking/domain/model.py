from dataclasses import dataclass
import datetime
from enum import Enum


class TransactionStatus(Enum):
    """
    Transaction status: may be booked or pending

    """

    booked = 1
    pending = 2


# Transaction class


@dataclass
class Transaction:
    booking_date: str = None
    booking_date_time: str = None
    remittance_information_unstructured: str = None
    proprietary_bank_transaction_code: str = None
    transaction_amount: float = None
    transaction_currency: str = None
    status: str = None
    transaction_id: str = None
    internal_transaction_id: str = None
    account_id: str = None
    account_type: str = None
    account_name: str = None
    creditor_name: str = None
    merchant_category_code: str = None
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
        account_id: str,
        balance_amount_interim_available: float,
        balance_amount_currency: str,
        balance_amount_reference_date: str,
        balance_amount_interim_booked: float,
        balance_amount_forward_available: float = None,
        balance_amount_opening_cleared: float = None,
        balance_amount_previously_closed_booked: float = None,
    ):
        self.account_name = account_name
        self.account_id = account_id
        self.account_type = account_type
        self.balance_amount_interim_available = balance_amount_interim_available
        self.balance_amount_currency = balance_amount_currency
        self.balance_amount_reference_date = balance_amount_reference_date
        self.balance_amount_interim_booked = balance_amount_interim_booked
        self.balance_amount_forward_available = balance_amount_forward_available
        self.balance_amount_opening_cleared = balance_amount_opening_cleared
        self.balance_amount_previously_closed_booked = (
            balance_amount_previously_closed_booked
        )

        self.pending_transactions = []
        self.booked_transactions = []

    def __str__(self) -> str:
        return f"Account: {self.account_name} ({self.account_id})"

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


csv_row = "2023-04-21,2023-04-21T05:05:50Z,RECURRENT TRANSACTION AT APPLE.COM/BIL IRL OF 6.99 GBP ON 2023-04-21,RECURRENT TRANSACTION,-6.99,GBP,pending,,,590300bd-3daf-4d5e-9274-7a3782261f7e,CACC,joint account,,,,,,,,,,,"
# Split the CSV row into individual values
row_values = csv_row.split(",")

# Create a Transaction instance
transaction_instance = Transaction(
    booking_date=row_values[0],
    booking_date_time=row_values[1],
    remittance_information_unstructured=row_values[2],
    proprietary_bank_transaction_code=row_values[3],
    transaction_amount=float(row_values[4]),
    transaction_currency=row_values[5],
    status=row_values[6],
    transaction_id=row_values[7],
    internal_transaction_id=row_values[8],
    account_id=row_values[9],
    account_type=row_values[10],
    account_name=row_values[11],
    creditor_name=row_values[12],
    merchant_category_code=row_values[13],
    instructed_amount=float(row_values[14]) if row_values[14] else None,
    instructed_currency=row_values[15],
    source_currency=row_values[16],
    exchange_rate=float(row_values[17]) if row_values[17] else None,
    unit_currency=row_values[18],
    target_currency=row_values[19],
    quotation_date=row_values[20],
    value_date=row_values[21],
    value_date_time=row_values[22],
)

# Print the created instance
print(transaction_instance)

account_id = "590300bd-3daf-4d5e-9274-7a3782261f7e"
account_row = "joint account,CACC,13299.63,GBP,2023-04-21,13310.67,,,"

# Split the account information into individual values
account_values = account_row.split(",")

# Create an Account instance
account_instance = Account(
    account_name=account_values[0],
    account_type=account_values[1],
    balance_amount_interim_available=float(account_values[2]),
    balance_amount_currency=account_values[3],
    balance_amount_reference_date=account_values[4],
    balance_amount_interim_booked=float(account_values[5]),
    balance_amount_forward_available=float(account_values[6])
    if account_values[6]
    else None,
    balance_amount_opening_cleared=float(account_values[7])
    if account_values[7]
    else None,
    balance_amount_previously_closed_booked=float(account_values[8])
    if account_values[8]
    else None,
    account_id=account_id,
)

# Print the created instance
print(account_instance)
