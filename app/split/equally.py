import random


def split(total_amount: float, users: dict[int, float | None]) -> dict[int, float]:
    num_users = len(users)

    base_split = (total_amount / num_users) // 0.01
    split = {user_id: base_split for user_id in users}

    # Calculate the total distributed amount and the spare amount
    distributed_total = base_split * num_users
    spare_amount = total_amount * 100 - distributed_total

    # Assign the spare amount to a random user if it's non-zero
    if spare_amount != 0:
        spare_users = list(users.keys())
        while spare_amount > 0:
            random_user = random.choice(spare_users)
            split[random_user] += 1
            spare_users.remove(random_user)
            spare_amount -= 1

    return {user_id: amount / 100 for user_id, amount in split.items()}
