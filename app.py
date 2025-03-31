from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask_wtf import CSRFProtect
from mailjet_rest import Client
from dotenv import load_dotenv
from flask import send_from_directory
import logging
import stripe

load_dotenv()  # This should come before accessing the environment variables
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Configure the Secret Key and the SQLAlchemy database URI
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://PVschool:postgres@PVschool.mysql.pythonanywhere-services.com/PVschool$apschool'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_DEFAULT_SENDER'] = "alagupl2710@gmail.com"

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Mailjet configuration
api_key = os.getenv('MAILJET_API_KEY')
api_secret = os.getenv('MAILJET_API_SECRET')
mailjet_client = Client(auth=(api_key, api_secret), version='v3.1')

stripe.api_key = os.getenv('STRIPE_API_KEY')

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    country_code = db.Column(db.String(5), nullable=False)
    phone = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    address = db.Column(db.Text, nullable=False)
    course = db.Column(db.String(50), nullable=False)
    graduated = db.Column(db.Boolean, nullable=False)
    tenth_score = db.Column(db.Float, nullable=False)
    twelfth_score = db.Column(db.Float, nullable=False)
    group = db.Column(db.String(50), nullable=False)
    slot = db.Column(db.String(50), nullable=False)
    college = db.Column(db.String(255), nullable=True)  # 🟢 Ensure this column is present
    amount = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Contact(db.Model):
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database context
with app.app_context():
    db.create_all()

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/check-email')
def check_email():
    email = request.args.get('email')
    if not email:
        return jsonify({'exists': False})

    exists = Student.query.filter_by(email=email).first()
    return jsonify({'exists': bool(exists)})

@app.route('/check-phone')
def check_phone():
    phone = request.args.get('phone')
    if not phone:
        return jsonify({'exists': False})

    exists = Student.query.filter_by(phone=phone).first()
    return jsonify({'exists': bool(exists)})


# @app.route('/d48dc6fb61cec79bd7d53f20de7b9bb9.txt')
# def serve_verification_file():
#     return send_from_directory(os.path.dirname(__file__), 'd48dc6fb61cec79bd7d53f20de7b9bb9.txt')
VALID_PAYMENT_METHODS = ["card"]  # Google Pay is supported through "card"

COURSE_PRICES = {
    "Internet of Things": 1200000,    # ₹12000
    "Machine Learning": 1400000,     # ₹14000
    "Artifical Intelligence": 1600000,     # ₹16000
    "Java": 1500000,   # ₹15000
    "Python": 1500000, # ₹15000
    "Frontend": 1500000, # ₹15000
    "Agile": 1000000,
    "Jira": 800000,
    "BigData": 1400000,
    "React": 1400000,
    "MicroservicesApi": 1200000,
    "RestApi": 800000,
    "CA": 2000000
}

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         form_data = request.form.to_dict()

#         # Clean and normalize data
#         form_data['email'] = form_data['email'].strip().lower()
#         form_data['phone'] = form_data['phone'].strip()

#         # Pre-check with case-insensitive email comparison
#         existing = Student.query.filter(
#             (db.func.lower(Student.email) == form_data['email']) |
#             (Student.phone == form_data['phone'])
#         ).first()

#         if existing:
#             flash('This email or phone is already registered', 'error')
#             return render_template('register.html', form_data=form_data)

#         try:
#             # Validate and convert data
#             dob = datetime.strptime(form_data['dob'], '%d/%m/%Y').date()
#             # year = int(form_data['year'])
#             tenth_score = float(form_data['tenth'])
#             twelfth_score = float(form_data['twelfth'])
#             graduated = form_data.get('graduated') == 'yes'

#             # Create student object
#             student = Student(
#                 name=form_data['name'],
#                 dob=dob,
#                 country_code=form_data['country_code'],
#                 phone=form_data['phone'],
#                 email=form_data['email'],
#                 address=form_data['address'],
#                 course=form_data['course'],
#                 # year=year,
#                 graduated=graduated,
#                 tenth_score=tenth_score,
#                 twelfth_score=twelfth_score,
#                 group=form_data['group']
#             )

#             db.session.add(student)
#             db.session.commit()

#             # Send Welcome Email
#             send_welcome_email(student.name, student.email, student.course)

