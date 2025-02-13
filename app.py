from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
import os
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# Database connection configuration
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Application model
class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)          # The category of the application (e.g., DJ, Artist)
    full_name = db.Column(db.String(255), nullable=False)        # Full name of the applicant
    alias = db.Column(db.String(255), nullable=True)             # Optional alias
    how_heard = db.Column(db.Text, nullable=True)                # How they heard about m(ux)
    description = db.Column(db.Text, nullable=True)              # Description of services they are interested in
    experience = db.Column(db.String(50), nullable=False)        # Experience level
    location = db.Column(db.String(255), nullable=False)         # Applicant's location
    links = db.Column(db.Text, nullable=True)                    # Links to their work
    volunteer = db.Column(db.Boolean, nullable=False)            # Whether they are open to volunteer
    email = db.Column(db.String(255), nullable=False)            # Email address
    comments = db.Column(db.Text, nullable=True)                 # Additional comments
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # Timestamp of application

class Response(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    avatar = db.Column(db.Text, nullable=False)  # Avatar stored as SVG text
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

@app.route('/delete-old-responses', methods=['DELETE'])
def delete_old_responses():
    try:
        # Calculate the cutoff time (messages older than 1 minute)
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)

        # Query and delete old responses using SQLAlchemy
        old_responses = Response.query.filter(Response.created_at < cutoff_time).all()
        for response in old_responses:
            db.session.delete(response)

        db.session.commit()

        return jsonify({"success": True, "deleted_count": len(old_responses)}), 200
    except Exception as e:
        print(f"Error deleting old responses: {e}")
        db.session.rollback()  # Rollback in case of an error
        return jsonify({"error": str(e)}), 500

# Admin password
ADMIN_PASSWORD = "Multunex123"

@app.before_request
def require_admin_authentication():
    # Protect only the /admin route
    if request.endpoint in ['admin.index'] and not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return redirect(url_for('admin.index'))
        else:
            flash("Incorrect password. Please try again.", "danger")
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('admin_login'))
# Set up Flask-Admin
admin = Admin(app, name='Mux Admin', template_mode='bootstrap4')
admin.add_view(ModelView(Application, db.session))
admin.add_view(ModelView(Response, db.session))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/apply')
def apply():
    return render_template('apply.html')

@app.route('/form')
def form_page():
    category = request.args.get('category')
    category_titles = {
        'dj': 'DJ/Musical Artist',
        'artist': 'Visual Artist/Vendor',
        'staff': 'Production/Staff'
    }
    return render_template('apply_form.html', category=category, category_title=category_titles.get(category, 'Application'))

@app.route('/streams')
def streams():
    return render_template('streams.html')

@app.route('/live')
def live():
    return render_template('live.html')

@app.route('/live-submit', methods=['POST'])
def live_submit():
    username = request.form.get('username')
    message = request.form.get('message')
    avatar = request.form.get('avatar')  # Avatar SVG data

    # Insert data into the responses table
    new_response = Response(name=username, message=message, avatar=avatar)
    db.session.add(new_response)
    db.session.commit()

    flash("New Message Added!")
    return redirect(url_for('live'))

@app.route('/get-responses', methods=['GET'])
def get_responses():
    responses = Response.query.all()
    data = [
        {
            "name": response.name,
            "message": response.message,
            "avatar": response.avatar
        }
        for response in responses
    ]
    return {"responses": data}

@app.route('/display')
def display():
    return render_template('display.html')

@app.route('/delete-response/<int:id>', methods=['DELETE'])
def delete_response(id):
    response = Response.query.get(id)
    if response:
        db.session.delete(response)
        db.session.commit()
        return '', 204
    return 'Not Found', 404

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Capture data from form submission
        category = request.form.get('category')
        full_name = request.form.get('full_name')
        alias = request.form.get('alias')
        how_heard = request.form.get('how_heard')
        description = request.form.get('description')
        experience = request.form.get('experience')
        location = request.form.get('location')
        links = request.form.get('links')
        volunteer = request.form.get('volunteer') == 'Yes'  # Convert to boolean
        email = request.form.get('email')
        comments = request.form.get('comments')

        # Insert data into the applications table
        new_application = Application(
            category=category,
            full_name=full_name,
            alias=alias,
            how_heard=how_heard,
            description=description,
            experience=experience,
            location=location,
            links=links,
            volunteer=volunteer,
            email=email,
            comments=comments
        )
        db.session.add(new_application)
        db.session.commit()

        flash("Thank you for your submission!")  # Flash a thank-you message
        return redirect(url_for('apply'))  # Redirect to the apply page
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        flash(f"An error occurred: {e}")  # Flash an error message
        return redirect(url_for('apply'))  # Redirect to the apply page

if __name__ == '__main__':
    app.run(debug=True)
