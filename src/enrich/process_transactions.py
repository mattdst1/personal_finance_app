from loguru import logger
import numpy as np
import pandas as pd

from enrich import clean, mappings, counterparty, categories
import model


def get_flow(amount: float):
    if amount > 0:
        return "credit"
    elif amount < 0:
        return "debit"
    else:
        raise ValueError()


def time_data(df: pd.DataFrame) -> pd.DataFrame:
    df["booking_year"] = df["booking_date"].dt.year
    df["booking_month"] = df["booking_date"].dt.month
    return df


def adjust_transaction_datetime(df: pd.DataFrame):
    df["booking_date"] = df.copy()["booking_date"].apply(pd.to_datetime)
    df["year_month"] = df["booking_date"].dt.strftime("%Y-%m")
    # df["booking_date"] = df.copy()["booking_date"].apply(pd.to_datetime)
    return df


def enrich_transactions_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"Enriching dataframe")
    # counterparties
    df = counterparty.add_counterparties(df)

    # categorise
    df = categories.categorizer.categorize_transactions(df)

    # process currency
    df["flow"] = df["amount"].apply(get_flow)

    # process time
    df = adjust_transaction_datetime(df)
    df = time_data(df)
    return df


def enrich_transactions(transactions=list[model.Transaction]):
    df = pd.DataFrame(transactions)
    enriched_df = enrich_transactions_dataframe(df)
    enriched_transactions = [
        model.Transaction(**d) for d in enriched_df.to_dict(orient="records")
    ]
    df = df.drop_duplicates().dropna(axis=1)
    return enriched_transactions


def process_transactions(transactions: list[model.Transaction]):
    # clean transactions
    cleaned_transactions = clean.clean_transactions(transactions)
    enriched_transactions = enrich_transactions(cleaned_transactions)
    return enriched_transactions
