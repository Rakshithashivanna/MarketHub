from extensions import db


class Cart(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('product.id')
    )

    quantity = db.Column(
        db.Integer,
        default=1
    )

    # RELATIONSHIPS

    product = db.relationship(
        'Product'
    )

    user = db.relationship(
        'User'
    )