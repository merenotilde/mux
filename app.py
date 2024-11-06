from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database connection configuration
DB_HOST = "52.91.34.166"
DB_PORT = "5432"
DB_NAME = "mux"
DB_USER = "postgres"
DB_PASSWORD = "9545"

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Application model
class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Create the database tables if they don't exist already
with app.app_context():
    db.create_all()

# Set up Flask-Admin
admin = Admin(app, name='Mux Admin', template_mode='bootstrap4')
admin.add_view(ModelView(Application, db.session))

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/apply')
def apply():
    return render_template('apply.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Capture data from form submission
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Insert data into the applications table
    new_application = Application(name=name, email=email, message=message)
    db.session.add(new_application)
    db.session.commit()

    

    flash("Thank you for your submission!")  # Set the "Thank you" message
    return redirect(url_for('apply'))  # Redirect to the same page

    return render_template('apply.html')

if __name__ == '__main__':
    app.run(debug=True)
