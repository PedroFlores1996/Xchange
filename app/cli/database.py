from typing import List
import random
import signal
import sys

import sqlalchemy
from flask_migrate import stamp
from flask.cli import AppGroup
from app.database import db
from app.split.constants import OWED, PAYED, TOTAL
from app.debt import update_debts
from app.model.group import Group
from app.model.user import User
from app.model.expense import Expense
from app.split import SplitType, equally, amount as amount_split, percentage
from app.expense.mapper import map_balances_to_model
from app.user import update_expenses_in_users

cli = AppGroup("database", help="Database commands.")


def is_db_empty() -> bool:
    table_names: List[str] = sqlalchemy.inspect(db.get_engine()).get_table_names()
    return len(table_names) == 0 or (
        len(table_names) == 1 and table_names[0] == "alembic_version"
    )


@cli.command("create-tables")
def create_tables() -> None:
    """Create all database tables."""
    if is_db_empty():
        db.create_all()
        print("All tables created successfully.")
        stamp()


@cli.command("clear-data")
def clear_data() -> None:
    """Clear all data from the database tables."""
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
    print("All data cleared successfully.")


def _create_users(count: int) -> List[User]:
    """Create a specified number of users."""
    users = []
    for i in range(1, count + 1):
        user = User.create(
            username=f"user{i}", email=f"{i}@email.com", password="password"
        )
        users.append(user)
    return users


def _create_groups(names: List[str]) -> List[Group]:
    """Create groups with the given names."""
    groups = []
    for name in names:
        group = Group(name=name)
        db.session.add(group)
        groups.append(group)
    db.session.commit()
    return groups


def _assign_users_to_groups(users: List[User], groups: List[Group], assignments: List[List[int]]) -> None:
    """Assign users to groups based on assignments list.
    assignments[i] contains the user indices for groups[i]."""
    for group_idx, user_indices in enumerate(assignments):
        for user_idx in user_indices:
            users[user_idx].add_to_group(groups[group_idx])


def _make_all_friends(users: List[User]) -> None:
    """Make all users friends with each other."""
    for user in users:
        for friend in users:
            if user != friend:
                user.add_friends(friend)
    db.session.commit()


def _create_expense_with_balances(description: str, amount: float, creator_id: int, 
                                 group_id: int, payers_split: SplitType, owers_split: SplitType,
                                 balances: dict) -> Expense:
    """Create an expense with the given parameters and update debts."""
    
    update_debts(balances, group_id)
    mapped_balances = map_balances_to_model(balances)
    
    expense = Expense.create(
        description=description,
        amount=amount,
        creator_id=creator_id,
        group_id=group_id,
        payers_split=payers_split,
        owers_split=owers_split,
        balances=mapped_balances,
    )
    
    return expense


