import mock_data
import model

# user_data, transactions, _account_mapping = mock_data.get_mocked_data()

# account_mapping = {
#     "590300bd-3daf-4d5e-9274-7a3782261f7e": "joint account",
#     "d2ff77d0-6c80-4580-95a5-e3e87a098db9": "STAFF ALL IN ONE CREDIT CARD",
#     "e9e5f8b9-da61-49ce-bdae-56546ce4a1c9": "single account",
# }


def set_account_ids(user_data: model.UserData, mapping: dict):
    """
    Set account IDs for user data based on mapping.

    Args:
        user_data (model.UserData): The user data to set account IDs for.
        mapping (dict): The mapping of account IDs to account names.
    """

    def invert_mapping(mapping):
        # invert the mapping {key: name} to {name: key}
        return {v: k for k, v in mapping.items()}

    def process_credit_cards(cards: list[model.CreditCardDetails], mapping: dict):
        for card in cards:
            card.account_id = mapping[card.details]

    def process_current_accounts(accounts: list[model.CurrentAccountDetails], mapping):
        current_account: model.CurrentAccountDetails
        for account in user_data.account_details.current_accounts:
            account.account_id = mapping[account.name]

    mapping = invert_mapping(mapping)
    process_credit_cards(user_data.account_details.credit_cards, mapping)
    process_current_accounts(user_data.account_details.current_accounts, mapping)
