from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import mapper, relationship

from .banking.adapters import model


metadata = MetaData()
transaction_lines = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("booking_date", Date),
    Column("booking_date_time", Date),
    Column("remittance_information_unstructured", String(255)),
    Column("proprietary_bank_transaction_code", String(255)),
    Column("amount", Float),
    Column("transaction_currency", String(255)),
    Column("status", String(255)),
    Column("transaction_id", String(255)),
    Column("internal_transaction_id", String(255)),
    Column("account_id", String(255)),
    Column("account_type", String(255)),
    Column("account_name", String(255)),
    Column("creditor_name", String(255)),
    Column("debtor_name", String(255)),
    Column("merchant_category_code", String(255)),
    Column("currency", String(255)),
    Column("instructed_amount", Float),
    Column("instructed_currency", String(255)),
    Column("source_currency", String(255)),
    Column("exchange_rate", Float),
    Column("unit_currency", String(255)),
    Column("target_currency", String(255)),
    Column("quotation_date", Date),
    Column("value_date", Date),
    Column("value_date_time", Date),
)


accounts = Table(
    "accounts",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("account_name", String(255)),
    Column("account_type", String(255)),
    Column("currency", String(255)),
    Column("reference_date", Date),
    Column("interim_booked", Float),
    Column("interim_available", Float),
    Column("forward_available", Float),
    Column("opening_cleared", Float),
    Column("previously_closed_booked", Float),
    Column("masked_pan", String(255)),
)

# fix this using model.User
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255)),
    Column("user_id", String(255)),
    Column("account_id", String(255)),
    Column("transaction_id", String(255)),
)


def start_mappers():
    transaction_mapper = mapper(model.Transaction, transaction_lines)
    mapper(
        model.Account,
        accounts,
        properties={
            "_allocations": relationship(
                transaction_mapper,
                secondary=users,
                collection_class=set,
            )
        },
    )


# write test_transactionline_mapper_can_load_lines(session)
def test_transactionline_mapper_can_load_lines(session):
    transaction_lines = [
        model.Transaction(
            booking_date="2022-01-01",
            booking_date_time="2022-01-01T00:00:00Z",
            remittance_information_unstructured="Remittance information unstructured",
            proprietary_bank_transaction_code="Proprietary bank transaction code",
            amount=100.0,
            transaction_currency="GBP",
            status="booked",
            transaction_id="transaction_id",
            internal_transaction_id="internal_transaction_id",
            account_id="account_id",
            account_type="account_type",
            account_name="account_name",
            creditor_name="creditor_name",
            debtor_name="debtor_name",
            merchant_category_code="merchant_category_code",
            currency="currency",
            instructed_amount=100.0,
            instructed_currency="instructed_currency",
            source_currency="source_currency",
            exchange_rate=1.0,
            unit_currency="unit_currency",
            target_currency="target_currency",
            quotation_date="2022-01-01",
            value_date="2022-01-01",
            value_date_time="2022-01-01T00:00:00Z",
        ),
        model.Transaction(
            booking_date="2022-01-02",
            booking_date_time="2022-01-02T00:00:00Z",
            remittance_information_unstructured="Remittance information unstructured",
            proprietary_bank_transaction_code="Proprietary bank transaction code",
            amount=200.0,
            transaction_currency="GBP",
            status="booked",
            transaction_id="transaction_id",
            internal_transaction_id="internal_transaction_id",
            account_id="account_id",
            account_type="account_type",
            account_name="account_name",
            creditor_name="creditor_name",
            debtor_name="debtor_name",
            merchant_category_code="merchant_category_code",
            currency="currency",
            instructed_amount=200.0,
            instructed_currency="instructed_currency",
            source_currency="source_currency",
            exchange_rate=1.0,
            unit_currency="unit_currency",
            target_currency="target_currency",
            quotation_date="2022-01-02",
            value_date="2022-01-02",
            value_date_time="2022-01-02T00:00:00Z",
        ),
    ]

    session.add_all(transaction_lines)
    session.commit()

    loaded_transaction_lines = session.query(model.Transaction).all()

    assert loaded_transaction_lines == transaction_lines