@cli.command("test-data")
def test_data() -> None:
    """Create test data."""

    # Create users and groups
    users = _create_users(10)
    groups = _create_groups(["Group 1", "Group 2"])
    
    # Assign users to groups (first 5 to group1, last 5 to group2)
    _assign_users_to_groups(users, groups, [list(range(5)), list(range(5, 10))])
    
    # Make all users friends
    _make_all_friends(users)

    # Create expenses using helper method
    expenses = []
    
    # Expense 1: Group 1 Dinner
    balances = {
        users[0].id: {TOTAL: 100.0, PAYED: 100.0, OWED: 0.0},
        users[1].id: {TOTAL: -50.0, PAYED: 0.0, OWED: 50.0},
        users[2].id: {TOTAL: -50.0, PAYED: 0.0, OWED: 50.0},
    }
    expense1 = _create_expense_with_balances(
        "Group 1 Dinner", 100.0, users[0].id, groups[0].id,
        SplitType.EQUALLY, SplitType.EQUALLY, balances
    )
    expenses.append(expense1)

    # Expense 2: Group 2 Trip
    balances = {
        users[8].id: {TOTAL: 200.0, PAYED: 200.0, OWED: 0.0},
        users[6].id: {TOTAL: -100.0, PAYED: 0.0, OWED: 100.0},
        users[7].id: {TOTAL: -100.0, PAYED: 0.0, OWED: 100.0},
    }
    expense2 = _create_expense_with_balances(
        "Group 2 Trip", 200.0, users[5].id, groups[1].id,
        SplitType.EQUALLY, SplitType.EQUALLY, balances
    )
    expenses.append(expense2)

    # Expense 3: Coffee (no group)
    balances = {
        users[0].id: {TOTAL: 20.0, PAYED: 20.0, OWED: 0.0},
        users[3].id: {TOTAL: -20.0, PAYED: 0.0, OWED: 20.0},
    }
    expense3 = _create_expense_with_balances(
        "Coffee", 20.0, users[0].id, None,
        SplitType.EQUALLY, SplitType.EQUALLY, balances
    )
    expenses.append(expense3)

    # Expense 4: Movie Tickets (no group)
    balances = {
        users[6].id: {TOTAL: 50.0, PAYED: 50.0, OWED: 0.0},
        users[8].id: {TOTAL: -25.0, PAYED: 0.0, OWED: 25.0},
        users[9].id: {TOTAL: -25.0, PAYED: 0.0, OWED: 25.0},
    }
    expense4 = _create_expense_with_balances(
        "Movie Tickets", 50.0, users[4].id, None,
        SplitType.EQUALLY, SplitType.EQUALLY, balances
    )
    expenses.append(expense4)

    # Expense 5: Team Lunch (amount split)
    balances = {
        users[0].id: {TOTAL: 120.0, PAYED: 120.0, OWED: 0.0},
        users[1].id: {TOTAL: -60.0, PAYED: 0.0, OWED: 60.0},
        users[2].id: {TOTAL: -60.0, PAYED: 0.0, OWED: 60.0},
    }
    expense5 = _create_expense_with_balances(
        "Team Lunch", 120.0, users[0].id, groups[0].id,
        SplitType.AMOUNT, SplitType.EQUALLY, balances
    )
    expenses.append(expense5)

    # Expense 6: Office Supplies (percentage split)
    balances = {
        users[3].id: {TOTAL: 50.0, PAYED: 50.0, OWED: 0.0},
        users[4].id: {TOTAL: 50.0, PAYED: 50.0, OWED: 0.0},
        users[2].id: {TOTAL: -30.0, PAYED: 0.0, OWED: 30.0},
        users[1].id: {TOTAL: -70.0, PAYED: 0.0, OWED: 70.0},
    }
    expense6 = _create_expense_with_balances(
        "Office Supplies", 100.0, users[3].id, groups[0].id,
        SplitType.EQUALLY, SplitType.PERCENTAGE, balances
    )
    expenses.append(expense6)

    # Expense 7: Conference Tickets (percentage payers)
    balances = {
        users[7].id: {TOTAL: 120.0, PAYED: 120.0, OWED: 0.0},
        users[8].id: {TOTAL: 80.0, PAYED: 80.0, OWED: 0.0},
        users[9].id: {TOTAL: -100.0, PAYED: 0.0, OWED: 100.0},
        users[6].id: {TOTAL: -100.0, PAYED: 0.0, OWED: 100.0},
    }
    expense7 = _create_expense_with_balances(
        "Conference Tickets", 200.0, users[7].id, None,
        SplitType.PERCENTAGE, SplitType.EQUALLY, balances
    )
    expenses.append(expense7)

    # Expense 8: Shared Taxi (amount owers)
    balances = {
        users[1].id: {TOTAL: 45.0, PAYED: 45.0, OWED: 0.0},
        users[2].id: {TOTAL: 45.0, PAYED: 45.0, OWED: 0.0},
        users[3].id: {TOTAL: -30.0, PAYED: 0.0, OWED: 30.0},
        users[4].id: {TOTAL: -60.0, PAYED: 0.0, OWED: 60.0},
    }
    expense8 = _create_expense_with_balances(
        "Shared Taxi", 90.0, users[1].id, None,
        SplitType.EQUALLY, SplitType.AMOUNT, balances
    )
    expenses.append(expense8)

    # Update all expenses in users
    update_expenses_in_users(expenses)

    db.session.commit()
    print("Test data created successfully.")


@cli.command("test-data-big")
def test_data_big() -> None:
    """Create extensive test data with timeout protection."""
    
    def timeout_handler(signum, frame):
        try:
            db.session.rollback()
        except Exception:
            pass
        sys.exit(1)
    
    # Set timeout for 5 minutes (300 seconds)
    timeout_seconds = 300
    
    # Set up the timeout signal
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        # Call the actual implementation
        _test_data_big()
        
        # If we get here, it completed successfully
        signal.alarm(0)  # Cancel the alarm
        print("Extensive test data created successfully.")
        
    except KeyboardInterrupt:
        signal.alarm(0)  # Cancel the alarm
        try:
            db.session.rollback()
        except Exception:
            pass
        sys.exit(1)
        
    except Exception as e:
        signal.alarm(0)  # Cancel the alarm
        try:
            db.session.rollback()
        except Exception:
            pass
        raise


