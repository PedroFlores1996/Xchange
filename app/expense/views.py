from werkzeug import Response
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.expense import (
    handle_expense_creation,
    validate_expense_access,
    prepare_expense_form_data,
    prepare_expense_summary_data,
    prepare_all_debts_data
)
from app.expense.forms import ExpenseForm


bp = Blueprint("expense", __name__)


@bp.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses() -> str | Response:
    form = ExpenseForm()
    
    if form.validate_on_submit():
        result = handle_expense_creation(form)
        
        if result['success']:
            template_data = prepare_expense_summary_data(result['expense'])
            return render_template("expense/summary.html", **template_data)
        else:
            flash(result['message'], result['message_type'])
            return redirect(url_for(result['redirect_to']))
    elif form.errors:
        # Flash individual field errors
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(f"{field_name.replace('_', ' ').title()}: {error}", 'danger')
    
    # Check for group context - first from URL parameter, then from referrer
    group_id_from_context = None
    
    # Check URL parameter first (explicit)
    group_id_param = request.args.get('group_id')
    if group_id_param:
        try:
            group_id_from_context = int(group_id_param)
        except ValueError:
            pass
    
    # If no URL param, check referrer
    if not group_id_from_context:
        referrer = request.referrer
        if referrer:
            # Check if referrer contains a group ID pattern like /groups/{id}
            import re
            group_match = re.search(r'/groups/(\d+)', referrer)
            if group_match:
                group_id_from_context = int(group_match.group(1))
    
    # Verify user has access to the group if one was found
    group = None
    if group_id_from_context:
        from app.model.group import Group
        group = Group.query.filter_by(id=group_id_from_context).first()
        if not group or current_user not in group.users:
            group_id_from_context = None
            group = None
    
    template_data = prepare_expense_form_data(current_user)
    if group_id_from_context and group:
        template_data['pre_selected_group_id'] = group_id_from_context
        template_data['group'] = group
    
    return render_template("expense/expense.html", **template_data)


@bp.route("/expenses/<int:expense_id>", methods=["GET"])
@login_required
def expense_summary(expense_id):
    validation = validate_expense_access(expense_id, current_user)
    
    if not validation['valid']:
        flash(validation['message'], validation['message_type'])
        return redirect(url_for(validation['redirect_to']))
    
    template_data = prepare_expense_summary_data(validation['expense'])
    return render_template("expense/summary.html", **template_data)


@bp.route("/success")
def success():
    return "Success"


@bp.route("/debts", methods=["GET"])
@login_required
def debts() -> str | Response:
    template_data = prepare_all_debts_data()
    
    if not template_data['success']:
        flash(template_data['message'], 'danger')
    
    return render_template("expense/debts.html", **template_data)
