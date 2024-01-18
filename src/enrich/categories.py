import pandas as pd
from loguru import logger

import utils
from enrich.mappings import DESCRIPTION, CODE, COUNTERPARTY, EMPLOYERS


def clean_df(transactions_df: pd.DataFrame):
    # data
    df = transactions_df.copy()
    df["category"] = "unlabelled"
    df[DESCRIPTION] = df[DESCRIPTION].fillna("unknown")
    df[CODE] = df[CODE].fillna("unknown")
    return df


class TransactionCategorizer:
    def __init__(self):
        self.category_functions = []

    def register(self, func):
        """Register a new categorization function."""
        self.category_functions.append(func)

    def _apply_functions(self, row):
        """Apply registered categorization functions to a DataFrame row."""

        for func in self.category_functions:
            row = func(row)
            if row["category"] != "unlabelled":
                break
        return row

    def categorize_transactions(self, df) -> pd.DataFrame:
        logger.info(f"Adding transactions category")
        """Categorize transactions in a DataFrame using registered functions."""
        df = clean_df(df.copy())
        df["category"] = "unlabelled"
        return df.apply(self._apply_functions, axis=1)


# Define categorization functions
def category_salary(row):
    if row["category"] != "unlabelled":
        return row

    is_bank_transfer = row[CODE] == "BANK TRANSFER CREDIT"
    is_employer = any(employer in row[COUNTERPARTY] for employer in EMPLOYERS)

    if is_bank_transfer and is_employer:
        row["category"] = "salary"
    return row


def category_interest_income(row):
    if row["category"] != "unlabelled":
        return row

    is_interest_paid = "interest paid" in row[DESCRIPTION]
    is_interest_paid_credit = "credit interest" in row[DESCRIPTION]
    is_cashback = "cashback" in row[DESCRIPTION]
    is_cashback_method = "CASHBACK" in row[CODE]
    if (
        (is_interest_paid)
        or (is_interest_paid_credit)
        or (is_cashback)
        or (is_cashback_method)
    ):
        row["category"] = "interest"
    return row


ACCOUNT_TRANSFER = "own account transfer"


def category_own_account_transfer(row):
    if row["category"] != "unlabelled":
        return row

    is_credit_card_payment = "credit card payment" in row[DESCRIPTION]
    is_my_transfer = "transfer to mr matthew david stewart" in row[DESCRIPTION]
    is_my_transfer_received = (
        "transfer from mr matthew david stewart" in row[DESCRIPTION]
    )
    is_faster_payment = "faster payment" in row[DESCRIPTION]
    is_received_payment = "FASTER PAYMENT RECEIVED".lower() in row[CODE].lower()
    is_faster_payment_receipt = "FASTER PAYMENT RECEIPT".lower() in row[CODE].lower()
    is_vanguard = "vanguard asset management" in row[COUNTERPARTY]
    is_solium = "solium capital" in row[COUNTERPARTY]
    is_bank_credit = "BANK TRANSFER CREDIT" in row[CODE]
    if (is_credit_card_payment) or (is_my_transfer) or (is_my_transfer_received):
        row["category"] = ACCOUNT_TRANSFER
    elif is_faster_payment and is_received_payment:
        row["category"] = ACCOUNT_TRANSFER
    elif (is_vanguard) and is_faster_payment_receipt:
        row["category"] = ACCOUNT_TRANSFER
    elif (is_solium) and (is_bank_credit):
        row["category"] = ACCOUNT_TRANSFER
    elif is_faster_payment_receipt:
        row["category"] = "faster_payments_receipt"
    return row


def category_childcare(row):
    if row["category"] != "unlabelled":
        return row

    is_gov_uk = "gov" in row[DESCRIPTION]
    is_blair_reference = "1100049398055" in row[DESCRIPTION]
    if (is_gov_uk) and (is_blair_reference):
        row["category"] = "childcare"
    return row


UTILITY_PROVIDERS = [
    "scottishpower",
    "ee limited",
    "seethelight",
    "thames water",
    "apple.com/bill",
    "chatgpt subscription",
    "tv licence",
]


