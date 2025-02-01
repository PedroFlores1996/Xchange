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
    group = db.relationship("GroupDebt", uselist=False, back_populates='debt')
    __table_args__ = (db.UniqueConstraint('lender_id', 'borrower_id'),)
