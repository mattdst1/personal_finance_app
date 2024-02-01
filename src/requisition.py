import ast
import os

import pandas as pd
from pathlib import Path
from pydantic import BaseModel, Field
from loguru import logger

from data_import import load_user_data
from model import UserData
from services.nordigen import account_api
import utils


class RequisitionModel(BaseModel):
    requisition_id: str = Field(
        description="Requisition id. This is unique to a user's account with an institution"
    )


class RequisitionHelper:
    def __init__(self):
        self.requisition: RequisitionModel = RequisitionModel(
            requisition_id=self._get_requisition_id()
        )

    def _get_requisition_id(self):
        requisition_ids = ast.literal_eval(os.environ.get("requisition_ids"))
        logger.info(f"found {len(requisition_ids)} requisition_ids")

        if not requisition_ids:
            raise ValueError("no requisition ids found")

        if not isinstance(requisition_ids, list):
            raise TypeError("invalid type found")

        if len(requisition_ids) > 1:
            logger.warning("More than 1 requisition id found")
            raise NotImplementedError("unhandled >1 requisition")

        requisition_id = requisition_ids[0]
        return requisition_id

    async def get_latest_data(self):
        """ """
        output_path = await account_api.get_latest_data(
            requisition_id=self.requisition.requisition_id
        )
        latest_data = load_user_data(output_path)
        return latest_data

    def import_historic_data():
        # read from csv
        path_transactions_historic = Path("../data/historic/df_transactions_raw.csv")
        transactions_df = pd.read_csv(path_transactions_historic)
        # camel to snake case, keeping right of '.'
        transactions_dict = transactions_df.to_dict(orient="records")
        transactions_dict = utils.clean_column_names(transactions_dict)
        # validate with dataclass
        return transactions_dict

    async def get_latest_transactions(self):
        data = await self.get_latest_data()
        return data.transactions


async def get_user_data():
    requisition_helper = RequisitionHelper()
    user_data = await requisition_helper.get_latest_data()
    return user_data
