from app.splits import amounts


def split(
    total_amount: float, payers: dict[int, float], owers: dict[int, float]
) -> dict[int, dict[str, float]]:
    payers_amounts = {k: total_amount * v / 100 for k, v in payers.items()}
    owers_amounts = {k: total_amount * v / 100 for k, v in owers.items()}
    return amounts.split(payers_amounts, owers_amounts)
