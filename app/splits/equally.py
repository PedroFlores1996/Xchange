def split(
    total_amount: float, payers: dict[int, float], owers: dict[int, float]
) -> dict[int, float]:
    balances = dict.fromkeys(owers.keys(), -total_amount / len(owers))
    if len(payers) == 1:
        payer_id: int = next(iter(payers.keys()))
        balances[payer_id] = total_amount + balances.get(payer_id, 0)
    else:
        balances.update(
            {
                id: total_amount / len(payers) + balances.get(id, 0)
                for id in payers.keys()
            }
        )
    return balances
