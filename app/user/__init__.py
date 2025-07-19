from flask_login import current_user
from app.model.expense import Expense
from app.model.user import User
from app.model.constants import NO_GROUP


def update_expense_in_users(expense: Expense) -> None:
    for balance in expense.balances:
        balance.user.add_expense(expense)
    if expense not in expense.creator.expenses:
        expense.creator.add_expense(expense)


def update_expenses_in_users(expenses: list[Expense]) -> None:
    for expense in expenses:
        update_expense_in_users(expense)


def get_user_balances(user: User) -> tuple[dict[int, float], float]:
    # Initialize group balances with group IDs
    group_balances = dict.fromkeys([group.id for group in user.groups], 0.0)
    group_balances[NO_GROUP] = 0.0
    overall_balance = 0.0
    
    # Add individual debts to NO_GROUP category
    for debt in user.lender_debts:
        group_balances[NO_GROUP] += debt.amount
        overall_balance += debt.amount
    for debt in user.borrower_debts:
        group_balances[NO_GROUP] -= debt.amount
        overall_balance -= debt.amount
    
    # Add group balances from GroupBalance records
    for group_balance in user.group_balances:
        group_balances[group_balance.group_id] = group_balance.balance
        overall_balance += group_balance.balance
    
    return group_balances, overall_balance


def prepare_dashboard_data(user: User) -> dict:
    """
    Prepares all data needed for the user dashboard.
    Returns a dictionary with dashboard template data.
    """
    from app.group import get_no_group_debts
    
    # 1st Column: Debts outside any group
    no_group_debts = get_no_group_debts(user)
    no_group_debts = sorted(
        no_group_debts, key=lambda debt: abs(debt.amount), reverse=True
    )

    # 2nd Column: Groups ordered by balance or name
    group_balances, overall_balance = get_user_balances(user)
    groups_sorted = sorted(
        [group for group in user.groups if group.id != NO_GROUP],
        key=lambda group: group_balances[group.id],
        reverse=True,
    )
    no_group_balance = group_balances.pop(NO_GROUP)
    overall_group_balance = overall_balance - no_group_balance

    return {
        'current_user': user,
        'no_group_debts': no_group_debts,
        'no_group_balance': no_group_balance,
        'groups': groups_sorted,
        'group_balances': group_balances,
        'overall_group_balance': overall_group_balance,
        'expenses': user.expenses,
    }


def handle_add_friend(user: User, email: str) -> dict:
    """
    Handles the business logic for adding a friend.
    Returns a dictionary with the result status and data.
    """
    if friend := User.get_user_by_email(email):
        if friend in user.friends:
            return {
                'success': False,
                'message': f"User {friend.username} with email {email} is already your friend",
                'message_type': 'info',
                'redirect_to': 'user.add_friend_form'
            }
        else:
            user.add_friends(friend)
            return {
                'success': True,
                'message': f"User {friend.username} with email {email} added as a friend",
                'message_type': 'success',
                'redirect_to': 'user.friends'
            }
    else:
        return {
            'success': False,
            'message': f"No user found with email {email}",
            'message_type': 'danger',
            'redirect_to': 'user.add_friend_form'
        }


def prepare_friends_data(user: User) -> dict:
    """
    Prepares data for the friends page including debts and sorted friends.
    Returns a dictionary with friends template data.
    """
    from app.group import get_no_group_user_balances
    
    friends_debts = get_no_group_user_balances(user)
    friends = sorted(
        user.friends,
        key=lambda friend: abs(friends_debts.get(friend.id, 0)),
        reverse=True,
    )
    
    return {
        'friends': friends,
        'debts': friends_debts
    }


def prepare_groups_data(user: User) -> dict:
    """
    Prepares data for the user groups page.
    Returns a dictionary with groups template data.
    """
    group_balances, overall_balance = get_user_balances(user)
    groups_sorted = sorted(
        [group for group in user.groups if group.id != NO_GROUP],
        key=lambda group: group_balances[group.id],
        reverse=True,
    )
    no_group_balance = group_balances.pop(NO_GROUP)
    overall_group_balance = overall_balance - no_group_balance
    
    return {
        'current_user': user,
        'groups': groups_sorted,
        'group_balances': group_balances,
        'overall_balance': overall_group_balance,
    }


def prepare_balances_data(user: User) -> dict:
    """
    Prepares data for the user balances page.
    Returns a dictionary with balances template data.
    """
    group_balances, overall_balance = get_user_balances(user)

    # Sort group_balances by absolute balance amount in descending order
    sorted_group_balances = dict(
        sorted(group_balances.items(), key=lambda item: abs(item[1]), reverse=True)
    )

    return {
        'groups': user.groups,
        'group_balances': sorted_group_balances,
        'overall_balance': overall_balance,
    }


