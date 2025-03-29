from werkzeug import Response
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.expense import ExpenseData
from app.expense.forms import ExpenseForm
from app.expense.mapper import map_form_to_expense_data
from app.expense.submit import submit_expense
from app.model.expense import Expense
from app.model.debt import Debt


bp = Blueprint("expense", __name__)


@bp.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses() -> str | Response:
    form = ExpenseForm()
    if form.validate_on_submit():
        data: ExpenseData = map_form_to_expense_data(form)
        expense: Expense = submit_expense(data)
        return render_template("expense/summary.html", expense=expense)
    return render_template("expense/expense.html", form=form, current_user=current_user)


@bp.route("/expenses/<int:expense_id>", methods=["GET"])
@login_required
def expense_summary(expense_id):
    # Fetch the expense by ID
    expense = next((e for e in current_user.expenses if e.id == expense_id), None)

    # If the expense does not exist or does not belong to the current user, show a 404 error
    if not expense:
        flash("Expense not found or you do not have access to it.", "danger")
        return redirect(url_for("user.expenses"))

    # Render the summary template with the expense details
    return render_template("expense/summary.html", expense=expense)


@bp.route("/success")
def success():
    return "Success"


@bp.route("/debts", methods=["GET"])
@login_required
def debts() -> str | Response:
    all_debts = Debt.query.all()
    return render_template("expense/debts.html", debts=all_debts)
