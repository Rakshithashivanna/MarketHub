from extensions import db


class Order(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    product_name = db.Column(
        db.String(200)
    )

    total_price = db.Column(
        db.Float
    )

    address = db.Column(
        db.Text
    )

    phone = db.Column(
        db.String(20)
    )

    payment_method = db.Column(
        db.String(50)
    )

    status = db.Column(
        db.String(50),
        default='Pending'
    )

    user = db.relationship(
        'User'
    )