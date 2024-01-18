import utils

EMPLOYERS = ["aviva", "satalia"]
CODE = utils.to_snake_case_with_dots("proprietaryBankTransactionCode")
DESCRIPTION = utils.to_snake_case_with_dots("remittanceInformationUnstructured")
AMOUNT = utils.to_snake_case_with_dots("transactionAmount.amount")
COUNTERPARTY = utils.to_snake_case_with_dots("counterparty")
CREDITOR_NAME = utils.to_snake_case_with_dots("creditorName")
MERCHANT_CODE = utils.to_snake_case_with_dots("merchantCategoryCode")