#             flash('Registration successful!', 'success')
#             return redirect(url_for('register'))  # Fixed typo in redirect

#         except IntegrityError as e:
#             db.session.rollback()
#             flash('Database integrity error. Please check your input.', 'error')
#             return render_template('register.html', form_data=form_data)

#         except ValueError as e:
#             db.session.rollback()
#             flash(f'Invalid data format: {str(e)}', 'error')
#             return render_template('register.html', form_data=form_data)

#         except Exception as e:
#             db.session.rollback()
#             flash(f'Unexpected error: {str(e)}', 'error')
#             return render_template('register.html', form_data=form_data)

#     return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        print("Received Form Data:", form_data)

        # Clean and normalize data
        form_data['email'] = form_data['email'].strip().lower()
        form_data['phone'] = form_data['phone'].strip()
        course = form_data.get('course')
        payment_option = form_data.get('payment_option')  # Get payment choice

        # ✅ Validate course selection
        if course not in COURSE_PRICES:
            flash("Invalid course selected.", "error")
            return redirect(url_for('register'))

        # ✅ Get price in INR (Stripe requires paise)
        amount = COURSE_PRICES[course]

        # ✅ Store student details in the database
        new_student = Student(
            name=form_data['name'],
            dob=datetime.strptime(form_data['dob'], '%d/%m/%Y').date(),
            country_code=form_data['country_code'],
            phone=form_data['phone'],
            email=form_data['email'],
            address=form_data['address'],
            course=form_data['course'],
            graduated=form_data.get('graduated') == 'yes',
            tenth_score=float(form_data['tenth']),
            twelfth_score=float(form_data['twelfth']),
            group=form_data['group'],
            slot=form_data['slot'],
            college=form_data['college'],
            amount=amount,
            payment_status="Pending" if payment_option == "pay_later" else "Processing"
        )

        db.session.add(new_student)
        db.session.commit()
        send_welcome_email(new_student.name, new_student.email, new_student.course)
        # ✅ If "Pay Later", just register the student without payment
        if payment_option == "pay_later":
            flash("✅ Registration successful! You can complete the payment later.", "success")
            return redirect(url_for('register'))

        # ✅ If "Pay Now", redirect to Stripe for payment
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=VALID_PAYMENT_METHODS,  # ✅ FIXED: Removed "google_pay"
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {'name': f'Course: {course}'},
                        'unit_amount': amount,  # INR in paise
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=url_for('payment_success', student_id=new_student.id, _external=True),
                cancel_url=url_for('register', _external=True),
            )
            return redirect(session.url)

        except Exception as e:
            flash(f"Payment error: {str(e)}", "error")
            return redirect(url_for('register'))

    return render_template('register.html', course_prices=COURSE_PRICES)

@app.route('/payment-success/<int:student_id>')
def payment_success(student_id):
    # ✅ Retrieve student from the database
    student = Student.query.get(student_id)
    if not student:
        flash("Payment successful, but student record not found!", "warning")
        return redirect(url_for('register'))

    # ✅ Update payment status
    student.payment_status = "Paid"
    db.session.commit()

    flash("✅ Registration and Payment successful!", "success")
    return redirect(url_for('register'))

def send_welcome_email(name, email, course):
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "alagupl2710@gmail.com",
                    "Name": "Palaniappan Visalakshi Academy"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": name
                    }
                ],
                "Cc": [
                    {
                        "Email": "alagammaipl1993@gmail.com",
                        "Name": "Academy Admin"
                    }
                ],
                "Subject": "Welcome to Palaniappan Visalakshi Academy",
                "HTMLPart": f"""
                    <div style="text-align: center; font-family: 'Verdana', sans-serif; color: #333; font-size: 16px;">

                        <div style="font-family: 'Arial', sans-serif; font-size: 24px; color: #4A90E2;
                                    text-shadow: 2px 2px 0px #E5E5E5; margin-bottom: 20px;">
                            Palaniappan Visalakshi Academy
                        </div>

                        <h1>Welcome {name} to Palaniappan Visalakshi Academy!</h1>
                        <p style="font-size: 18px; color: #555;">
                            Thank you for registering for the <strong>{course}</strong> course.
                            We are excited to have you with us!
                        </p>

                        <div style="margin-top: 30px; padding: 15px; background-color: #f4f4f4; border-radius: 8px;">
                            <p style="font-size: 16px; color: #222;">
                                <strong>Next Steps:</strong> Our team will contact you soon with more details.
                            </p>
                        </div>

                        <p style="margin-top: 20px; color: #888;">
                            Best regards,<br>
                            <strong>Palaniappan Visalakshi Academy Team</strong>
                        </p>
                    </div>
                """
            }
        ]
    }

    print("📤 Sending Email Request to Mailjet...")
    result = mailjet_client.send.create(data=data)

    print("Response Status Code:", result.status_code)
    print("Response JSON:", result.json())

    if result.status_code == 200:
        print("✅ Email sent successfully")
    else:
        print("❌ Failed to send email:", result.json())

