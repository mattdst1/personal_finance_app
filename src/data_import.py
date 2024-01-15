from pathlib import Path

import mock_data
import data_parsers
import model


def load_user_data(filepath: Path = mock_data.MOCK_PATH):
    # user level
    data, requisition = mock_data.load_data(data_filepath=filepath)
    metadata = model.UserAccountMetadata(accounts={})
    details = model.UserAccountDetails()
    balances = model.UserAccountBalances()
    transactions = []
    # import an account

    def parse_account_name(
        account_details: model.CurrentAccountDetails | model.CreditCardDetails,
    ):
        if isinstance(account_details, model.CurrentAccountDetails):
            account_name = account_details.name
            return account_name
        elif isinstance(account_details, model.CreditCardDetails):
            account_name = account_details.details
            return account_name
        else:
            raise ValueError(f"Unknown account type: {type(account_details)}")

    for account_id in requisition.accounts:
        # read all data
        account_data = data.get(account_id)

        # parse and validate
        metadata.add_account(
            account_id=account_id,
            account_metadata=data_parsers.parse_metadata(account_data),
        )

        # parse details and account account name
        parsed_account_details = data_parsers.parse_account_details(account_data)
        account_name = parse_account_name(parsed_account_details)

        # update user details
        details.add_account(
            account_id=account_id,
            account=parsed_account_details,
        )

        # update user balances
        balances.set_account_balances(
            account_id=account_id,
            balance=data_parsers.parse_account_balances(account_data),
            account_name=account_name,
        )

        # update user transactions
        account_transactions = data_parsers.parse_account_transactions(
            account_data=account_data, account_id=account_id, account_name=account_name
        )
        transactions.extend(account_transactions)

    user_data = model.UserData(
        requisition=requisition,
        account_metadata=metadata,
        account_details=details,
        account_balances=balances,
        transactions=transactions,
    )
    # return user_data,  transactions
    return user_data
