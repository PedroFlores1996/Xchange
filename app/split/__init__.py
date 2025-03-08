from app.enum import FormEnum
from . import amount, equally, percentage


class SplitType(FormEnum):
    AMOUNT = "Amount"
    EQUALLY = "Equally"
    PERCENTAGE = "Percentage"


def split(
    total_amount: float, payers: list, owers: list, split_type: SplitType
) -> dict[int, dict[str, float]]:
    match split_type:
        case SplitType.EQUALLY:
            return equally.split(total_amount, payers, owers)
        case SplitType.AMOUNT:
            return amount.split(payers, owers)
        case SplitType.PERCENTAGE:
            return percentage.split(total_amount, payers, owers)
        case _:
            raise ValueError(f"Unknown split type: {split_type}")