def send_contact_email(name, email, subject, message):
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "alagupl2710@gmail.com",
                    "Name": "Palaniappan Visalakshi Academy"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": name
                    }
                ],
                "Cc": [
                    {
                        "Email": "alagammaipl1993@gmail.com",
                        "Name": "Academy Admin"
                    }
                ],
                "Subject": subject,
                "HTMLPart": f"""
                    <div style="text-align: center; font-family: 'Verdana', sans-serif; color: #333; font-size: 16px;">
                        <div style="font-family: 'Arial', sans-serif; font-size: 24px; color: #4A90E2;
                                    text-shadow: 2px 2px 0px #E5E5E5; margin-bottom: 20px;">
                            Palaniappan Visalakshi Academy
                        </div>
                        <h1>Dear {name},</h1>
                        <p style="font-size: 18px; color: #555;">
                            {message}
                        </p>
                        <div style="margin-top: 30px; padding: 15px; background-color: #f4f4f4; border-radius: 8px;">
                            <p style="font-size: 16px; color: #222;">
                                We will contact you shortly.
                            </p>
                        </div>
                        <p style="margin-top: 20px; color: #888;">
                            Best regards,<br>
                            <strong>Palaniappan Visalakshi Academy Team</strong>
                        </p>
                    </div>
                """
            }
        ]
    }

    print("📤 Sending Contact Email Request to Mailjet...")
    result = mailjet_client.send.create(data=data)
    print("Response Status Code:", result.status_code)
    print("Response JSON:", result.json())
    if result.status_code == 200:
        print("✅ Contact email sent successfully")
    else:
        print("❌ Failed to send contact email:", result.json())

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        print("Contact Form Data:", form_data)

        # Retrieve form values
        name = form_data.get('name')
        email = form_data.get('email')
        subject = form_data.get('subject')
        message = form_data.get('message')

        # Insert query: Create a new Contact record
        new_contact = Contact(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        try:
            db.session.add(new_contact)
            db.session.commit()
            send_contact_email(name, email, subject, message)
            flash("Sent successfully. We will contact you shortly.", "success")
            return redirect(url_for('contact'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('contact'))

    # On GET, simply render the contact form template.
    return render_template('index.html')

# def send_welcome_email(name, email, course):
#     try:
#         message = Mail(
#             from_email=app.config['MAIL_DEFAULT_SENDER'],
#             to_emails=email,
#             subject="Welcome to Palaniappan Visalakshi Academy",
#             html_content=f"""
#                 <div style="text-align: center;">
#                     <div style="font-family: 'Arial', sans-serif;font-size: 24px;color: #4A90E2;text-shadow: 2px 2px 0px #E5E5E5;margin-bottom: 20px;">Palaniappan Visalakshi Academy</div>
#                     <div style="font-family: 'Verdana', sans-serif;color: #333;font-size: 16px;">
#                         <h1>Welcome to Palaniappan Visalakshi Academy, {name}!</h1>
#                         <p>Thank you for registering for the <strong>{course}</strong> course.</p>
#                         <p>We will contact you shortly.</p>
#                     </div>
#                     <div style="font-family: 'Tahoma', sans-serif;font-size: 16px;color: #888;margin-top: 20px;">
#                         Best regards,<br>
#                         Palaniappan Visalakshi Academy Team
#                     </div>
#                 </div>
#             """
#         )
#         sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
#         response = sg.send(message)
#         print(f"Email sent successfully with status code {response.status_code}")
#     except Exception as e:
#         print(f"Failed to send email: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)  # Change port to 8000 or another free port