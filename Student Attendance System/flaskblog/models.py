from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    user = Student.query.get(int(user_id))
    if user:
        return user
    else:
        return Faculty.query.get(int(user_id))

class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    course = db.Column(db.String(120), nullable=False)
    sem = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.course}' , '{self.sem}' , '{self.email}', '{self.image_file}')"

class Faculty(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    dept = db.Column(db.String(120), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

    def __repr__(self):
        return f"User('{self.id}','{self.dept}',)"

class Subject(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    subname = db.Column(db.String(120), nullable=False)
    dept = db.Column(db.String(120), nullable=False)
    course = db.Column(db.String(120), nullable=False)
    sem = db.Column(db.Integer, nullable=False )
    totalclass = db.Column(db.Integer, nullable=True, default=0)
    fid = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)

    def __repr__(self):
        return f"User('{self.id}','{self.subname}', '{self.course}', '{self.sem}')"


class Attendance(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('student.id'),primary_key=True, nullable=False)
    subid = db.Column(db.String(10), db.ForeignKey('subject.id'), primary_key=True,nullable=False)
    datemissed = db.Column(db.DateTime, nullable=False, primary_key=True,default=datetime.now())

    def __repr__(self):
        return f"User('{self.id}','{self.subid}','{self.datemissed}')"

class ImageData(db.Model):
    subname = db.Column(db.String(120),primary_key=True, nullable=False)
    fid = db.Column(db.Integer, db.ForeignKey('faculty.id'),primary_key=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=True)
