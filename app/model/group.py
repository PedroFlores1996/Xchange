from sqlalchemy import Integer, String
from app.database import db

# Association table
group_members = db.Table(
    "group_members",
    db.metadata,
    db.Column("user_id", Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("group_id", Integer, db.ForeignKey("group.id"), primary_key=True),
)


class Group(db.Model):
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String, nullable=False)
    description = db.Column(String, nullable=True)
    users = db.relationship("User", secondary=group_members, back_populates="groups")
    debts = db.relationship("Debt", back_populates="group")

    @classmethod
    def create_group(cls, name, description=None):
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
