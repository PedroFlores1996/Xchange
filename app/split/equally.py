def split(total_amount: float, users: dict[int, float]) -> dict[int, float]:
    return {k: total_amount / len(users) for k in users}
