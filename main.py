from datetime import date, datetime
import os
from dotenv import load_dotenv
import tempfile

from dominate.tags import comment
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor

from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps

from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from form import DiscussForm, DiscussRegistrationForm, DiscussLoginForm , DiscussCommentForm


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
Bootstrap5(app)
ckeditor = CKEditor(app)

# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))

# use function decoration to create a function that can give ony an admin access
def admin_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)

        if current_user.id != 1:
            abort(403)

        return function(*args, **kwargs)

    return wrapper


#DataBase
class Base(DeclarativeBase):
    pass

database_url = os.getenv("DATABASE_URI")


app.config["SQLALCHEMY_DATABASE_URI"] = database_url

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CONFIGURE TABLE
class DiscussPost(db.Model):
    __tablename__ = "discuss_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("Users", back_populates="posts")
    # ***************Parent Relationship*************#
    comments = relationship("Comments", back_populates="parent_post")


# USERS TABLE
class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    surname: Mapped[str] = mapped_column(String(100))
    firstname: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(100))
    posts = relationship("DiscussPost", back_populates="author")
    comments = relationship("Comments", back_populates="comment_author")

class Comments(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("Users", back_populates="comments")

    # ***************Child Relationship*************#
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("discuss_posts.id"))
    parent_post = relationship("DiscussPost", back_populates="comments")
    text: Mapped[str] = mapped_column(Text, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def landing_page():
    return render_template("landing-page.html")


@app.route('/home')
def home_page():
    result = db.session.execute(db.select(DiscussPost))
    posts = result.scalars().all()

    return render_template('index.html', posts=posts, logged_in = current_user.is_authenticated)


@app.route('/register-user', methods=['GET', 'POST'])
def register_user():
    reg_form = DiscussRegistrationForm()
    if reg_form.validate_on_submit():
        hash_and_salted_password = generate_password_hash(
            reg_form.password.data,
            method='pbkdf2:sha256',
            salt_length=8)

        existing_email = db.session.execute(db.select(Users).where(Users.email == reg_form.email.data)).scalar()
        if existing_email:
            flash('Email address already registered!, Login instead', 'danger')
            return redirect(url_for('login'))
        else:
            new_user = Users(
                email=reg_form.email.data,
                password=hash_and_salted_password,
                surname=reg_form.surname.data,
                firstname=reg_form.firstname.data,
                username=reg_form.username.data
            )
            db.session.add(new_user)
            db.session.commit()
            flash('You have successfully registered!', 'success')
            return redirect(url_for('login'))

    return render_template('registration-page.html', regis_form=reg_form,logged_in = current_user.is_authenticated)


@app.route('/login-user', methods=['GET', 'POST'])
def login():
    log_form = DiscussLoginForm()
    if log_form.validate_on_submit():
        email = log_form.email.data
        password = log_form.password.data

        user = db.session.execute(db.select(Users).where(Users.email == email)).scalar()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home_page"))
        else:
            flash("Invalid username or password", "danger")

    return render_template('login-page.html', login_form=log_form,logged_in = current_user.is_authenticated )


@app.route('/show-discuss/<int:discuss_id>', methods=['GET', 'POST'])
def show_discuss(discuss_id):
    post = db.get_or_404(DiscussPost, discuss_id)
    comment_form = DiscussCommentForm()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.", 'danger')
            return redirect(url_for("login"))
        new_comment = Comments(
            text=comment_form.body.data,
            comment_author=current_user,
            parent_post= post
        )
        db.session.add(new_comment)
        db.session.commit()


    return render_template('post.html', discuss_post=post,comment_form = comment_form, logged_in = current_user.is_authenticated)


@app.route('/discuss-post', methods=['GET', 'POST'])
@login_required
def discuss_post():
    discuss_form = DiscussForm()
    if discuss_form.validate_on_submit():
        new_post = DiscussPost(
            body=discuss_form.post.data,
            date=date.today().strftime("%B %d, %Y"),
            author=current_user,
            title=discuss_form.title.data,
            subtitle=discuss_form.subtitle.data,
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home_page"))
    return render_template('create_post.html', discuss_form=discuss_form, logged_in = current_user.is_authenticated)

@app.route("/about")
@login_required
def about():
    return render_template("about.html", logged_in = current_user.is_authenticated)


@app.route("/contact")
@login_required
def contact():
    return render_template("contact.html", logged_in = current_user.is_authenticated)


@app.route("/delete/<int:discuss_id>")
@admin_only
def delete_post(discuss_id):
    post_to_delete = db.get_or_404(DiscussPost, discuss_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('landing-page.html')


if __name__ == "__main__":
    app.run(debug=False, port=5000)
