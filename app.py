from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# create db
with app.app_context():
    db.create_all()

@app.route('/hello/<username>', methods=['PUT'])
def save_user(username):
    if not re.match("^[A-Za-z]+$", username):
        return "Invalid username", 400

    data = request.get_json()
    date_of_birth = data.get('dateOfBirth')

    try:
        date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        if date_of_birth > date.today():
            return "dateOfBirth must be before today", 400
    except ValueError:
        return "Invalid date format", 400

    user = User.query.filter_by(username=username).first()
    if user:
        user.date_of_birth = date_of_birth
    else:
        user = User(username=username, date_of_birth=date_of_birth)
        db.session.add(user)
    db.session.commit()

    return '', 204

@app.route('/hello/<username>', methods=['GET'])
def get_user(username):
    if not re.match("^[A-Za-z]+$", username):
        return "Invalid username", 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return "User not found", 404

    today = date.today()
    next_birthday = user.date_of_birth.replace(year=today.year)
    if next_birthday < today:
        next_birthday = next_birthday.replace(year=today.year + 1)

    days_until_birthday = (next_birthday - today).days

    if days_until_birthday == 0:
        message = f"Hello, {username}! Happy birthday!"
    else:
        message = f"Hello, {username}! Your birthday is in {days_until_birthday} day(s)"

    return jsonify({"message": message})

if __name__ == '__main__':
    app.run(debug=True)
