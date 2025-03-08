from werkzeug import Response
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from app.expense.forms import ExpenseForm
from app.expense.mapper import ExpenseData, expense_data_from
from app.expense.processor import create_expense_from
from app.model.expense import Expense
from app.model.debt import Debt

bp = Blueprint("expense", __name__)


@bp.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses() -> str | Response:
    form = ExpenseForm()
    if form.validate_on_submit():
        data: ExpenseData = expense_data_from(form)
        expense: Expense = create_expense_from(data)
        return render_template("expense/summary.html", expense=expense)
    return render_template("expense/expense.html", form=form)


@bp.route("/success")
def success():
    return "Success"


@bp.route("/debts", methods=["GET"])
@login_required
def debts() -> str | Response:
    all_debts = Debt.query.all()
    return render_template("expense/debts.html", debts=all_debts)