def category_utilities(row):
    if row["category"] != "unlabelled":
        return row

    is_utility = any(provider in row[COUNTERPARTY] for provider in UTILITY_PROVIDERS)

    if is_utility:
        row["category"] = "utilities"
    return row


HOME_SERVICE_PROVIDERS = ["mr dax baker", "townsends cleani", "cerisa sansum"]


def category_home_services(row):
    if row["category"] != "unlabelled":
        return row

    is_provider = any(
        provider in row[DESCRIPTION] for provider in HOME_SERVICE_PROVIDERS
    )

    if is_provider:
        row["category"] = "home services"
    return row


EATING_OUT_PROVIDERS = [
    "mcdonalds",
    "kfc",
    "burger king",
    "bk",
    "five guys",
    "zpos* swindon",
    "dominos",
    "costa",
    "subway",
    "costa coffee",
    "coffee",
    "pizza hut",
    "blundson arms",
    "harvester",
    "greek olive",
    "greggs",
    "starbucks",
    "just eat",
    "uber eats",
    "sims chippy",
    "goddard arms",
    "olive tree",
    "nandos",
    "itsu",
    "benugo",
    "pret a manger",
    "gulshan brasserie",
    "sq *balulas",
    "pizza",
    "pizzaexpress",
    "swindon rendezvous",
    "frosts garden",
    "cornish bakehouse bath gb",
    "project coffee",
    "greek euros ltd",
    "fratellos swindon",
    "sweet little thing",
    "hall and woodhouse",
    "*eat",
    "mollies",
]


def category_eating_out(row):
    if row["category"] != "unlabelled":
        return row

    is_provider = any(provider in row[DESCRIPTION] for provider in EATING_OUT_PROVIDERS)

    if is_provider:
        row["category"] = "eating out"
    return row


GROCERY_PROVIDERS = [
    "co-operative",
    "co operative food",
    "sainsburys",
    "sainsbury's",
    "s pubs",
    "marks & spencer",
    "marks&spencer",
    "tesco stores",
    "tesco subscription",
    "icelandfood",
    "iceland foods",
    "aldi stores",
    "lidl",
    "aldi",
    "gousto",
    "asda stores",
    "asda",
]


def category_groceries(row):
    if row["category"] != "unlabelled":
        return row

    is_provider = any(provider in row[DESCRIPTION] for provider in GROCERY_PROVIDERS)
    not_fuel = "fuel" not in row[DESCRIPTION]
    not_petrol_1 = "petr" not in row[DESCRIPTION]
    not_petrol = not_petrol_1

    if (is_provider) and (not_fuel) and (not_petrol):
        row["category"] = "groceries"
    return row


HOUSING = ["virgin money", "swindon bc central"]


def category_housing(row):
    if row["category"] != "unlabelled":
        return row

    is_provider = any(provider in row[DESCRIPTION] for provider in HOUSING)

    if is_provider:
        row["category"] = "housing"
    return row


DEBT = ["slc receipts", "creation.co.uk", "student loans co"]


def category_debt(row):
    if row["category"] != "unlabelled":
        return row

    is_provider = any(provider in row[DESCRIPTION] for provider in DEBT)

    if is_provider:
        row["category"] = "debt"
    return row


TRANSPORT = [
    "hcp capital uk",
    "fish brothers kia",
    "applegreen swindon",
    "waves at",
    "bucksrailcentre",
    "trainline",
    "hks saxon bletchley" "tfl london",
    "tfl travel",
    "holmrook  s.stn",
    "parking",
    "go south coast",
    "apcoa parking",
    "thamesdown tyres",
    "esso",
    "first york",
    "garage",
    "shell",
    "ref mmv310288591",
]


def category_transport(row):
    if row["category"] != "unlabelled":
        return row

    is_provider = any(provider in row[DESCRIPTION] for provider in TRANSPORT)
    is_fuel = "fuel" in row[DESCRIPTION]
    is_petrol = "petrol" in row[DESCRIPTION]
    if (is_provider) or (is_fuel) or (is_petrol):
        row["category"] = "transport"
    return row


