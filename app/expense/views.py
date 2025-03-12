from werkzeug import Response
from flask import Blueprint, render_template
from flask_login import login_required
from app.expense import ExpenseData
from app.expense.forms import ExpenseForm
from app.expense.mapper import map_form_to_expense_data
from app.expense.submit import submit_expense
from app.model.expense import Expense
from app.model.debt import Debt
from app.model.user import User

bp = Blueprint("expense", __name__)


@bp.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses() -> str | Response:
    form = ExpenseForm()
    if form.validate_on_submit():
        data: ExpenseData = map_form_to_expense_data(form)
        expense: Expense = submit_expense(data)
        return render_template("expense/summary.html", expense=expense)
    return render_template("expense/expense.html", form=form, users=User.query.all())


@bp.route("/success")
def success():
    return "Success"


@bp.route("/debts", methods=["GET"])
@login_required
def debts() -> str | Response:
    all_debts = Debt.query.all()
    return render_template("expense/debts.html", debts=all_debts)