def _test_data_big() -> None:
    """Create extensive test data with many users, groups, and expenses."""
    
    # Create 50 users
    users = _create_users(50)
    
    # Create 8 groups with descriptive names
    group_names = [
        "Weekend Warriors", "Office Team", "College Friends", "Family Trip",
        "Book Club", "Hiking Group", "Cooking Club", "Gaming Squad"
    ]
    groups = _create_groups(group_names)
    
    # Assign users to groups with some overlap
    group_assignments = [
        list(range(0, 12)),      # Weekend Warriors: 12 members
        list(range(8, 20)),      # Office Team: 12 members (some overlap)
        list(range(15, 28)),     # College Friends: 13 members
        list(range(25, 35)),     # Family Trip: 10 members
        list(range(30, 42)),     # Book Club: 12 members
        list(range(35, 47)),     # Hiking Group: 12 members
        list(range(40, 50)) + list(range(0, 5)),  # Cooking Club: 15 members
        list(range(45, 50)) + list(range(0, 10))  # Gaming Squad: 15 members
    ]
    _assign_users_to_groups(users, groups, group_assignments)
    
    # Make strategic friendships (not everyone with everyone)
    for i, user in enumerate(users):
        # Add friends from same groups
        for group in user.groups:
            for group_member in group.users:
                if group_member != user and random.random() < 0.8:  # 80% chance
                    user.add_friends(group_member)
        
        # Add some random friends outside groups
        for j in range(5):  # Each user gets 5 random friends
            friend_idx = random.randint(0, len(users) - 1)
            if friend_idx != i:
                user.add_friends(users[friend_idx])
    
    db.session.commit()
    
    # Create many expenses with different patterns
    expenses = []
    expense_descriptions = [
        # Group expenses
        "Team Dinner", "Weekend Trip", "Office Lunch", "Birthday Party",
        "Concert Tickets", "Movie Night", "Grocery Shopping", "Gas Money",
        "Restaurant Bill", "Hotel Booking", "Activity Fees", "Transport",
        "Camping Supplies", "Board Games", "Pizza Party", "Coffee Run",
        "Uber Ride", "Parking Fees", "Snacks", "Drinks",
        # Individual expenses
        "Coffee", "Lunch", "Taxi", "Groceries", "Books", "Medicine",
        "Phone Bill", "Internet", "Utilities", "Rent Share"
    ]
    
    # Generate group expenses (80 expenses)
    for i in range(80):
        group = random.choice(groups)
        group_users = list(group.users)
        
        if len(group_users) < 2:
            continue
            
        # Pick random users from the group
        num_participants = random.randint(2, min(6, len(group_users)))
        participants = random.sample(group_users, num_participants)
        
        # Random expense details
        amount = round(random.uniform(20.0, 500.0), 2)
        description = random.choice(expense_descriptions)
        creator = random.choice(participants)
        
        # Random split types
        payers_split = random.choice([SplitType.EQUALLY, SplitType.AMOUNT, SplitType.PERCENTAGE])
        owers_split = random.choice([SplitType.EQUALLY, SplitType.AMOUNT, SplitType.PERCENTAGE])
        
        # Generate balances based on split types
        balances = _generate_random_balances(participants, amount, payers_split, owers_split)
        
        expense = _create_expense_with_balances(
            f"{description} #{i+1}", amount, creator.id, group.id,
            payers_split, owers_split, balances
        )
        expenses.append(expense)
    
    # Generate individual expenses (40 expenses)
    for i in range(40):
        # Pick 2-4 random users (not necessarily from same group)
        num_participants = random.randint(2, 4)
        participants = random.sample(users, num_participants)
        
        # Random expense details
        amount = round(random.uniform(10.0, 200.0), 2)
        description = random.choice(expense_descriptions)
        creator = random.choice(participants)
        
        # Random split types
        payers_split = random.choice([SplitType.EQUALLY, SplitType.AMOUNT, SplitType.PERCENTAGE])
        owers_split = random.choice([SplitType.EQUALLY, SplitType.AMOUNT, SplitType.PERCENTAGE])
        
        # Generate balances
        balances = _generate_random_balances(participants, amount, payers_split, owers_split)
        
        expense = _create_expense_with_balances(
            f"Individual {description} #{i+1}", amount, creator.id, None,
            payers_split, owers_split, balances
        )
        expenses.append(expense)
    
    # Update all expenses in users
    update_expenses_in_users(expenses)
    
    db.session.commit()


