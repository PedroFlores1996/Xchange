from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database import db

class Debt(db.Model):
    id = Column(Integer, primary_key=True)
    lender_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    lender = db.relationship("User", foreign_keys=[lender_id], back_populates='lender_debts')
    borrower_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    borrower = db.relationship("User", foreign_keys=[borrower_id], back_populates='borrower_debts')
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    group = db.relationship("GroupDebt", uselist=False, back_populates='debt')
