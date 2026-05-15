from extensions import db


class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(
        db.String(300)
    )

    role = db.Column(
        db.String(20),
        default='user'
    )

    def __repr__(self):

        return f'<User {self.username}>'