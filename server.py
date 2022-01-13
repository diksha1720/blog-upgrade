from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import NewPostForm, LoginForm, RegisterForm
from flask_ckeditor import CKEditor, CKEditorField
import smtplib
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import html
from functools import wraps


app = Flask(__name__)
ckeditor = CKEditor(app)

Bootstrap(app)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

my_email = ""
password = ""
to_address = ""


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

# db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


def send_mail(msg):
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()

        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email,
                            to_addrs=to_address,
                            msg=msg)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    response = BlogPost.query.all()[::-1]
    img = "static/assets/img/home-bg.jpg"
    head = "Diksha's Blog"
    subhead = "Hello everyone, Welcome to my blog"
    if not current_user.is_authenticated or current_user.id != 1:
        is_admin = False
    else:
        is_admin = True
    return render_template("index.html", img=img, head=head, subhead=subhead, posts=response, logged_in=current_user.is_authenticated, is_admin=is_admin)


@app.route('/about')
def about():
    img = "static/assets/img/about-bg.jpg"
    head = "About Me"
    subhead = "This is what I do"
    return render_template("about.html", img=img, head=head, subhead=subhead, logged_in=current_user.is_authenticated)


@app.route('/post/<id>')
def post(id):
    response = BlogPost.query.get(id)
    img = response.img_url
    head = response.title
    subhead = response.subtitle
    if not current_user.is_authenticated or current_user.id != 1:
        is_admin = False
    else:
        is_admin = True
    return render_template("post.html", img=img, head=head, subhead=subhead, post=response, id=int(id), logged_in=current_user.is_authenticated, is_admin=is_admin)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    img = "static/assets/img/contact-bg.jpg"
    subhead = "Have questions? I have answers"
    if request.method == 'POST':
        send_mail(f"{request.form['name']}\n{request.form['email']}\n{request.form['phone']}\n{request.form['msg']}")
        head = "Message sent successfully"
    else:
        head = "Contact Me"
    return render_template("contact.html", img=img, head=head, subhead=subhead, logged_in=current_user.is_authenticated)


@app.route('/form-entry', methods=['POST'])
def form():
    if request.method == 'POST':
        return f"{request.form['name']}\n{request.form['email']}\n{request.form['phone']}\n{request.form['msg']}"


@app.route('/new_post', methods=['GET', 'POST'])
@admin_only
def new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        new_post = BlogPost(title=form.title.data,
                            subtitle=form.subtitle.data,
                            date=datetime.now().strftime("%B %d, %Y"),
                            body=form.body.data,
                            author=form.author.data,
                            img_url=form.img_url.data,)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        img = "static/assets/img/contact-bg.jpg"
        head = "New Post"
        subhead = "You're going to make a great blog post!"
        return render_template('new-post.html', form=form, img=img, head=head, subhead=subhead, logged_in=current_user.is_authenticated)


@app.route('/edit_post/<id>', methods=['GET', 'POST'])
@admin_only
def edit_post(id):
    post = BlogPost.query.get(id)
    editform = NewPostForm(title=post.title, subtitle=post.subtitle, img_url=post.img_url, author=post.author, body=post.body)

    if editform.validate_on_submit():
        post.title = editform.title.data
        post.subtitle = editform.subtitle.data
        post.img_url = editform.img_url.data
        post.author = editform.author.data
        post.body = editform.body.data
        db.session.commit()
        return redirect(url_for('home'))
    else:
        img = "../static/assets/img/contact-bg.jpg"
        head = "Edit Post"
        subhead = "You're going to make a great blog post!"
        return render_template('edit.html', id=id, img=img, head=head, subhead=subhead, form=editform, logged_in=current_user.is_authenticated)


@app.route('/delete_post/<ide>')
@admin_only
def delete_post(ide):
    post = BlogPost.query.get(ide)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Password incorrect, please try again.')
                return redirect(url_for('login'))
        else:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
    else:
        img = "static/assets/img/register-bg.jpg"
        head = "Login"
        subhead = "“Please think about your legacy, because you’re writing it every day.” -Gary Vaynerchuck"
        return render_template('login.html', form=form, img=img, head=head, subhead=subhead, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        else:
            hash = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
            user = User(email=form.email.data, password=hash, name=form.username.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('home'))
    else:
        img = "static/assets/img/register-bg.jpg"
        head = "Register"
        subhead = " “Champions keep playing until they get it right.” -Billie Jean King"
        return render_template('login.html', form=form, img=img, head=head, subhead=subhead)


if __name__ == '__main__':
    app.run(debug=True)