def validate_friend_access(user: User, user_id: int) -> dict:
    """
    Validates if the user_id represents a valid friend of the current user.
    Returns validation result and friend data if valid.
    """
    # Check if the user_id corresponds to the current_user's ID
    if user_id == user.id:
        return {
            'valid': False,
            'redirect_required': True,
            'redirect_to': 'user.user_dashboard'
        }

    # Check if the user_id belongs to one of the current_user's friends
    friend = next(
        (friend for friend in user.friends if friend.id == user_id), None
    )
    
    if not friend:
        return {
            'valid': False,
            'error': "User not found, or not added as a friend",
            'status_code': 403
        }
    
    return {
        'valid': True,
        'friend': friend
    }


def prepare_user_profile_data(user: User, friend: User) -> dict:
    """
    Prepares all data needed for a friend's profile page.
    Returns a dictionary with profile template data.
    """
    # Get all debts between the current_user and the friend
    debt_with_friend = next(
        (
            debt
            for debt in user.lender_debts + user.borrower_debts
            if debt.lender_id == friend.id or debt.borrower_id == friend.id
        ),
        None,
    )

    # Get all the current user's expenses involving the friend
    expenses_with_friend = [
        expense
        for expense in user.expenses
        if friend in [balance.user for balance in expense.balances]
    ]

    # Get common groups between current user and friend
    current_user_groups = set(user.groups)
    friend_groups = set(friend.groups)
    common_groups = list(current_user_groups.intersection(friend_groups))

    # Sort common groups by name
    common_groups.sort(key=lambda group: group.name)

    return {
        'friend': friend,
        'debt': debt_with_friend,
        'expenses': expenses_with_friend,
        'common_groups': common_groups,
    }


def validate_friend_for_settlement(user: User, friend_id: int) -> dict:
    """
    Validates if the friend_id represents a valid friend for settlement.
    Returns validation result and friend data if valid.
    """
    friend = next(
        (friend for friend in user.friends if friend.id == friend_id), None
    )
    
    if not friend:
        return {
            'valid': False,
            'message': "Friend not found",
            'message_type': 'error',
            'redirect_to': 'user.friends'
        }
    
    return {
        'valid': True,
        'friend': friend
    }


def calculate_friend_debt(user: User, friend: User) -> tuple[object, float]:
    """
    Calculates the debt between the current user and a friend.
    Returns the debt object and debt amount from current user's perspective.
    """
    # Get debt between current user and friend
    debt_with_friend = next(
        (
            debt
            for debt in user.lender_debts + user.borrower_debts
            if debt.lender_id == friend.id or debt.borrower_id == friend.id
        ),
        None,
    )

    # Calculate debt amount from current user's perspective
    if debt_with_friend:
        if debt_with_friend.lender_id == user.id:
            # Current user is owed money (positive)
            debt_amount = debt_with_friend.amount
        else:
            # Current user owes money (negative)
            debt_amount = -debt_with_friend.amount
    else:
        debt_amount = 0

    return debt_with_friend, debt_amount


def process_friend_debt_settlement(user: User, friend: User, debt_with_friend: object) -> dict:
    """
    Processes the settlement of debt between current user and friend.
    Returns the result of the settlement process.
    """
    from app.expense import ExpenseData
    from app.model.expense import ExpenseCategory
    from app.expense.submit import submit_expense
    from app.split import SplitType
    from app.database import db
    
    if not debt_with_friend:
        return {
            'success': False,
            'message': "No debt found between you and this friend",
            'message_type': 'info',
            'redirect_to': f'user.user_profile'
        }

    # Calculate settlement details
    if debt_with_friend.lender_id == user.id:
        # Current user is owed money - friend pays current user
        payer = friend
        receiver = user
        amount = debt_with_friend.amount
    else:
        # Current user owes money - current user pays friend
        payer = user
        receiver = friend
        amount = debt_with_friend.amount

    # Create settlement expense
    settlement_description = (
        f"Debt settlement between {payer.username} and {receiver.username}"
    )

    try:
        expense_data = ExpenseData(
            creator_id=user.id,
            group_id=None,  # Individual settlement, no group
            description=settlement_description,
            amount=amount,
            category=ExpenseCategory.SETTLEMENT,
            payers_split=SplitType.EQUALLY,
            owers_split=SplitType.EQUALLY,
            payers={payer.id: amount},  # Payer pays the full amount
            owers={receiver.id: amount},  # Receiver is owed the full amount
        )

        expense = submit_expense(expense_data)

        return {
            'success': True,
            'message': f"Successfully settled debt with {friend.username} for {amount:.2f}",
            'message_type': 'success',
            'redirect_to': f'user.user_profile'
        }

    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f"Error settling debt: {str(e)}",
            'message_type': 'error',
            'redirect_to': f'user.user_profile'
        }
