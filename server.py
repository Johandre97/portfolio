from flask import Flask, render_template, request, redirect, url_for, jsonify
import csv
import smtplib
from email.message import EmailMessage
from string import Template
from pathlib import Path
import qrcode
import requests
import hashlib
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy

load_dotenv()


# Define the Flask app
app = Flask(__name__)

# Configure the SQLAlchemy database URI and Secret Key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)

class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))

@app.route('/')
def my_home():
    return render_template('index.html')

#This is the HTML submit route for the infomation posted on the 'Contact Me' FORM
@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            write_to_csv(data)
            send_email(data)
            return redirect('thankyou.html')
        except:
            return "did not save to database"
    else:
        return 'something went wrong, try again!'

# This logs all users that use the 'Contact Me' FORM
def write_to_csv(data):
    with open('database.csv', mode='a',newline='') as database2:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        csv_writer = csv.writer(database2, delimiter=',', quotechar='|',  quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([email,subject,message])

# This sends an email to the owner when a user uses the 'Contact Me' FORM
def send_email(data):
    html = Template(Path('mail.html').read_text())

    message = EmailMessage()
    message['from'] = 'Johandre de Beer'
    message['to'] = 'johandrehdb@gmail.com'
    message['subject'] = 'New Message Request from Portfolio'
    message.set_content(html.substitute(name= data["email"], name2= data["subject"],name3 = data["message"]),'html')

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(os.getenv('SMTP_EMAIL'), os.getenv('SMTP_PASSWORD'))
        smtp.send_message(message)


# QR-code generator
@app.route('/qr_request', methods=['POST', 'GET'])
def generate_qr_code():
    if request.method == 'POST':
        try:
            link = request.form["link"]
            qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(Path('portfolio/static/assets/qr.png'))
            return redirect('thankspy.html')
        except:
            return 'Failed to generate QR-code'
    else:
        return 'Something went wrong'


# Password checker using 'HaveIBeenPWNDED' API
def request_api_data(query_char):
    url = 'https://api.pwnedpasswords.com/range/' + query_char
    res = requests.get(url)
    if res.status_code != 200:
        raise RuntimeError(f'Error fetching: {res.status_code}, check the API and try again')
    return res


def get_password_leaks_count(hashes, hash_to_check):
    hashes = (line.split(':') for line in hashes.text.splitlines())
    for h, count in hashes:
        if h == hash_to_check:
            return count
    return 0


def pwned_api_check(password):
    sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    first5_char, tail = sha1password[:5], sha1password[5:]
    response = request_api_data(first5_char)
    return get_password_leaks_count(response, tail)


@app.route('/check_passwords', methods=['POST', 'GET'])
def check_passwords():
    password = request.form['pass']
    count = pwned_api_check(password)
    if count:
        result = f'Your Password was found {count} times... you should probably change your password'
    else:
        result = f'Your Password was not found, carry on.'
    return render_template('result.html', result=result)


#The following code is to run a webscraping application
@app.route('/pywork3')
@app.route('/pywork3.html')
def spaceflight():
    try:
        response = requests.get('https://api.spaceflightnewsapi.net/v4/articles/?limit=10&search=launch')
        response.raise_for_status()
        data = response.json()
        articles = data['results']
        article_list = []
        for article in articles:
            article_data = {
                'title': article['title'],
                'url': article['url'],
                'summary': article['summary'],
                'image_url': article['image_url']
            }
            article_list.append(article_data)

        return render_template('pywork3.html', articles=article_list)
    except requests.exceptions.RequestException as e:
        # Handle request exceptions (e.g., network error, invalid URL)
        return f"Error: {e}"
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (e.g., 404, 500)
        return f"HTTP Error: {e}"
    except ValueError as e:
        # Handle JSON decoding error
        return f"JSON Decoding Error: {e}"


@app.route('/generate_card', methods=['POST'])
def generate_card():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        if not first_name or not last_name:
            return jsonify({"error": "Name and surname cannot be empty."})

        # Create a new User record in the database
        new_user = user(first_name=first_name, last_name=last_name)
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the pywork5.html page after adding the user
        return redirect(url_for('pywork5'))

    return jsonify({"error": "Invalid request."})


@app.route('/pywork5')
@app.route('/pywork5.html')
def pywork5():
    try:
        # Fetch all users from the database
        users = user.query.all()
        # Render the HTML template and pass the users data
        return render_template('pywork5.html', users=users)
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        return "An error occurred while fetching users."



@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)


if __name__ == '__main__':
    app.run()