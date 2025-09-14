from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///applications.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the database model
class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    date_applied = db.Column(db.Date, nullable=False)

# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    applications = JobApplication.query.all()

    # Add progress info to each application
    for app_item in applications:
        if app_item.status == 'Applied':
            app_item.progress = 20
            app_item.color = 'green'
        elif app_item.status == 'Interview':
            app_item.progress = 60
            app_item.color = 'green'
        elif app_item.status == 'Offer':
            app_item.progress = 100
            app_item.color = 'green'
        elif app_item.status == 'Rejected':
            app_item.progress = 100
            app_item.color = 'red'
        else:
            app_item.progress = 40
            app_item.color = 'green'

    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('index.html', applications=applications, today=today)

@app.route('/submit', methods=['POST'])
def submit():
    company = request.form['company']
    role = request.form['role']
    date_str = request.form['date_applied']
    date_applied = datetime.strptime(date_str, '%Y-%m-%d').date()

    new_application = JobApplication(
        company=company,
        role=role,
        status="Applied",
        date_applied=date_applied
    )
    db.session.add(new_application)
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    application = JobApplication.query.get_or_404(id)
    db.session.delete(application)
    db.session.commit()
    return redirect('/')

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    new_status = request.form['status']
    application = JobApplication.query.get_or_404(id)

    # Prevent moving back from Offer or Rejected
    if application.status in ['Offer', 'Rejected']:
        return redirect('/')

    # Prevent decreasing progress
    status_order = ['Applied', 'Interview', 'Offer', 'Rejected']
    current_index = status_order.index(application.status)
    new_index = status_order.index(new_status)
    if new_index >= current_index:
        application.status = new_status

    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
