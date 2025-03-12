from dataclasses import dataclass
from app.model.expense import ExpenseCategory
from app.split import SplitType


@dataclass
class ExpenseData:
    amount: float
    description: str
    category: ExpenseCategory
    payers_split: SplitType
    owers_split: SplitType
    payers: dict[int, float | None]
    owers: dict[int, float | None]
    group_id: int | None
    creator_id: int
