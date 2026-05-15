from extensions import db


class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200))

    price = db.Column(db.Float)

    description = db.Column(db.Text)

    image = db.Column(db.Text)
    gender = db.Column(db.String(50))

    category = db.Column(db.String(100))

    subcategory = db.Column(db.String(100))

    def __repr__(self):
        return f'<Product {self.name}>'