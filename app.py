from flask import Flask, render_template, request, jsonify, make_response
import os
from flask_migrate import Migrate
from flask_cors import CORS
from models import setup_db, BookedAppointments, OpenAppointments, setup_email
from flask_mail import Message
import jinja2

app = Flask(__name__)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

mail = setup_email(app)
db = setup_db(app)
migrate = Migrate(app, db)
CORS(app)


@app.route("/get_times", methods=(["POST"]))
def get_times():
  date=request.get_json()[:10]

  print(db.metadata.tables.keys())
  
  raw_date_data = OpenAppointments.query.filter_by(date=date).first()


  date_data = []
  for data in raw_date_data:
    if data[1] != "":
      date_data.append(
        {"value":data[0],
        "label":data[1]
        })

  response = make_response(jsonify({ "options" : date_data }))
  response.headers["Content-Type"] = "application/json"

  return response


@app.route("/post_appointment", methods=["POST"])
def post_appointment():
  data=request.get_json()
  email=data[0]
  date=data[1][:10]
  time=data[2]["label"]
  time_column=data[2]["value"]

  db.session.query(OpenAppointments).filter_by(date=date).update({time_column:""})

  old_booking = db.session.query(BookedAppointments).filter_by(email=email).first()
  if old_booking != None:
    db.session.delete(old_booking)
    db.session.query(OpenAppointments).filter_by(date=old_booking.date).update({old_booking.column:old_booking.time})

  new_booking=BookedAppointments(email=email, date=date, time=time, column=time_column)
  new_booking.insert()

  msg = Message(subject="Thank You for Booking with Us!", sender="jrogers@intuitautomation.com", recipients = [email])
  template = jinja_env.get_template('email.html')
  msg.html = template.render(data={'email':email,'date':date,'time':time})
  mail.send(msg)

  return jsonify('ok'), 201

@app.route('/delete_booking', methods=['POST'])
def delete_booking():
  email = request.form['submit_button']

  old_booking = db.session.query(BookedAppointments).filter_by(email=email).first()
  old_booking.delete()
  db.session.query(OpenAppointments).filter_by(date=old_booking.date).update({old_booking.column:old_booking.time})
  db.session.commit()

if __name__ == "__main__":
  app.run()