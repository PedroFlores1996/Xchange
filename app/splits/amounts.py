def single_payer(
    total_amount: float, payer_id: int, owed_amounts: dict[int, float]
) -> dict[int, float]:

    balances = dict.fromkeys([payer_id] + list(owed_amounts.keys()), 0)
    balances[payer_id] = total_amount
    for ower_id, amount in owed_amounts.items():
        balances[ower_id] -= amount
    return balances


def multiple_payers(
    payed_amounts: dict[int, float], owed_amounts: dict[int, float]
) -> dict[int, float]:
    balances = dict.fromkeys(payed_amounts.keys() | owed_amounts.keys(), 0)
    for id, amount in payed_amounts.items():
        balances[id] = amount
    for id, amount in owed_amounts.items():
        balances[id] -= amount
    return balances
