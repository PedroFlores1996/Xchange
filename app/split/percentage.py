def split(total_amount: float, users: dict[int, float]) -> dict[int, float]:
    return {k: total_amount * v / 100 for k, v in users.items()}
