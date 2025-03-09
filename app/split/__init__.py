from app.enum import FormEnum
from . import amount, equally, percentage


class SplitType(FormEnum):
    AMOUNT = "Amount"
    EQUALLY = "Equally"
    PERCENTAGE = "Percentage"


def _split_by_type(
    total_amount: float, users: dict[int, float], split_type: SplitType
) -> dict[int, float]:
    match split_type:
        case SplitType.AMOUNT:
            return users
        case SplitType.EQUALLY:
            return equally.split(total_amount, users)
        case SplitType.PERCENTAGE:
            return percentage.split(total_amount, users)


def split(
    total_amount: float,
    payers: dict[int, float],
    owers: dict[int, float],
    payers_split: SplitType,
    owers_split: SplitType,
) -> dict[int, dict[str, float]]:
    payers_amount = _split_by_type(total_amount, payers, payers_split)
    owers_amount = _split_by_type(total_amount, owers, owers_split)
    return amount.split(payers_amount, owers_amount)
