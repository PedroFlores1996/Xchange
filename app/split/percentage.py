import random


def split(total_amount: float, users: dict[int, float]) -> dict[int, float]:
    # Calculate base split for each user in cents
    base_split = {user_id: (total_amount * percentage / 100) // 0.01 
                  for user_id, percentage in users.items()}

    # Calculate the total distributed amount and the spare amount
    distributed_total = sum(base_split.values())
    spare_amount = total_amount * 100 - distributed_total

    # Assign the spare amount to a random user if it's non-zero
    if spare_amount != 0:
        spare_users = list(users.keys())
        while spare_amount > 0:
            random_user = random.choice(spare_users)
            base_split[random_user] += 1
            spare_users.remove(random_user)
            spare_amount -= 1

    return {user_id: amount / 100 for user_id, amount in base_split.items()}
