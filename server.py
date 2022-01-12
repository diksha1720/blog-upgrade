from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import smtplib
from datetime import datetime
import html

app = Flask(__name__)
ckeditor = CKEditor(app)

Bootstrap(app)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


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


class NewPostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


def send_mail(msg):
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()

        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email,
                            to_addrs=to_address,
                            msg=msg)


@app.route('/')
def home():
    response = BlogPost.query.all()[::-1]
    img = "static/assets/img/home-bg.jpg"
    head = "Diksha's Blog"
    subhead = "Hello everyone, Welcome to my blog"
    return render_template("index.html", img=img, head=head, subhead=subhead, posts=response)


@app.route('/about')
def about():
    img = "static/assets/img/about-bg.jpg"
    head = "About Me"
    subhead = "This is what I do"
    return render_template("about.html", img=img, head=head, subhead=subhead)


@app.route('/post/<id>')
def post(id):
    response = BlogPost.query.get(id)
    img = response.img_url
    head = response.title
    subhead = response.subtitle
    return render_template("post.html", img=img, head=head, subhead=subhead, post=response, id=int(id))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    img = "static/assets/img/contact-bg.jpg"
    subhead = "Have questions? I have answers"
    if request.method == 'POST':
        send_mail(f"{request.form['name']}\n{request.form['email']}\n{request.form['phone']}\n{request.form['msg']}")
        head = "Message sent successfully"
    else:
        head = "Contact Me"
    return render_template("contact.html", img=img, head=head, subhead=subhead)


@app.route('/form-entry', methods=['POST'])
def form():
    if request.method == 'POST':
        return f"{request.form['name']}\n{request.form['email']}\n{request.form['phone']}\n{request.form['msg']}"


@app.route('/new_post', methods=['GET','POST'])
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
        return render_template('new-post.html', form=form, img=img, head=head, subhead=subhead)


@app.route('/edit_post/<id>', methods=['GET','POST'])
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
        return render_template('edit.html', id=id, img=img, head=head, subhead=subhead, form=editform)


@app.route('/delete_post/<ide>')
def delete_post(ide):
    post = BlogPost.query.get(ide)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
