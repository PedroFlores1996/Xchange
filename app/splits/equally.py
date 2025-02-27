def single_payer(
    total_amount: float, payer_id: int, ower_ids: list[int]
) -> dict[int, float]:
    balances = dict.fromkeys([payer_id] + ower_ids, 0)
    balances[payer_id] = total_amount
    for id in ower_ids:
        balances[id] -= total_amount / len(ower_ids)
    return balances


def multiple_payers(
    total_amount: float, payer_ids: list[int], ower_ids: list[int]
) -> dict[int, float]:
    balances = dict.fromkeys(payer_ids + ower_ids, 0)
    for id in payer_ids:
        balances[id] = total_amount / len(payer_ids)
    for id in ower_ids:
        balances[id] -= total_amount / len(ower_ids)
    return balances
