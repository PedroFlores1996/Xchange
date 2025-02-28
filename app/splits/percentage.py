def single_payer(
    total_amount: float, payer_id: int, owed_percentages: dict[int, float]
) -> dict[int, float]:

    balances = dict.fromkeys([payer_id] + list(owed_percentages.keys()), 0)
    balances[payer_id] = total_amount
    for ower_id, percentage in owed_percentages.items():
        balances[ower_id] -= percentage / 100 * total_amount
    return balances


def multiple_payers(
    total_amount: float,
    payed_percentages: dict[int, float],
    owed_amounts: dict[int, float],
) -> dict[int, float]:
    balances = dict.fromkeys(payed_percentages.keys() | owed_amounts.keys(), 0)
    for id, percentage in payed_percentages.items():
        balances[id] = percentage / 100 * total_amount
    for id, percentage in owed_amounts.items():
        balances[id] -= percentage / 100 * total_amount
    return balances
