from sqlalchemy import Integer, String
from app.database import db

# Association table
group_members = db.Table('group_members', db.metadata,
    db.Column('user_id', Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', Integer, db.ForeignKey('group.id'), primary_key=True)
)

class Group(db.Model):
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String, nullable=False)
    description = db.Column(String, nullable=True)
    users = db.relationship("User", secondary=group_members, back_populates='groups')
    debts = db.relationship("GroupDebt", back_populates='group')

class GroupDebt(db.Model):
    id = db.Column(Integer, primary_key=True)
    group_id = db.Column(Integer, db.ForeignKey('group.id'), nullable=False)
    group = db.relationship("Group", back_populates='debts')
    debt_id = db.Column(Integer, db.ForeignKey('debt.id'), nullable=False)
    debt = db.relationship("Debt", back_populates='group')

