from app.split import amount


def split(
    total_amount: float, payers: dict[int, float], owers: dict[int, float]
) -> dict[int, dict[str, float]]:
    owers_amounts = {k: total_amount / len(owers) for k in owers}
    payers_amounts = {k: total_amount / len(payers) for k in payers}
    return amount.split(payers_amounts, owers_amounts)
