from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import re

# DATABASE
from extensions import db

# MODELS
from models.user import User
from models.product import Product
from models.cart import Cart
from models.order import Order
from models.review import Review


# CREATE FLASK APP
app = Flask(__name__)

# LOAD CONFIGURATION
app.config.from_object(Config)

# INITIALIZE DATABASE
db.init_app(app)

# SECRET KEY
app.secret_key = 'markethub'


# HOME PAGE
@app.route('/')
def home():

    products = Product.query.all()

    return render_template(
        'index.html',
        products=products
    )


# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')

        password = request.form.get('password')

        # FIND USER
        user = User.query.filter_by(
            email=email
        ).first()

        # CHECK PASSWORD
        if user and check_password_hash(
            user.password,
            password
        ):

            # CREATE SESSION
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            # ADMIN
            if user.role == 'admin':

                return redirect('/admin')

            # STAFF
            if user.role == 'staff':

                return redirect('/staff')

            # CUSTOMER
            return redirect('/')

        else:

            flash("Invalid Email or Password")

            return redirect('/login')

    return render_template('login.html')


# LOGOUT
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


# REGISTER PAGE
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username')

        email = request.form.get('email')

        password = request.form.get('password')

        confirm_password = request.form.get(
            'confirm_password'
        )

        # EMPTY FIELD CHECK
        if not username or not email or not password:

            flash("All fields are required")

            return redirect('/register')

        # EMAIL VALIDATION
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(email_pattern, email):

            flash("Invalid email format")

            return redirect('/register')

        # PASSWORD MATCH CHECK
        if password != confirm_password:

            flash("Passwords do not match")

            return redirect('/register')

        # EMAIL EXISTS CHECK
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash("Email already registered")

            return redirect('/register')

        # HASH PASSWORD
        hashed_password = generate_password_hash(
            password
        )

        # CREATE USER
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            role='customer'
        )

        # SAVE USER
        db.session.add(new_user)

        db.session.commit()

        flash("Registration Successful")

        return redirect('/login')

    return render_template('register.html')

@app.route('/profile')
def profile():

    # LOGIN CHECK
    if 'user_id' not in session:

        return redirect('/login')

    user = User.query.get(
        session['user_id']
    )

    return render_template(
        'profile.html',
        user=user
    )

# CART PAGE
@app.route('/cart')
def cart():

    if 'user_id' not in session:

        return redirect('/login')

    cart_items = Cart.query.filter_by(
        user_id=session['user_id']
    ).all()

    total = 0

    for item in cart_items:

        total += item.product.price * item.quantity

    return render_template(
        'cart.html',
        cart_items=cart_items,
        total=total
    )


# ADMIN DASHBOARD
@app.route('/admin')
def admin():

    # ADMIN CHECK
    if session.get('role') != 'admin':

        return redirect('/login')

    return render_template(
        'admin/dashboard.html'
    )


# STAFF DASHBOARD
@app.route('/staff')
def staff():

    # STAFF CHECK
    if session.get('role') != 'staff':

        return redirect('/login')

    return render_template(
        'staff/staff_dashboard.html'
    )

@app.route('/search')
def search():

    query = request.args.get('query')

    products = Product.query.filter(
        Product.name.ilike(f'%{query}%')
    ).all()

    return render_template(
        'search_results.html',
        products=products,
        query=query
    )


# ADD PRODUCT
@app.route('/add-product', methods=['GET', 'POST'])
def add_product():

    # ADMIN / STAFF CHECK
    if session.get('role') not in ['admin', 'staff']:

        return redirect('/login')

    if request.method == 'POST':

        name = request.form.get('name')

        price = request.form.get('price')

        description = request.form.get('description')

        image = request.form.get('image')

        

        category = request.form.get('category')
        gender = request.form.get('gender')

        subcategory = request.form.get('subcategory')

        # CREATE PRODUCT
        new_product = Product(
            name=name,
            price=price,
            description=description,
            image=image,
            category=category,
            gender=gender,
            subcategory=subcategory
        )

        # SAVE PRODUCT
        db.session.add(new_product)

        db.session.commit()

        flash("Product Added Successfully")

        # STAFF REDIRECT
        if session.get('role') == 'staff':

            return redirect('/staff')

        # ADMIN REDIRECT
        return redirect('/admin')

    return render_template(
        'admin/add_product.html'
    )


