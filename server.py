from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route('/')
def home():
    response = requests.get("https://api.npoint.io/4c1b65cf4e0734179b77").json()
    img = "url('static/assets/img/home-bg.jpg')"
    head = "Diksha's Blog"
    subhead = "Hello everyone, Welcome to my blog"
    return render_template("index.html", img=img, head=head, subhead=subhead, posts=response)


@app.route('/about')
def about():
    img = "url('static/assets/img/about-bg.jpg')"
    head = "About Me"
    subhead = "This is what I do"
    return render_template("about.html", img=img, head=head, subhead=subhead)

images = ["url('../static/assets/img/cactus.jpg')", "url('../static/assets/img/bored.jpg')", "url('../static/assets/img/fasting.jpg')"]
@app.route('/post/<id>')
def post(id):
    response = requests.get("https://api.npoint.io/4c1b65cf4e0734179b77").json()
    img = images[int(id)-1]
    head = response[int(id)-1]["title"]
    subhead = response[int(id)-1]["subtitle"]
    return render_template("post.html", img=img, head=head, subhead=subhead, posts=response, id=int(id))


@app.route('/contact')
def contact():
    img = "url('static/assets/img/contact-bg.jpg')"
    head = "Contact Me"
    subhead = "Have questions? I have answers"
    return render_template("contact.html", img=img, head=head, subhead=subhead)


if __name__ == '__main__':
    app.run(debug=True)