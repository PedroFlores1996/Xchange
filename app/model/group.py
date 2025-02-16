from sqlalchemy.orm import Mapped
from app.database import db

# Association table
group_members = db.Table(
    "group_members",
    db.metadata,
    db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
    db.Column("group_id", db.ForeignKey("group.id"), primary_key=True),
)


class Group(db.Model):
    id: Mapped[int] = db.mapped_column(primary_key=True)
    name: Mapped[str] = db.mapped_column(nullable=False)
    description: Mapped[str] = db.mapped_column(nullable=True)
    users = db.relationship("User", secondary=group_members, back_populates="groups")
    debts = db.relationship("Debt", back_populates="group")

    @classmethod
    def create(cls, name, description=None):
        new_group = cls(name=name, description=description)
        db.session.add(new_group)
        db.session.commit()
        return new_group

    def update_description(self, description):
        self.description = description
        db.session.commit()
        return self

    def add_user(self, user):
        if user not in self.users:
            self.users.append(user)
            db.session.commit()
        return self

    def remove_user(self, user):
        if user in self.users:
            self.users.remove(user)
            db.session.commit()
        if not self.users:
            db.session.delete(self)
            db.session.commit()
        return self
