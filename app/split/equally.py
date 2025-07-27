import random


def split(total_amount: float, users: dict[int, float | None]) -> dict[int, float]:
    num_users = len(users)

    # Convert to cents for exact arithmetic
    total_amount_cents = round(total_amount * 100)
    base_split_cents = total_amount_cents // num_users
    split = {user_id: base_split_cents for user_id in users}

    # Calculate the spare amount (remainder in cents)
    distributed_total = base_split_cents * num_users
    spare_amount = total_amount_cents - distributed_total

    # Assign the spare amount to a random user if it's non-zero
    if spare_amount != 0:
        spare_users = list(users.keys())
        while spare_amount > 0:
            random_user = random.choice(spare_users)
            split[random_user] += 1
            spare_users.remove(random_user)
            spare_amount -= 1

    return {user_id: amount / 100 for user_id, amount in split.items()}