TRAVEL = [
    "paris 2024",
    "doubletree",
    "holiday inn",
    "gwr swindon",
    "big bus tours",
    "hm passport office",
    "ravenglass & eskdale r",
    "scottish seabird centr",
    "airbnb",
    "roves farm swindon gb",
    "roman baths",
    "seton sand",
    "barnestravel",
    "booking.com",
    "kinggeorge-eskdale.com",
    "b h inn",
    "jubilee garage",
    "king george iv inn holmrook",
]


def category_travel(row):
    if row["category"] != "unlabelled":
        return row

    is_provider = any(provider in row[DESCRIPTION] for provider in TRAVEL)

    if is_provider:
        row["category"] = "travel"
    return row


ENTERTAINMENT = [
    "microsoft*xbox",
    "microsoft*subscription",
    "voucher express",
    "blizzard entertainment",
    "cotswold wildlife park",
    "theatre by the lake",
    "steamgames",
    "gymcastic",
    "stretches & strokes",
    "unite the union",
    "steam purchase",
    "the spectator",
    "toddler town",
    "lw theatres group",
    "microsoft*ultim msbill",
    "rookery farm",
    "party warehouse",
    "games lore",
    "event attractions",
    "firestorm cards",
    "uk games expo",
    "jagex.com",
    "sp computers",
]


def category_entertainment(row):
    if row["category"] != "unlabelled":
        return row

    is_provider = any(provider in row[DESCRIPTION] for provider in ENTERTAINMENT)

    if is_provider:
        row["category"] = "entertainment"
    return row


SHOPPING = [
    "amazon",
    "amznmktplace",
    "faceface",
    "under armour",
    "clarks outlet",
    "fatface",
    "poundland",
    "frosts",
    "photobox",
    "the entertainer",
    "next retail",
    "hobbycraft",
    "babysensory",
    "amazon.co.uk",
    "claybearofficial",
    "argos",
    "dobbies",
    "sp close parent",
    "nappy den",
    "dunelm",
    "littlelamb nappie",
    "photobox",
    "ikea",
    "paypal",
    "vinted",
    "adidas",
    "sumup",
    "next online",
    "the works",
    "etsy.com",
    "homesense",
    "mixtiles",
    "smyths toys",
    "snappy snaps",
    "bookshop",
    "wh smith",
    "wickes",
    "post office",
]


def category_shopping(row):
    if row["category"] != "unlabelled":
        return row

    is_provider = any(provider in row[DESCRIPTION] for provider in SHOPPING)

    if is_provider:
        row["category"] = "shopping"
    return row


PETCARE = [
    "butternut box",
    "butternut",
    "lilys kitchen limited",
    "pets at home",
    "ifl pet insurance",
]


def category_petcare(row):
    if row["category"] != "unlabelled":
        return row

    is_provider = any(provider in row[DESCRIPTION] for provider in PETCARE)

    if is_provider:
        row["category"] = "petcare"
    return row


HEALTHCARE = [
    "smiles centre swindon",
    "moveology",
    "david lloyd leisur",
    "vitabiotics",
    "jessicas hair",
    "boots",
    "pharmacy",
    "smilescentre",
    "david lloyd",
    "great western hospital swindon",
    "great western h",
]


def category_healthcare(row):
    if row["category"] != "unlabelled":
        return row

    is_provider = any(provider in row[DESCRIPTION] for provider in HEALTHCARE)

    if is_provider:
        row["category"] = "healthcare"
    return row


SAVINGS = ["winterflood"]


def category_savings(row):
    if row["category"] != "unlabelled":
        return row

    is_provider = any(provider in row[DESCRIPTION] for provider in SAVINGS)

    if is_provider:
        row["category"] = "savings"
    return row


categorizer = TransactionCategorizer()
categorizer.register(category_salary)
categorizer.register(category_interest_income)
categorizer.register(category_own_account_transfer)
categorizer.register(category_utilities)
categorizer.register(category_childcare)
categorizer.register(category_home_services)
categorizer.register(category_groceries)
categorizer.register(category_eating_out)
categorizer.register(category_housing)
categorizer.register(category_debt)
categorizer.register(category_transport)
categorizer.register(category_travel)
categorizer.register(category_shopping)
categorizer.register(category_healthcare)
categorizer.register(category_petcare)
categorizer.register(category_savings)
categorizer.register(category_entertainment)
