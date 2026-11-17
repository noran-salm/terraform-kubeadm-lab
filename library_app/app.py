import os 
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-devops-key")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///library.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# -------------------- DATABASE MODELS --------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    cover_image = db.Column(db.String(300), nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_qty = db.Column(db.Integer, nullable=False)
    available_qty = db.Column(db.Integer, nullable=False)
    borrowable = db.Column(db.Boolean, default=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # 'BUY' or 'BORROW'
    status = db.Column(db.String(20), default="ACTIVE")  # 'ACTIVE', 'RETURNED', 'COMPLETED'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    book = db.relationship("Book")

# -------------------- SEED INITIAL DATA --------------------

def seed_books():
    if Book.query.count() == 0:
        sample_books = [
            Book(
                title="The Phoenix Project",
                author="Gene Kim",
                category="DevOps",
                cover_image="https://placehold.co/200x280/1e3a8a/ffffff?text=Phoenix+Project",
                price=29.99,
                total_qty=5,
                available_qty=5,
                borrowable=True,
            ),
            Book(
                title="Site Reliability Engineering",
                author="Betsy Beyer",
                category="Cloud & SRE",
                cover_image="https://placehold.co/200x280/0f766e/ffffff?text=SRE+Book",
                price=39.50,
                total_qty=3,
                available_qty=3,
                borrowable=True,
            ),
            Book(
                title="Kubernetes Up & Running",
                author="Brendan Burns",
                category="Containers",
                cover_image="https://placehold.co/200x280/4338ca/ffffff?text=Kubernetes",
                price=44.00,
                total_qty=2,
                available_qty=2,
                borrowable=False,  # Purchase only
            ),
        ]
        db.session.bulk_save_objects(sample_books)
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_books()

# -------------------- TASK 1: AUTHENTICATION --------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return redirect(url_for("register"))

        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["user_name"] = user.name
        flash(f"Welcome back, {user.name}!", "success")
        return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/")
def index():
    books = Book.query.all()
    return render_template("index.html", books=books)

@app.route("/buy/<int:book_id>", methods=["POST"])
def buy_book(book_id):
    if "user_id" not in session:
        flash("Please log in to purchase books.", "warning")
        return redirect(url_for("login"))

    book = Book.query.get_or_404(book_id)
    if book.available_qty < 1:
        flash("This book is out of stock.", "danger")
        return redirect(url_for("index"))

    book.available_qty -= 1
    book.total_qty -= 1  # Permanently sold
    tx = Transaction(
        user_id=session["user_id"], book_id=book.id, action="BUY", status="COMPLETED"
    )
    db.session.add(tx)
    db.session.commit()
    flash(f"You purchased '{book.title}'!", "success")
    return redirect(url_for("index"))

@app.route("/borrow/<int:book_id>", methods=["POST"])
def borrow_book(book_id):
    if "user_id" not in session:
        flash("Please log in to borrow books.", "warning")
        return redirect(url_for("login"))

    book = Book.query.get_or_404(book_id)
    if not book.borrowable or book.available_qty < 1:
        flash("This book cannot be borrowed right now.", "danger")
        return redirect(url_for("index"))

    book.available_qty -= 1
    tx = Transaction(
        user_id=session["user_id"], book_id=book.id, action="BORROW", status="ACTIVE"
    )
    db.session.add(tx)
    db.session.commit()
    flash(f"You borrowed '{book.title}'.", "success")
    return redirect(url_for("index"))

@app.route("/my-books")
def my_books():
    if "user_id" not in session:
        return redirect(url_for("login"))

    transactions = (
        Transaction.query.filter_by(user_id=session["user_id"])
        .order_by(Transaction.timestamp.desc())
        .all()
    )
    return render_template("my_books.html", transactions=transactions)

@app.route("/return/<int:tx_id>", methods=["POST"])
def return_book(tx_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    tx = Transaction.query.get_or_404(tx_id)
    if tx.user_id == session["user_id"] and tx.action == "BORROW" and tx.status == "ACTIVE":
        tx.status = "RETURNED"
        tx.book.available_qty += 1
        db.session.commit()
        flash(f"Returned '{tx.book.title}'. Thank you!", "success")

    return redirect(url_for("my_books"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)