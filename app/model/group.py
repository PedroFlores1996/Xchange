from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import db

# Association table
group_members = db.Table('group_members', db.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('group.id'), primary_key=True)
)

class Group(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    users = db.relationship("User", secondary=group_members, back_populates='groups')
    debts = db.relationship("GroupDebt", back_populates='group')

class GroupDebt(db.Model):
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('group.id'), nullable=False)
    group = db.relationship("Group", back_populates='debts')
    debt_id = Column(Integer, ForeignKey('debt.id'), nullable=False)
    debt = db.relationship("Debt", back_populates='group')

