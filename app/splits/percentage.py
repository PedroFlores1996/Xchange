def split(
    total_amount: float, payers: dict[int, float], owers: dict[int, float]
) -> dict[int, float]:
    payed = {k: total_amount * v / 100 for k, v in payers.items()}
    owed = {k: total_amount * v / 100 for k, v in owers.items()}
    total = payed.copy()
    total.update(
        {id: total.get(id, 0) - total_amount * v / 100 for id, v in owers.items()}
    )
    return {
        k: {"total": v, "payed": payed.get(k, 0), "owed": owed.get(k, 0)}
        for k, v in total.items()
    }