# MANAGE PRODUCTS
@app.route('/manage-product')
def manage_products():

    # ADMIN / STAFF CHECK
    if session.get('role') not in ['admin', 'staff']:

        return redirect('/login')

    products = Product.query.all()

    return render_template(
        'admin/manage_products.html',
        products=products
    )


# DELETE PRODUCT
@app.route('/delete-product/<int:id>')
def delete_product(id):

    # ADMIN / STAFF CHECK
    if session.get('role') not in ['admin', 'staff']:

        return redirect('/login')

    # FIND PRODUCT
    product = Product.query.get_or_404(id)

    # DELETE PRODUCT
    db.session.delete(product)

    # SAVE DATABASE
    db.session.commit()

    flash("Product Deleted Successfully")

    return redirect('/manage-product')


@app.route('/edit-product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):

    # ADMIN / STAFF CHECK
    if session.get('role') not in ['admin', 'staff']:

        return redirect('/login')

    # FIND PRODUCT
    product = Product.query.get_or_404(id)

    # UPDATE PRODUCT
    if request.method == 'POST':

        product.name = request.form.get('name')

        product.price = request.form.get('price')

        product.description = request.form.get(
            'description'
        )

        product.image = request.form.get('image')

        product.category = request.form.get('category')

        product.gender = request.form.get('gender')

        product.subcategory = request.form.get(
            'subcategory'
        )

        db.session.commit()

        flash("Product Updated Successfully")

        return redirect('/manage-product')

    return render_template(
        'admin/edit_product.html',
        product=product
    )

# PRODUCT DETAILS
@app.route('/product/<int:id>')
def product_details(id):

    product = Product.query.get_or_404(id)

    return render_template(
        'product_details.html',
        product=product
    )


# CATEGORY PRODUCTS
@app.route('/category/<string:category_name>')
def category_products(category_name):

    if category_name == 'Fashion':

        genders = ['Men', 'Women']

        return render_template(
            'fashion_gender.html',
            genders=genders
        )

    products = Product.query.filter_by(
        category=category_name
    ).all()

    subcategories = []

    for product in products:
        if product.subcategory not in subcategories:
            subcategories.append(product.subcategory)

    return render_template(
        'gender_products.html',
        subcategories=subcategories,
        category_name=category_name,
        gender='Unisex'
    )

#gender
@app.route('/category/<string:category_name>/<string:gender>')
def gender_products(category_name, gender):

    products = Product.query.filter_by(
        category=category_name,
        gender=gender
    ).all()

    subcategories = []

    for product in products:

        if product.subcategory not in subcategories:
            subcategories.append(product.subcategory)

    return render_template(
        'gender_products.html',
        subcategories=subcategories,
        category_name=category_name,
        gender=gender
    )

# SUBCATEGORY PRODUCTS
@app.route('/subcategory/<string:category_name>/<string:gender>/<string:subcategory_name>')
def subcategory_products(category_name, gender, subcategory_name):

    products = Product.query.filter_by(
        category=category_name,
        gender=gender,
        subcategory=subcategory_name
    ).all()

    return render_template(
        'subcategory_products.html',
        products=products,
        subcategory_name=subcategory_name
    )


# ADD TO CART
@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):

    # LOGIN CHECK
    if 'user_id' not in session:

        return redirect('/login')

    product = Product.query.get_or_404(
        product_id
    )

    # CHECK EXISTING ITEM
    existing_item = Cart.query.filter_by(
        user_id=session['user_id'],
        product_id=product.id
    ).first()

    # IF EXISTS
    if existing_item:

        existing_item.quantity += 1

    else:

        cart_item = Cart(
            user_id=session['user_id'],
            product_id=product.id,
            quantity=1
        )

        db.session.add(cart_item)

    db.session.commit()

    return redirect('/cart')


# REMOVE FROM CART
@app.route('/remove-from-cart/<int:id>')
def remove_from_cart(id):

    cart_item = Cart.query.get_or_404(id)

    db.session.delete(cart_item)

    db.session.commit()

    return redirect('/cart')


