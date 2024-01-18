from loguru import logger
import numpy as np
import pandas as pd

import model


# clean
def validate_field(df, field):
    if not field in df.columns:
        logger.warning("[CLEANING] field {field} not found in df.columns")
        return False
    else:
        return True


def remove_nan(df):
    return df.replace({np.nan: None})


def clean_text(text: str) -> str:
    text = (
        text.replace("description:", "").replace("ref.", "ref ").replace("&amp;", " ")
    )

    text = text.lower()
    return text


def clean_text_field(df, field):
    if not validate_field(df, field):
        raise ValueError()

    if not field in df.columns:
        logger.warning("[CLEANING] field {field} not found in df.columns")
        return df

    df[field] = df[field].fillna("unknown")
    df[field] = df[field].apply(clean_text)
    return df


def round_currency(df, field):
    if not validate_field(df, field):
        raise ValueError()
    # handle rounding
    df[field] = df[field].apply(lambda x: round(x, 2))
    return df


def handle_integer_category(df, field):
    if not validate_field(df, field):
        raise ValueError()
    df[field] = df[field].fillna(-1)
    df[field] = df[field].astype(int)
    return df


def clean_transactions(transactions: list[model.Transaction]):
    # instantiate
    df = pd.DataFrame(transactions)

    # remove nan // incorrect types
    df = remove_nan(df)

    # process integer categories
    integer_category_fields = ["merchant_category_code"]
    for field in integer_category_fields:
        df = handle_integer_category(df=df, field=field)

    # process currency
    df = round_currency(df, "amount")

    # process text
    text_fields = [
        "debtor_name",
        "creditor_name",
        "remittance_information_unstructured",
    ]
    for field in text_fields:
        df = clean_text_field(df, field)

    # drop null columns
    df = df.dropna(axis=1)

    # back to transactions
    cleaned_transactions = [
        model.Transaction(**d) for d in df.to_dict(orient="records")
    ]
    return cleaned_transactions
