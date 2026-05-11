#!/usr/bin/env python

from typing import Any

DateTuple = tuple[int, int, int]

financial_transactions_storage: list[dict[str, Any]] = []

DATE_KEY = "date"
CATEGORY_KEY = "category"
AMOUNT_KEY = "amount"

LEN_CATEGORY_PATH = 2

DATE_LENGTH = 10
NUMBER_OF_DEFIS = 2

INCOME_ARGS = 3
COST_ARGS_TO_OPERATE = 4
COST_ARGS_TO_GET_CATEGORIES = 2
STATS_ARGS = 2

MONTHS_THIRTY_DAYS = (4, 6, 9, 11)

FEBRUARY = 2

MIN_MONTH = 1
MAX_MONTH = 12

MIN_DAY = 1

MAX_DAY_IN_THIRTY_DAYS_MONTH = 30
MAX_DAY_IN_THIRTY_ONE_DAY_MONTH = 31

MAX_DAY_FEB_LEAP = 29
MAX_DAY_FEB_NORMAL = 28

STATS_PRINT = """Your statistics as of {}:
Total capital: {} rubles
This month, {} amounted to {} rubles.
Income: {} rubles
Expenses: {} rubles

Details (category: amount):"""

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"
NOT_EXISTS_CATEGORY = "Category not exists!"

EXPENSE_CATEGORIES: dict[str, tuple[str, ...]] = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("BuyCar", "BuyMobilePhone"),
}


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def date_validation(day: int, month: int, year: int) -> bool:
    if not (MIN_MONTH <= month <= MAX_MONTH):
        return False
    if day < MIN_DAY:
        return False
    if month in MONTHS_THIRTY_DAYS:
        return day <= MAX_DAY_IN_THIRTY_DAYS_MONTH
    if month == FEBRUARY:
        max_day = MAX_DAY_FEB_LEAP if is_leap_year(year) else MAX_DAY_FEB_NORMAL
        return day <= max_day
    return day <= MAX_DAY_IN_THIRTY_ONE_DAY_MONTH


def extract_date(raw_date: str) -> DateTuple | None:
    if len(raw_date) != DATE_LENGTH:
        return None
    if raw_date.count("-") != NUMBER_OF_DEFIS:
        return None
    try:
        day, month, year = map(int, raw_date.split("-"))
    except ValueError:
        return None
    parsed_date = (day, month, year)
    if not date_validation(*parsed_date):
        return None
    return parsed_date


def parse_float(raw_number: str) -> float | None:
    try:
        return float(raw_number.replace(",", "."))
    except ValueError:
        return None


def categories_validate(category_name: str) -> bool:
    category_path = category_name.split("::")
    return (
        len(category_path) == LEN_CATEGORY_PATH
        and category_path[0] in EXPENSE_CATEGORIES
        and category_path[1] in EXPENSE_CATEGORIES[category_path[0]]
    )


def is_same_month(first_date: DateTuple, second_date: DateTuple) -> bool:
    return first_date[1:] == second_date[1:]


def is_not_later(reference_date: DateTuple, transaction_date: DateTuple) -> bool:
    return to_comparable_date(transaction_date) <= to_comparable_date(reference_date)

def to_comparable_date(date: DateTuple) -> DateTuple:
    day, month, year = date
    return (year, month, day)


def count_capital(reference_date: DateTuple) -> float:
    total_capital: float = 0
    for transaction in financial_transactions_storage:
        transaction_date = transaction[DATE_KEY]
        if not is_not_later(reference_date, transaction_date):
            continue
        if CATEGORY_KEY in transaction:
            total_capital -= transaction[AMOUNT_KEY]
        else:
            total_capital += transaction[AMOUNT_KEY]
    return total_capital


def count_monthly_income(reference_date: DateTuple) -> float:
    monthly_income: float = 0
    for transaction in financial_transactions_storage:
        transaction_date = transaction[DATE_KEY]
        if check_count_monthly_income(transaction, reference_date, transaction_date):
            continue
        monthly_income += transaction[AMOUNT_KEY]
    return monthly_income


def check_count_monthly_income(transaction: dict[str, Any], reference_date: DateTuple, transaction_date: DateTuple) -> bool:
    if CATEGORY_KEY in transaction:
        return False
    if not is_not_later(reference_date, transaction_date):
        return False
    return not is_same_month(reference_date, transaction_date)


def count_monthly_expense(reference_date: DateTuple) -> float:
    monthly_expense: float = 0
    for transaction in financial_transactions_storage:
        transaction_date = transaction[DATE_KEY]
        if check_count_monthly_expense(transaction, reference_date, transaction_date):
            continue
        monthly_expense += transaction[AMOUNT_KEY]
    return monthly_expense


