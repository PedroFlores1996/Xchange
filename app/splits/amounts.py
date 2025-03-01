from app.splits.constants import TOTAL, PAYED, OWED


def split(
    payers: dict[int, float], owers: dict[int, float]
) -> dict[int, dict[str, float]]:
    total = {k: v for k, v in payers.items()}
    total.update({id: total.get(id, 0) - amount for id, amount in owers.items()})
    return {
        k: {TOTAL: v, PAYED: payers.get(k, 0), OWED: owers.get(k, 0)}
        for k, v in total.items()
    }
