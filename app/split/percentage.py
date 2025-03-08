from app.split import amount


def split(
    total_amount: float, payers: dict[int, float], owers: dict[int, float]
) -> dict[int, dict[str, float]]:
    payers_amounts = {k: total_amount * v / 100 for k, v in payers.items()}
    owers_amounts = {k: total_amount * v / 100 for k, v in owers.items()}
    return amount.split(payers_amounts, owers_amounts)
