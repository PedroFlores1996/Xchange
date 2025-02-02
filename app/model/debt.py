from sqlalchemy import Integer, String, Float
from app.database import db

class Debt(db.Model):
    id = db.Column(Integer, primary_key=True)
    lender_id = db.Column(Integer, db.ForeignKey('user.id'), nullable=False)
    lender = db.relationship("User", foreign_keys=[lender_id], back_populates='lender_debts')
    borrower_id = db.Column(Integer, db.ForeignKey('user.id'), nullable=False)
    borrower = db.relationship("User", foreign_keys=[borrower_id], back_populates='borrower_debts')
    amount = db.Column(Float, nullable=False)
    description = db.Column(String, nullable=True)
    group_id = db.Column(Integer, db.ForeignKey('group.id'), nullable=True)
    group = db.relationship("Group", back_populates='debts')
    __table_args__ = (db.UniqueConstraint('lender_id', 'borrower_id', 'group_id'),)

    def get_reversed_debt(lender_id, borrower_id):
        return Debt.get_reversed_debt(lender_id, borrower_id, None)
    
    def get_reversed_debt(lender_id, borrower_id, group_id):
        return Debt.query.filter_by(lender_id=borrower_id, borrower_id=lender_id, group_id=group_id).first()

    def update_debt(lender, borrower, amount, description=None, group=None):
        if reverse_debt := Debt.get_reversed_debt(lender.id, borrower.id, group.id if group else None):
            if reverse_debt.amount == amount:
                db.session.delete(reverse_debt)
                db.session.commit()
                return reverse_debt
            elif reverse_debt.amount > amount:
                reverse_debt.amount -= amount
                db.session.commit()
                return reverse_debt
            else:
                amount -= reverse_debt.amount
                db.session.delete(reverse_debt)
                db.session.commit()
        new_debt = Debt(lender=lender, borrower=borrower, amount=amount, description=description, group=group)
        db.session.add(new_debt)
        db.session.commit()
        return new_debt