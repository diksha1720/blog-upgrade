from flask import Flask, render_template, request
import requests
import smtplib

app = Flask(__name__)

my_email = "Your Email"
password = "Your Password"
to_address = "Your to address"


def send_mail(msg):
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()

        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email,
                            to_addrs=to_address,
                            msg=msg)


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


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    img = "url('static/assets/img/contact-bg.jpg')"
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



if __name__ == '__main__':
    app.run(debug=True)