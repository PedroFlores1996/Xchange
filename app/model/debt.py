from sqlalchemy.orm import Mapped
from app.database import db

NO_GROUP = "no-group"


class Debt(db.Model):
    id: Mapped[int] = db.mapped_column(primary_key=True)
    lender_id: Mapped[int] = db.mapped_column(db.ForeignKey("user.id"), nullable=False)
    lender = db.relationship(
        "User", foreign_keys=[lender_id], back_populates="lender_debts"
    )
    borrower_id: Mapped[int] = db.mapped_column(
        db.ForeignKey("user.id"), nullable=False
    )
    borrower = db.relationship(
        "User", foreign_keys=[borrower_id], back_populates="borrower_debts"
    )
    amount: Mapped[float] = db.mapped_column(nullable=False)
    description: Mapped[str] = db.mapped_column(nullable=True)
    group_id: Mapped[int] = db.mapped_column(
        db.ForeignKey("group.id"), nullable=True, default=NO_GROUP
    )
    group = db.relationship("Group", back_populates="debts")
    __table_args__ = (db.UniqueConstraint("lender_id", "borrower_id", "group_id"),)

    @classmethod
    def find(cls, lender, borrower, group=None):
        return cls.query.filter_by(
            lender_id=lender.id,
            borrower_id=borrower.id,
            group_id=group.id if group else NO_GROUP,
        ).first()

    @classmethod
    def __find_reversed(cls, lender, borrower, group=None):
        return cls.find(borrower, lender, group)

    @classmethod
    def update(cls, lender, borrower, amount, description=None, group=None):
        if existing_debt := cls.find(lender, borrower, group):
            existing_debt.amount += amount
            db.session.commit()
            return

        if reverse_debt := cls.__find_reversed(lender, borrower, group):
            if reverse_debt.amount == amount:
                db.session.delete(reverse_debt)
                db.session.commit()
                return
            elif reverse_debt.amount > amount:
                reverse_debt.amount -= amount
                db.session.commit()
                return
            else:
                amount -= reverse_debt.amount
                db.session.delete(reverse_debt)
                db.session.commit()

        new_debt = cls(
            lender=lender,
            borrower=borrower,
            amount=amount,
            description=description,
            group=group,
        )
        db.session.add(new_debt)
        db.session.commit()
        return
