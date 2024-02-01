from loguru import logger
import numpy as np
import pandas as pd
from pathlib import Path
from pydantic import BaseModel

from enrich import clean, mappings, counterparty, categories
import model
import requisition
import utils

SOURCE_HISTORIC = "historic"
SOURCE_API = "api"
BOOKING_DATE = "booking_date"
SAVE_PATH = Path("../data/transactions.json")
HISTORIC_TRANSACTIONS_PATH = Path("../data/historic/df_transactions_raw.csv")


def _time_data(df: pd.DataFrame) -> pd.DataFrame:
    df["booking_year"] = df["booking_date"].dt.year
    df["booking_month"] = df["booking_date"].dt.month
    return df


def _adjust_transaction_datetime(df: pd.DataFrame):
    df["booking_date"] = df.copy()["booking_date"].apply(pd.to_datetime)
    df["year_month"] = df["booking_date"].dt.strftime("%Y-%m")
    # df["booking_date"] = df.copy()["booking_date"].apply(pd.to_datetime)
    return df


def _enrich_transactions_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"Enriching dataframe")
    # counterparties
    df = counterparty.add_counterparties(df)

    # categorise
    df = categories.categorizer.categorize_transactions(df)

    # process currency
    df["flow"] = df["amount"].apply(utils.get_flow)

    # process time
    df = _adjust_transaction_datetime(df)
    df = _time_data(df)
    return df


def _enrich_transactions(transactions=list[model.Transaction]):
    df = pd.DataFrame(transactions)
    enriched_df = _enrich_transactions_dataframe(df)
    enriched_transactions = [
        model.Transaction(**d) for d in enriched_df.to_dict(orient="records")
    ]
    df = df.drop_duplicates().dropna(axis=1)
    return enriched_transactions


def enrich(transactions: list[model.Transaction]):
    # clean transactions
    cleaned_transactions = clean.clean_transactions(transactions)
    enriched_transactions = _enrich_transactions(cleaned_transactions)
    return enriched_transactions


def save_transactions(cleaned_transactions: list[model.Transaction]):
    data_to_save = [transaction.to_dict() for transaction in cleaned_transactions]
    utils.save_data_to_json(data_to_save, SAVE_PATH)

    assert Path("../data/transactions.json").is_file(), f"file not saved"


class HistoricDataHelper(BaseModel):
    path_transactions_historic: Path = Path("../data/historic/df_transactions_raw.csv")

    def read_data(
        self,
    ):
        transactions_df = pd.read_csv(self.path_transactions_historic)
        return transactions_df

    def preprocess_data(self, df: pd.DataFrame):
        df = df.dropna(axis=1)
        df.columns = [
            utils.keep_text_right_of_dot(utils.to_snake_case_with_dots(key))
            for key in df.columns
        ]

        transactions_dict = df.to_dict(orient="records")
        transactions_dict = utils.clean_column_names(transactions_dict)
        historic_transactions = [
            model.Transaction.from_dict(d) for d in transactions_dict
        ]
        # df["source"] = "historic"
        return historic_transactions

    def get_historic_transactions(self):
        df = self.read_data()
        transactions = self.preprocess_data(df)
        return transactions


def combine_transactions(
    historic_transactions: list[model.Transaction],
    latest_transactions: list[model.Transaction],
) -> list[model.Transaction]:
    """
    Combine historic and live transaction tables.

    Args:
        historic_transactions (list[model.Transaction]): Historic transactions.
        latest_transactions (list[model.Transaction]): Latest transactions.

    Returns:
        list[model.Transaction]: Combined transactions.
    """
    logger.debug(f"joining historic and live transaction tables")

    def make_dataframe(historic_transactions, source):
        # filter
        historic_df = pd.DataFrame(historic_transactions)
        historic_df = historic_df.loc[historic_df["status"] == "booked"]
        historic_df["source"] = source
        return historic_df

    historic_df = make_dataframe(historic_transactions, source=SOURCE_HISTORIC).dropna(
        axis=1, how="all"
    )
    latest_df = make_dataframe(latest_transactions, source=SOURCE_API).dropna(
        axis=1, how="all"
    )

    transactions_df = pd.concat([historic_df, latest_df]).drop_duplicates()
    transactions_df = transactions_df.sort_values(by="booking_date", ascending=False)
    transactions_df = transactions_df.drop_duplicates()
    transactions_df = transactions_df.reset_index(drop=True)
    transactions_df = transactions_df.drop(columns="source")
    transactions = [
        model.Transaction.from_dict(d)
        for d in transactions_df.to_dict(orient="records")
    ]
    return transactions


async def load_transactions():
    historic_helper = HistoricDataHelper()
    requisition_api = requisition.RequisitionHelper()
    # extract
    latest_transactions = await requisition_api.get_latest_transactions()
    historic_transactions = historic_helper.get_historic_transactions()
    transactions = combine_transactions(
        historic_transactions=historic_transactions,
        latest_transactions=latest_transactions,
    )
    return transactions


async def main():
    transactions = await load_transactions()
    enriched_transactions = enrich(transactions)
    save_transactions(enriched_transactions)


if __name__ == "__main__":
    logger.info("starting process_transactions.py")
    # use asyncio and run main
    import asyncio

    asyncio.run(main())
    logger.info("finished process_transactions.py")

"""
Usage example in notebook to run main:

from process_transactions import main

asyncio.run(main())  # run main


# RuntimeError: asyncio.run() cannot be called from a running event loop

import asyncio

loop = asyncio.get_event_loop()
loop.run_until_complete(main())  # run main
loop.close()  # close event loop


"""
