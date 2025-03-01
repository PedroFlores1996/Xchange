def split(
    total_amount: float, payers: dict[int, float], owers: dict[int, float]
) -> dict[int, float]:
    owed = {k: total_amount / len(owers) for k, v in owers.items()}
    payed = {k: total_amount / len(payers) for k, v in payers.items()}
    total = payed.copy()
    total.update(
        {id: total.get(id, 0) - total_amount / len(owers) for id in owers.keys()}
    )
    return {
        k: {"total": v, "payed": payed.get(k, 0), "owed": owed.get(k, 0)}
        for k, v in total.items()
    }