def check_count_monthly_expense(transaction: dict[str, Any], reference_date: DateTuple, transaction_date: DateTuple) -> bool:
    if CATEGORY_KEY not in transaction:
        return False
    if not is_not_later(reference_date, transaction_date):
        return False
    return not is_same_month(reference_date, transaction_date)


def count_categories(reference_date: DateTuple) -> dict[str, float]:
    categories: dict[str, float] = {}
    for transaction in financial_transactions_storage:
        transaction_date = transaction[DATE_KEY]
        if check_count_categories(transaction, reference_date, transaction_date):
            continue
        category_name = transaction[CATEGORY_KEY]
        amount = transaction[AMOUNT_KEY]
        categories[category_name] = categories.get(category_name, float(0)) + amount
    return dict(sorted(categories.items()))

def check_count_categories(transaction: dict[str, Any], reference_date: DateTuple, transaction_date: DateTuple) -> bool:
    if CATEGORY_KEY not in transaction:
        return False
    if not is_not_later(reference_date, transaction_date):
        return False
    return not is_same_month(reference_date, transaction_date)


def print_capital(reference_date: DateTuple) -> str:
    capital = count_capital(reference_date)
    return f"{capital:.2f}"


def print_month_income(reference_date: DateTuple) -> str:
    monthly_income = count_monthly_income(reference_date)
    return f"{monthly_income:.2f}"


def print_month_expense(reference_date: DateTuple) -> str:
    monthly_expense = count_monthly_expense(reference_date)
    return f"{monthly_expense:.2f}"


def print_categories(reference_date: DateTuple) -> list[str]:
    categories = count_categories(reference_date)
    lines: list[str] = []
    for index, (category_name, amount) in enumerate(categories.items(), start=1):
        lines.append(f"{index}. {category_name}: {amount:.0f}")
    return lines


def add_for_tests() -> None:
    financial_transactions_storage.append({})


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        add_for_tests()
        return NONPOSITIVE_VALUE_MSG
    parsed_date = extract_date(income_date)
    if parsed_date is None:
        add_for_tests()
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append({AMOUNT_KEY: amount, DATE_KEY: parsed_date})
    return OP_SUCCESS_MSG


def cost_handler(
    category_name: str,
    amount: float,
    operation_date: str,
) -> str:
    if not categories_validate(category_name):
        add_for_tests()
        return NOT_EXISTS_CATEGORY
    if amount <= 0:
        add_for_tests()
        return NONPOSITIVE_VALUE_MSG
    parsed_date = extract_date(operation_date)
    if parsed_date is None:
        add_for_tests()
        return INCORRECT_DATE_MSG
    _, subcategory = category_name.split("::")
    financial_transactions_storage.append({CATEGORY_KEY: subcategory, AMOUNT_KEY: amount, DATE_KEY: parsed_date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    lines: list[str] = []
    for main_category, subcategories in EXPENSE_CATEGORIES.items():
        lines.extend(f"{main_category}::{subcategory}" for subcategory in subcategories)
    return "\n".join(lines)


def stats_handler(date: str) -> str:
    parsed_date = extract_date(date)
    if parsed_date is None:
        return INCORRECT_DATE_MSG
    month_profit = count_monthly_income(parsed_date) - count_monthly_expense(parsed_date)
    profit_type = "the profit" if month_profit > 0 else "the loss"
    result = STATS_PRINT.format(
        date,
        print_capital(parsed_date),
        profit_type,
        f"{month_profit:.2f}",
        print_month_income(parsed_date),
        print_month_expense(parsed_date),
    )
    lines = [result]
    lines.extend(print_categories(parsed_date))
    return "\n".join(lines)


def process_income(input_line: list[str]) -> str:
    if len(input_line) != INCOME_ARGS:
        return UNKNOWN_COMMAND_MSG
    amount = parse_float(input_line[1])
    if amount is None:
        return UNKNOWN_COMMAND_MSG
    return income_handler(amount, input_line[2])


def process_cost(input_line: list[str]) -> str:
    if len(input_line) == COST_ARGS_TO_GET_CATEGORIES:
        if input_line[1] == "categories":
            return cost_categories_handler()
        return UNKNOWN_COMMAND_MSG
    if len(input_line) != COST_ARGS_TO_OPERATE:
        return UNKNOWN_COMMAND_MSG
    amount = parse_float(input_line[2])
    if amount is None:
        return UNKNOWN_COMMAND_MSG
    return cost_handler(input_line[1], amount, input_line[3])


def process_stats(input_line: list[str]) -> str:
    if len(input_line) != STATS_ARGS:
        return UNKNOWN_COMMAND_MSG
    return stats_handler(input_line[1])


def main() -> None:
    while True:
        input_line = input().split()
        if not input_line:
            return
        command = input_line[0]
        match command:
            case "income":
                print(process_income(input_line))
            case "cost":
                print(process_cost(input_line))
            case "stats":
                print(process_stats(input_line))
            case _:
                print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
