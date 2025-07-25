from werkzeug import Response
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.expense import (
    handle_expense_creation,
    validate_expense_access,
    prepare_expense_form_data,
    prepare_expense_summary_data,
    prepare_all_debts_data,
)
from app.expense.forms import ExpenseForm
from app.group import get_authorized_group


bp = Blueprint("expense", __name__)


@bp.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses() -> str | Response:
    form = ExpenseForm()

    if form.validate_on_submit():
        result = handle_expense_creation(form)

        if result["success"]:
            template_data = prepare_expense_summary_data(result["expense"])
            return render_template("expense/summary.html", **template_data)
        else:
            flash(result["message"], result["message_type"])
            return redirect(url_for(result["redirect_to"]))
    else:
        # Flash individual field errors
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(f"{field_name.replace('_', ' ').title()}: {error}", "danger")

    # Prepare template data for the expense form
    template_data = prepare_expense_form_data(form)

    # Check for group context from URL parameter only
    if group_id_param := request.args.get("group_id"):
        try:
            group_id = int(group_id_param)
            if group := get_authorized_group(group_id):
                template_data["group"] = group
            else:
                flash("You don't have access to this group.", "danger")
                return redirect(url_for("user.user_dashboard"))
        except ValueError:
            flash("Invalid group ID provided.", "danger")
            return redirect(url_for("user.user_dashboard"))

    return render_template("expense/expense.html", **template_data)


@bp.route("/expenses/<int:expense_id>", methods=["GET"])
@login_required
def expense_summary(expense_id):
    validation = validate_expense_access(expense_id, current_user)

    if not validation["valid"]:
        flash(validation["message"], validation["message_type"])
        return redirect(url_for(validation["redirect_to"]))

    template_data = prepare_expense_summary_data(validation["expense"])
    return render_template("expense/summary.html", **template_data)


@bp.route("/success")
def success():
    return "Success"


@bp.route("/debts", methods=["GET"])
@login_required
def debts() -> str | Response:
    template_data = prepare_all_debts_data()

    if not template_data["success"]:
        flash(template_data["message"], "danger")

    return render_template("expense/debts.html", **template_data)
