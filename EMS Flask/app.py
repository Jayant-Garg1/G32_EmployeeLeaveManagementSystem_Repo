from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from werkzeug.exceptions import InternalServerError
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "app.db")
app.config['SECRET_KEY'] = 'my_secret_key'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    _tablename_ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")
    username = db.Column(db.String(100), nullable=False, unique=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="pending")

    user = db.relationship('User', backref=db.backref('leave_requests', lazy=True))

    def __repr__(self):
        return f'<LeaveRequest {self.id} - {self.leave_type}>'

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all() 
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user is None:
        admin_user = User(
            name="Admin",
            email="admin@example.com",
            username="admin",
            role="admin"
        )
        admin_user.set_password("password123")
        db.session.add(admin_user)
        db.session.commit()


@app.route('/')
def home():
    return render_template('home_page.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        print("Role selected in form:", role)
        print("Email entered:", email)

        user = User.query.filter_by(email=email, role=role).first()
        print("Query:", User.query.filter_by(email=email, role=role))

        if user and user.check_password(password):
            login_user(user)
            session['username'] = user.name 
            flash("Login successful!", "success")
            if user.role == "admin":
                return redirect(url_for("admin_portal"))  
            else:
                return redirect(url_for("employee_portal")) 
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('login'))
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('login'))
        new_user = User(name=name, email=email, username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template('signup.html')




@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


@app.route('/admin_portal')
@login_required
def admin_portal():
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    leave_requests = LeaveRequest.query.all()
    return render_template('admin_portal.html', leave_requests=leave_requests)


@app.route('/approve_leave/<int:leave_id>')
@login_required
def approve_leave(leave_id):
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    leave_request = LeaveRequest.query.get_or_404(leave_id)
    leave_request.status = 'approved'
    db.session.commit()
    
    flash('Leave request approved!', 'success')
    return redirect(url_for('admin_portal'))


@app.route('/reject_leave/<int:leave_id>')
@login_required
def reject_leave(leave_id):
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    
    leave_request = LeaveRequest.query.get_or_404(leave_id)
    leave_request.status = 'rejected'
    db.session.commit()
    
    flash('Leave request rejected.', 'danger')
    return redirect(url_for('admin_portal'))


@app.route('/employee_portal')
@login_required
def employee_portal():
    leave_requests = LeaveRequest.query.filter_by(user_id=current_user.id).all()
    return render_template('employee_portal.html', leave_requests=leave_requests)


@app.route('/apply_leave', methods=['POST'])
@login_required
def apply_leave():
    leave_type = request.form['leave_type']
    start_date_str = request.form['start_date']
    end_date_str = request.form['end_date']
    
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    
    new_leave_request = LeaveRequest(
        user_id=current_user.id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        status='pending'
    )
    
    db.session.add(new_leave_request)
    db.session.commit()
    
    flash('Your leave request has been submitted and is pending approval.', 'success')
    return redirect(url_for('employee_portal'))




@app.route('/update_user/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    user = User.query.get(user_id)
    if user:
        user.name = request.form['name']
        user.email = request.form['email']
        user.username = request.form['username']
        db.session.commit()
        flash('User updated successfully!', 'success')
    return redirect(url_for('admin_portal'))

@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_portal'))

@app.route('/about_us')
def aboutus():
    return render_template('about_us.html')




@app.route('/privacy_and_policy')
def privacyandpolicy():
    return render_template('privacy_and_policy.html')


@app.route('/terms_and_conditions')
def termsandconditions():
    return render_template('terms_and_conditions.html')



app.secret_key = 'your_secret_key' 

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    feedback = Feedback(name=name, email=email, message=message)
    db.session.add(feedback)
    db.session.commit()
    
    flash('Thank you for your feedback!', 'success')
    return redirect(url_for('home'))
  
@app.route('/feedbacks')
def feedback_list():
    feedbacks = Feedback.query.all()
    return render_template('feedback_list.html', feedback_list=feedbacks)


from flask import jsonify

@app.route('/api/about_us')
def api_aboutus():
    html_content = render_template('about_us.html')
    return jsonify({"html": html_content})

@app.route('/api/privacy_and_policy')
def api_privacyandpolicy():
    html_content = render_template('privacy_and_policy.html')
    return jsonify({"html": html_content})

@app.route('/api/terms_and_conditions')
def api_termsandconditions():
    html_content = render_template('terms_and_conditions.html')
    return jsonify({"html": html_content})

@app.route('/api/submit_feedback', methods=['POST'])
def api_submit_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    feedback = Feedback(name=name, email=email, message=message)
    db.session.add(feedback)
    db.session.commit()

    return jsonify({"message": "Feedback submitted successfully!"}), 201

@app.route('/api/feedback_list', methods=['GET'])
def api_feedback_list():
    feedbacks = Feedback.query.all()
    feedback_list = [
        {
            "name": feedback.name,
            "email": feedback.email,
            "message": feedback.message,
            "submitted_at": feedback.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for feedback in feedbacks
    ]
    return jsonify(feedback_list)


if __name__ == "__main__":
    app.run(debug=True)



