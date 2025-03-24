def split(total_amount: float, users: dict[int, float | None]) -> dict[int, float]:
    return {k: total_amount / len(users) for k in users}