def _generate_random_balances(participants: List[User], amount: float, 
                            payers_split: SplitType, owers_split: SplitType) -> dict:
    """Generate random but valid balances for participants using the actual split functions."""
    
    # Randomly decide who are payers vs owers
    num_payers = random.randint(1, max(1, len(participants) - 1))
    payers = random.sample(participants, num_payers)
    owers = [p for p in participants if p not in payers]
    
    # If no owers, make at least one participant an ower
    if not owers:
        ower = random.choice(participants)
        owers = [ower]
        payers = [p for p in participants if p != ower]
    
    # Generate payer data using real split functions
    if payers_split == SplitType.EQUALLY:
        payer_data = {payer.id: None for payer in payers}  # equally split doesn't need values
        payer_amounts = equally.split(amount, payer_data)
    elif payers_split == SplitType.PERCENTAGE:
        # Generate random percentages that sum to 100
        payer_percentages = _generate_random_percentages(len(payers))
        payer_data = {payer.id: payer_percentages[i] for i, payer in enumerate(payers)}
        payer_amounts = percentage.split(amount, payer_data)
    else:  # AMOUNT
        # Generate random amounts that sum to total
        payer_random_amounts = _generate_random_amounts(len(payers), amount)
        payer_data = {payer.id: payer_random_amounts[i] for i, payer in enumerate(payers)}
        ower_data = {}  # No owers for this split
        result = amount_split.split(payer_data, ower_data)
        payer_amounts = {pid: result[pid][PAYED] for pid in payer_data.keys()}
    
    # Generate ower data using real split functions  
    if owers_split == SplitType.EQUALLY:
        ower_data = {ower.id: None for ower in owers}
        ower_amounts = equally.split(amount, ower_data)
    elif owers_split == SplitType.PERCENTAGE:
        ower_percentages = _generate_random_percentages(len(owers))
        ower_data = {ower.id: ower_percentages[i] for i, ower in enumerate(owers)}
        ower_amounts = percentage.split(amount, ower_data)
    else:  # AMOUNT
        ower_random_amounts = _generate_random_amounts(len(owers), amount)
        ower_data = {ower.id: ower_random_amounts[i] for i, ower in enumerate(owers)}
        payer_data = {}  # No payers for this split
        result = amount_split.split(payer_data, ower_data)
        ower_amounts = {oid: result[oid][OWED] for oid in ower_data.keys()}
    
    # Build final balances
    balances = {}
    for payer in payers:
        balances[payer.id] = {
            TOTAL: payer_amounts[payer.id],
            PAYED: payer_amounts[payer.id],
            OWED: 0.0
        }
    
    for ower in owers:
        balances[ower.id] = {
            TOTAL: -ower_amounts[ower.id],
            PAYED: 0.0,
            OWED: ower_amounts[ower.id]
        }
    
    return balances


def _generate_random_percentages(num_people: int) -> List[float]:
    """Generate random percentages that sum to 100 using tenths arithmetic."""
    
    # Work in tenths (1000 = 100.0%) to avoid floating point precision errors
    total_tenths = 1000  # 100.0% = 1000 tenths
    percentages_tenths = []
    remaining_tenths = total_tenths
    
    for i in range(num_people - 1):
        # Each person gets between 10% and 60% of remaining percentage (in tenths)
        max_tenths = min(int(remaining_tenths * 0.6), remaining_tenths - (num_people - i - 1) * 10)
        min_tenths = max(int(remaining_tenths * 0.1), 10)
        
        if max_tenths <= min_tenths:
            pct_tenths = min_tenths
        else:
            pct_tenths = random.randint(min_tenths, max_tenths)
        
        percentages_tenths.append(pct_tenths)
        remaining_tenths -= pct_tenths
    
    percentages_tenths.append(remaining_tenths)  # Last person gets remainder
    
    # Convert back to percentages
    percentages = [tenths / 10.0 for tenths in percentages_tenths]
    
    # Verify the total sums correctly (should always be true now)
    total_check = sum(percentages)
    assert abs(total_check - 100.0) < 0.05, f"Percentage generation failed: {total_check} != 100.0"
    
    return percentages


