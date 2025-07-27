from werkzeug import Response
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.expense import get_authorized_expense, prepare_all_debts_data
from app.expense.mapper import map_form_to_expense_data
from app.expense.submit import submit_expense
from app.expense.forms import ExpenseForm
from app.group import get_authorized_group


bp = Blueprint("expense", __name__)


@bp.route("/expenses", methods=["GET"])
@login_required
def expenses_get() -> str | Response:
    """Display expense creation form."""
    form = ExpenseForm()
    group = None

    # Handle group context
    if group_id_param := request.args.get("group_id"):
        try:
            if group := get_authorized_group(int(group_id_param)):
                pass  # group is already assigned
            else:
                flash("You don't have access to this group.", "danger")
                return redirect(url_for("user.user_dashboard"))
        except ValueError:
            flash("Invalid group ID provided.", "danger")
            return redirect(url_for("user.user_dashboard"))

    return render_template(
        "expense/expense.html", form=form, current_user=current_user, group=group
    )


@bp.route("/expenses", methods=["POST"])
@login_required
def expenses_post() -> str | Response:
    """Handle expense creation form submission."""
    form = ExpenseForm()

    if form.validate_on_submit():
        try:
            expense = submit_expense(map_form_to_expense_data(form))
            return render_template("expense/summary.html", expense=expense)
        except Exception as e:
            flash(f"Error creating expense: {str(e)}", "danger")
            return redirect(url_for("expense.expenses_get"))

    # Flash field errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{field.replace('_', ' ').title()}: {error}", "danger")

    return redirect(url_for("expense.expenses_get"))


@bp.route("/expenses/<int:expense_id>", methods=["GET"])
@login_required
def expense_summary(expense_id):
    expense = get_authorized_expense(expense_id, current_user)

    if not expense:
        flash("Expense not found or access denied.", "danger")
        return redirect(url_for("user.expenses"))

    return render_template("expense/summary.html", expense=expense)


@bp.route("/success")
def success():
    return "Success"


@bp.route("/debts", methods=["GET"])
@login_required
def debts() -> str | Response:
    data = prepare_all_debts_data()
    if not data["success"]:
        flash(data["message"], "danger")
    return render_template("expense/debts.html", **data)
