import random
import math

from app.split.equally import split
from tests.splits import TOTAL_AMOUNT, id1, id2, id3, id4, id5


def test_single_payer_that_does_not_owe():
    users = {id1: 0, id2: 0, id3: 0, id4: 0, id5: 0}

    balances = split(TOTAL_AMOUNT, users)

    equal_balance = equal_amounts_between(users)
    for balance in balances.values():
        assert balance == equal_balance


def equal_amounts_between(users: dict[int, float]) -> float:
    return TOTAL_AMOUNT / len(users)


def test_1():
    total_amount = 100.0
    users = {1: None, 2: None, 3: None}

    splits = split_equally(total_amount, users)

    print(splits)
    assert sum(splits.values()) == total_amount


def test_2():
    total_amount = 100.0
    users = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None}

    splits = split_equally(total_amount, users)

    print(splits)
    assert sum(splits.values()) == total_amount


def test_3():
    total_amount = 100.0
    users = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None}
    splits = split_equally(total_amount, users)
    print(splits)
    assert sum(splits.values()) == total_amount


def test_4():
    total_amount = 100.0
    users = {
        1: None,
        2: None,
        3: None,
        4: None,
        5: None,
        6: None,
        7: None,
        8: None,
        9: None,
    }
    splits = split_equally(total_amount, users)
    print(splits)
    assert sum(splits.values()) == total_amount


def split_equally(total_amount, users):
    num_users = len(users)
    base_split = (total_amount / num_users) // 0.01
    splits = {user_id: base_split for user_id in users}

    # Calculate the total distributed amount and the spare amount
    distributed_total = base_split * num_users
    spare_amount = total_amount * 100 - distributed_total

    # Assign the spare amount to a random user if it's non-zero
    if spare_amount != 0:
        spare_users = list(users.keys())
        while spare_amount > 0:
            random_user = random.choice(spare_users)
            splits[random_user] += 1
            spare_users.remove(random_user)
            spare_amount -= 1

    return {user_id: amount / 100 for user_id, amount in splits.items()}