def _generate_random_amounts(num_people: int, total_amount: float) -> List[float]:
    """Generate random amounts that sum to total_amount using cents arithmetic."""
    
    # Work in cents to avoid floating point precision errors
    total_cents = round(total_amount * 100)
    amounts_cents = []
    remaining_cents = total_cents
    
    for i in range(num_people - 1):
        # Each person gets between 10% and 60% of remaining amount (in cents)
        max_cents = min(int(remaining_cents * 0.6), remaining_cents - (num_people - i - 1))
        min_cents = max(int(remaining_cents * 0.1), 1)
        
        if max_cents <= min_cents:
            amount_cents = min_cents
        else:
            amount_cents = random.randint(min_cents, max_cents)
        
        amounts_cents.append(amount_cents)
        remaining_cents -= amount_cents
    
    amounts_cents.append(remaining_cents)  # Last person gets remainder
    
    # Convert back to dollars
    amounts = [cents / 100.0 for cents in amounts_cents]
    
    # Verify the total sums correctly (should always be true now)
    total_check = sum(amounts)
    assert abs(total_check - total_amount) < 0.005, f"Amount generation failed: {total_check} != {total_amount}"
    
    return amounts


def _distribute_amount(num_people: int, total_amount: float, split_type: SplitType) -> List[float]:
    """Distribute an amount among people based on split type."""
    
    if split_type == SplitType.EQUALLY:
        # Use the same balanced rounding logic as equally.py
        base_amount_cents = int((total_amount * 100) // num_people)
        amounts_cents = [base_amount_cents] * num_people
        
        # Calculate spare cents and distribute randomly
        total_cents = int(total_amount * 100)
        distributed_cents = base_amount_cents * num_people
        spare_cents = total_cents - distributed_cents
        
        # Randomly assign spare cents
        user_indices = list(range(num_people))
        while spare_cents > 0 and user_indices:
            chosen_idx = random.choice(user_indices)
            amounts_cents[chosen_idx] += 1
            user_indices.remove(chosen_idx)
            spare_cents -= 1
            if not user_indices:  # Reset if we've used all users
                user_indices = list(range(num_people))
        
        amounts = [cents / 100.0 for cents in amounts_cents]
        return amounts
    
    elif split_type == SplitType.AMOUNT:
        # Generate random amounts that sum to total
        amounts = []
        remaining = total_amount
        for i in range(num_people - 1):
            # Each person gets between 10% and 60% of remaining amount
            max_amount = min(remaining * 0.6, remaining - (num_people - i - 1) * 0.01)
            min_amount = max(remaining * 0.1, 0.01)
            
            if max_amount <= min_amount:
                amount = min_amount
            else:
                amount = round(random.uniform(min_amount, max_amount), 2)
            
            amounts.append(amount)
            remaining -= amount
        amounts.append(round(remaining, 2))  # Last person gets remainder
        
        # Verify total and fix any rounding error
        total_distributed = sum(amounts)
        rounding_error = round(total_amount - total_distributed, 2)
        
        if rounding_error != 0.0:
            amounts[-1] = round(amounts[-1] + rounding_error, 2)
        
        return amounts
    
    elif split_type == SplitType.PERCENTAGE:
        # Generate random percentages that sum to 100%
        percentages = []
        remaining = 100.0
        for i in range(num_people - 1):
            # Each person gets between 10% and 60% of remaining percentage
            max_pct = min(remaining * 0.6, remaining - (num_people - i - 1) * 1.0)
            min_pct = max(remaining * 0.1, 1.0)
            
            if max_pct <= min_pct:
                pct = min_pct
            else:
                pct = round(random.uniform(min_pct, max_pct), 1)
            
            percentages.append(pct)
            remaining -= pct
        percentages.append(round(remaining, 1))  # Last person gets remainder
        
        # Convert percentages to amounts with balanced rounding
        raw_amounts = [total_amount * pct / 100.0 for pct in percentages]
        amounts = [round(amt, 2) for amt in raw_amounts]
        
        # Check for rounding error and fix it
        total_raw = sum(raw_amounts)
        total_rounded = sum(amounts)
        rounding_error = round(total_raw - total_rounded, 2)
        
        if rounding_error != 0.0:
            # Assign the error to the last person (could be random, but this is simpler)
            amounts[-1] = round(amounts[-1] + rounding_error, 2)
        
        return amounts
    
    return [round(total_amount / num_people, 2)] * num_people
