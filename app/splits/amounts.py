def split(
    total_amount: float, payers: dict[int, float], owers: dict[int, float]
) -> dict[int, float]:
    balances = {k: -v for k, v in owers.items()}
    if len(payers) == 1:
        payer_id: int = next(iter(payers.keys()))
        balances[payer_id] = total_amount + balances.get(payer_id, 0)
    else:
        balances.update(
            {id: amount + balances.get(id, 0) for id, amount in payers.items()}
        )
    return balances