# CHECKOUT
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():

    # LOGIN CHECK
    if 'user_id' not in session:
        return redirect('/login')

    cart_items = Cart.query.filter_by(
        user_id=session['user_id']
    ).all()

    total = 0

    for item in cart_items:
        total += item.product.price * item.quantity

    # PLACE ORDER
    if request.method == 'POST':

        address = request.form.get('address')

        phone = request.form.get('phone')

        payment_method = request.form.get(
            'payment_method'
        )

        # CREATE ORDER FOR EACH PRODUCT
        for item in cart_items:

            new_order = Order(
                user_id=session['user_id'],
                product_name=item.product.name,
                total_price=item.product.price * item.quantity,
                address=address,
                phone=phone,
                payment_method=payment_method
            )

            db.session.add(new_order)

        # CLEAR CART
        for item in cart_items:
            db.session.delete(item)

        db.session.commit()

        return redirect('/success')

    return render_template(
        'checkout.html',
        cart_items=cart_items,
        total=total
    )


# SUCCESS PAGE
@app.route('/success')
def success():

    return render_template(
        'success.html'
    )


# ADMIN ORDERS
@app.route('/admin-orders')
def admin_orders():

    # ADMIN CHECK
    if session.get('role') != 'admin':

        return redirect('/login')

    orders = Order.query.all()

    return render_template(
        'admin/manage_orders.html',
        orders=orders
    )


# STAFF ORDERS
@app.route('/staff-orders')
def staff_orders():

    # STAFF CHECK
    if session.get('role') != 'staff':

        return redirect('/login')

    orders = Order.query.all()

    return render_template(
        'staff/staff_orders.html',
        orders=orders
    )


# UPDATE ORDER STATUS
@app.route('/update-order-status/<int:id>/<string:status>')
def update_order_status(id, status):

    # ADMIN / STAFF CHECK
    if session.get('role') not in ['admin', 'staff']:

        return redirect('/login')

    order = Order.query.get_or_404(id)

    order.status = status

    db.session.commit()

    # STAFF REDIRECT
    if session.get('role') == 'staff':

        return redirect('/staff-orders')

    # ADMIN REDIRECT
    return redirect('/admin-orders')


# MY ORDERS
@app.route('/my-orders')
def my_orders():

    # LOGIN CHECK
    if 'user_id' not in session:

        return redirect('/login')

    orders = Order.query.filter_by(
        user_id=session['user_id']
    ).all()

    return render_template(
        'orders.html',
        orders=orders
    )


# MANAGE USERS
@app.route('/manage-users')
def manage_users():

    # ADMIN CHECK
    if session.get('role') != 'admin':

        return redirect('/login')

    users = User.query.all()

    return render_template(
        'admin/manage_users.html',
        users=users
    )

@app.route('/cancel-order/<int:id>')
def cancel_order(id):

    if 'user_id' not in session:
        return redirect('/login')

    order = Order.query.get_or_404(id)

    if order.user_id != session['user_id']:
        return redirect('/my-orders')

    if order.status in ['Pending', 'Approved']:
        order.status = 'Cancelled'
        db.session.commit()

    return redirect('/my-orders')

@app.route('/review/<int:order_id>', methods=['GET', 'POST'])
def review(order_id):

    if 'user_id' not in session:
        return redirect('/login')

    order = Order.query.get_or_404(order_id)

    if order.status != 'Delivered':
        return redirect('/my-orders')

    if request.method == 'POST':

        rating = request.form.get('rating')
        comment = request.form.get('comment')

        review = Review(
            user_id=session['user_id'],
            product_name=order.product_name,
            order_id=order.id,
            rating=rating,
            comment=comment
        )

        db.session.add(review)
        db.session.commit()

        return redirect('/my-orders')

    return render_template(
        'review.html',
        order=order
    )

@app.route('/manage-reviews')
def manage_reviews():

    if session.get('role') != 'admin':
        return redirect('/login')

    reviews = Review.query.all()
    users = User.query.all()

    user_dict = {}

    for user in users:
        user_dict[user.id] = user.username

    return render_template(
        'admin/manage_reviews.html',
        reviews=reviews,
        user_dict=user_dict
    )


# CREATE DATABASE TABLES
with app.app_context():

    db.create_all()


# RUN SERVER
if __name__ == '__main__':

    app.run(debug=True)