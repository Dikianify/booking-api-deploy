from decouple import config
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

db = SQLAlchemy()

def setup_email(app):
  app.config['MAIL_SERVER']="smtp.office365.com"
  app.config['MAIL_PORT'] = 587
  app.config['MAIL_USERNAME'] = config('MAIL_USERNAME')
  app.config['MAIL_PASSWORD'] = config('MAIL_PASSWORD')
  app.config['MAIL_USE_TLS'] = False
  app.config['MAIL_USE_SSL'] = True
  return Mail(app)

def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = config('DATABASE_URL')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

class BookedAppointments(db.Model):
  __tablename__ = 'booked_appointments'
  email = db.Column(db.Text, primary_key=True)
  date = db.Column(db.Text, unique=True, nullable=False)
  time = db.Column(db.Text, unique=True, nullable=False)
  column = db.Column(db.Text, unique=True, nullable=False)

  def __init__(self, email, date, time, column):
    self.email = email
    self.date = date
    self.time = time
    self.column = column

  def insert(self):
      db.session.add(self)
      db.session.commit()
  def delete(self):
      db.session.delete(self)
      db.session.commit()
  def update(self):
      db.session.commit()

class OpenAppointments(db.Model):
  __tablename__ = 'open_appointments'
  date = db.Column(db.Text, primary_key=True)
  time_1 = db.Column(db.Text, unique=True, nullable=False)
  time_2 = db.Column(db.Text, unique=True, nullable=False)
  time_3 = db.Column(db.Text, unique=True, nullable=False)
  time_4 = db.Column(db.Text, unique=True, nullable=False)
  time_5 = db.Column(db.Text, unique=True, nullable=False)
  time_6 = db.Column(db.Text, unique=True, nullable=False)

  def __init__(self, date, time_1, time_2, time_3, time_4, time_5, time_6):
    self.date = date
    self.time_1 = time_1
    self.time_2 = time_2
    self.time_3 = time_3
    self.time_4 = time_4
    self.time_5 = time_5
    self.time_6 = time_6

  def insert(self):
      db.session.add(self)
      db.session.commit()
  def delete(self):
      db.session.delete(self)
      db.session.commit()
  def update(self):
      db.session.commit()