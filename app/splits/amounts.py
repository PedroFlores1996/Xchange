from app.splits.constants import OWED, PAYED, TOTAL


def split(
    payers: dict[int, float], owers: dict[int, float]
) -> dict[int, dict[str, float]]:
    users = set(payers.keys()) | set(owers.keys())
    return {
        k: {
            PAYED: payers.get(k, 0.0),
            OWED: owers.get(k, 0.0),
            TOTAL: payers.get(k, 0.0) - owers.get(k, 0.0),
        }
        for k in users
    }
