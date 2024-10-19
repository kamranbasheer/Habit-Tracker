from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.models import User, Habit
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@app.route('/index')
@login_required
def index():
    # Retrieve habits for the currently logged-in user
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', habits=habits)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Replace with your authentication logic
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:  # Simplified authentication
            login_user(user)
            return redirect(url_for('index'))  # Redirect to the main page after login
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')  # Render the login page

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Handle signup logic
    pass

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/habit', methods=['GET', 'POST'])
@login_required
def habit():
    if request.method == 'POST':
        # Extract form data to create or edit habits
        name = request.form.get('name')
        frequency = request.form.get('frequency')
        
        # Create a new Habit instance
        new_habit = Habit(name=name, frequency=frequency, user_id=current_user.id)
        db.session.add(new_habit)
        db.session.commit()
        
        flash('Habit added successfully!', 'success')
        return redirect(url_for('habit'))
    
    # Query habits for the current logged-in user
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    return render_template('habit.html', habits=habits)
