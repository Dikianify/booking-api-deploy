from flask import Flask, request, jsonify, make_response
import os
from flask_cors import CORS
from models import setup_db, BookedAppointments, OpenAppointments, Accounts, setup_email
from flask_mail import Message
import jinja2

app = Flask(__name__)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

mail = setup_email(app)
db = setup_db(app)
CORS(app)

@app.route("/")
def base():
  response = make_response(jsonify("ok"))
  response.headers["Content-Type"] = "application/json"
  return response


@app.route("/get_times", methods=(["POST"]))
def get_times():
  date=request.get_json()[:10]
  
  time_dict = db.session.query(OpenAppointments).filter_by(date=date).first().__dict__

  date_data = []
  for i in range(0, 6):
    time_col = f"time_{str(i+1)}"
    time_val = time_dict[time_col]
    if time_val != "":
      date_data.append(
        {"value":time_col,
        "label":time_val
        })

  response = make_response(jsonify({ "options" : date_data }))
  response.headers["Content-Type"] = "application/json"
  return response


@app.route("/post_appointment", methods=["POST"])
def post_appointment():
  data=request.get_json()
  email=data[0].lower()
  date=data[1][:10]
  time=data[2]["label"]
  selected_time_column=data[2]["value"]

  db.session.query(OpenAppointments).filter_by(date=date).update({selected_time_column:""})

  old_booking = db.session.query(BookedAppointments).filter_by(email=email).first()
  if old_booking != None:
    db.session.delete(old_booking)
    db.session.query(OpenAppointments).filter_by(date=old_booking.date).update({old_booking.time_column:old_booking.time})

  new_booking=BookedAppointments(email=email, date=date, time=time, time_column=selected_time_column)
  new_booking.insert()

  db.session.commit()

  response = make_response(jsonify("ok"))
  response.headers["Content-Type"] = "application/json"
  return response

@app.route('/cancellation_email', methods=["POST"])
def cancellation_email():
  data=request.get_json()
  email=data[0].lower()
  date=data[1]
  time=data[2]

  with mail.connect() as conn:
    msg = Message(subject="Thank You for Booking with Us!", sender="jrogers@intuitautomation.com", recipients = [email])
    template = jinja_env.get_template('email.html')
    msg.html = template.render(data={'email':email,'date':date,'time':time})
    conn.send(msg)

  response = make_response(jsonify("ok"))
  response.headers["Content-Type"] = "application/json"
  return response

@app.route('/cancel_booking', methods=['POST'])
def delete_booking():
  email=request.get_json().lower()

  old_booking = db.session.query(BookedAppointments).filter_by(email=email).first()

  if old_booking != None:
    old_booking.delete()
    db.session.query(OpenAppointments).filter_by(date=old_booking.date).update({old_booking.time_column:old_booking.time})
    db.session.commit()

  response = make_response(jsonify("ok"))
  response.headers["Content-Type"] = "application/json"
  return response

@app.route('/login', methods={'POST'})
def login():
  email=request.get_json()[0]
  password=hash(request.get_json()[1])

  user = db.session.query(Accounts).filter_by(email=email).first()

  if user != None:
    if user.password == hash(password):
        response = make_response(jsonify("ok"))
        response.headers["Content-Type"] = "application/json"
        return response

  response = make_response(jsonify("not ok"))
  response.headers["Content-Type"] = "application/json"
  return response


@app.route('/create_account', methods={'POST'})
def create_account():
  email=request.get_json()[0]
  password=hash(request.get_json()[1])
  name=request.get_json()[2]
  company=request.get_json()[3]

  user = db.session.query(Accounts).filter_by(email=email).first()

  if user == None:
    new_user = Accounts(email,password,name,company)
    new_user.insert()
    response = make_response(jsonify("ok"))
    response.headers["Content-Type"] = "application/json"
    return response

  response = make_response(jsonify("not ok"))
  response.headers["Content-Type"] = "application/json"
  return response

@app.route('/test_endpoint', methods={'POST'})
def test_endpoint():
  new_sentence = request.get_json()["sentence"].replace(" ", "")
  response = make_response(jsonify(sentence=new_sentence))
  return response

if __name__ == "__main__":
  app.run()