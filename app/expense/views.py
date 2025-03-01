from werkzeug import Response
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from app.expense.forms import ExpenseForm
from app.expense.mapper import ExpenseData, extract_from

bp = Blueprint("expense", __name__)


@bp.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses() -> str | Response:
    form = ExpenseForm()
    if form.validate_on_submit():
        data: ExpenseData = extract_from(form)

        return redirect(url_for("expense.success"))
    return render_template("expense/expense.html", form=form)


@bp.route("/success")
def success():
    return "Success"
