import pandas as pd
from pathlib import Path
from loguru import logger

from enrich import mappings


def add_merchant_codes(df, code_path: Path):
    # category codes
    if not Path(code_path).is_file():
        logger.warning(f"not found merchant_category_codes")
        return df
    else:
        merchant_category_codes = pd.read_json(str(code_path))

    df[mappings.MERCHANT_CODE] = df[mappings.MERCHANT_CODE].fillna(-1)
    df[mappings.MERCHANT_CODE] = df[mappings.MERCHANT_CODE].astype(int)
    df = pd.merge(
        df,
        merchant_category_codes[["edited_description", "mcc"]],
        left_on=mappings.MERCHANT_CODE,
        right_on="mcc",
        how="left",
    ).drop(columns=["mcc"])
    df = df.rename(columns={"edited_description": "merchant_category"})
    df["merchant_category"] = df["merchant_category"].fillna("unknown")
    return df
