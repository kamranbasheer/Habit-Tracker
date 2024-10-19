from flask import render_template, redirect, url_for, flash, request, jsonify
from app import app, db
from app.models import User, Habit
from flask_login import login_user, logout_user, current_user
from app.models import Habit, HabitStatus
from datetime import date, timedelta

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle new habit creation
        habit_name = request.form.get('habit_name')
        if habit_name:
            new_habit = Habit(name=habit_name, user_id=current_user.id, creation_date=date.today())
            db.session.add(new_habit)
            db.session.commit()
            
            # Optional: Create HabitStatus for the current week
            today = date.today()
            start_of_week = today - timedelta(days=today.weekday())
            week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
            for day in week_dates:
                status = HabitStatus(habit_id=new_habit.id, date=day, completed=False)
                db.session.add(status)
            db.session.commit()
            return redirect(url_for('index'))

    # Get the current week offset from the query parameter, default to 0
    week_offset = int(request.args.get('week_offset', 0))
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday() + 7 * week_offset)
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]

    habits = Habit.query.filter_by(user_id=current_user.id).all()

    habit_status_dict = {}
    for habit in habits:
        status_list = []
        for day in week_dates:
            status = HabitStatus.query.filter_by(habit_id=habit.id, date=day).first()
            if not status:
                status = HabitStatus(habit_id=habit.id, date=day, completed=False)
                db.session.add(status)
            status_list.append(status)
        habit_status_dict[habit] = status_list
    db.session.commit()

    return render_template('index.html', habits=habits, week_dates=week_dates, habit_status_dict=habit_status_dict, week_offset=week_offset)

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    habit_id = data['habit_id']
    date_str = data['date']
    completed = data['completed']

    # Update the HabitStatus in the database
    status = HabitStatus.query.filter_by(habit_id=habit_id, date=date_str).first()
    if status:
        status.completed = completed
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False, message="Status not found"), 404

@app.route('/analysis')
def analysis():
    today = date.today()
    
    # Fetch all habits for the current user
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    habit_analysis = []

    for habit in habits:
        # Check for a valid creation_date
        start_date = habit.creation_date
        if start_date is None:
            flash(f"Habit '{habit.name}' has no valid creation date.", 'warning')
            continue
        
        # Calculate the total number of days since the habit was created
        total_days = (today - start_date).days
        
        # Fetch statuses within the determined timeframe
        statuses = HabitStatus.query.filter(
            HabitStatus.habit_id == habit.id,
            HabitStatus.date.between(start_date, today)
        ).all()
        
        completed_days = sum(status.completed for status in statuses)
        consistency_percentage = (completed_days / total_days * 100) if total_days > 0 else 0
        
        habit_analysis.append({
            'name': habit.name,
            'consistency': consistency_percentage,
            'total_days': total_days,
            'completed_days': completed_days
        })

    return render_template('analysis.html', habit_analysis=habit_analysis)


@app.route('/delete_habit/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('index'))

    # Delete associated HabitStatus entries
    HabitStatus.query.filter_by(habit_id=habit_id).delete()

    # Delete the habit itself
    db.session.delete(habit)
    db.session.commit()
    flash('Habit deleted successfully.', 'success')
    return redirect(url_for('index'))
