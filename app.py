import random
import nexmo
from flask import Flask, request, session, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
app = Flask (__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL = 'mysql+pymysql://root:omobolaji@localhost/ajocard'
app.secret_key = 'some_random_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True


class sign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    pin = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    unique_id = db.Column(db.String(80), nullable=False)
    phone_no = db.Column(db.String(120), unique=True, nullable=False)

class transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.String(80),nullable=False)
    successful = db.Column(db.String(80),nullable=False)
    otp =  db.Column(db.String(80), nullable=False)
db.create_all()

@app.route("/sign", methods=["POST"])
def signup ():
    name = request.json.get('name')
    pin = request.json.get('pin')
    password = request.json.get('password')
    unique_id = request.json.get('unique_id')
    phone_no = request.json.get('phone_no')
    new = sign (name=name, pin=pin, password=password, unique_id=unique_id,phone_no=phone_no)
    db.session.add(new)
    db.session.commit()
    return (jsonify(
    {
            "message": "success",
            "name": name
        })), 202
@app.route("/login", methods=["POST"])
def login ():
    name = request.json.get('name')
    password = request.json.get('password')
    existing_user = sign.query.filter_by(name=name, password=password).first()
    if not existing_user:
        return (jsonify({"message":"incorect username or password"})), 404
    return (jsonify(
    {
        "message": "success",
        "username": name,
        "password": password
    
    })), 200

@app.route('/transact', methods=["POST"])
def transact():
    name = request.json.get('name')
    amount = request.json.get('amount')
    destination_id = request.json.get('destination_id')
    pin = request.json.get('pin')
    otp = random.randint(1000,9999)
    user = sign.query.filter_by(name=name, pin=pin).first()

    if amount.isdigit() == False :
        return (jsonify({
            "message" : "invalid amount"
        }))
    elif pin.isdigit() == False or len(pin) != 4:
        return (jsonify({
            "message" : "invalid pin"
        }))
    elif len(destination_id) != 12:
        return (jsonify({
            "message" : "invalid destination"
        }))
    elif not user:
        return (jsonify({"message": "incorrect pin"}))
    else:
        new_transaction = transaction(destination_id=destination_id, successful="no", amount=amount, otp=otp)
        db.session.add(new_transaction)
        db.session.commit()
        client = nexmo.Client(key='923e653d', secret='eX158CJctKtrgIWe')
        client.send_message({
            'from': 'Nexmo',
            'to': '2348149332585',
            'text': 'your otp is' + str(otp) + "visit localhost:5000/complete_transaction to complete your transaction"  
            })

        return (url_for("complete_trasaction", otp=the_otp))

@app.route('/complete_transaction', methods=["POST"])
def complete_trasaction(the_otp):
    otp =  request.json.get('otp')
   
    if otp == the_otp:
        successful = transaction.query.filter_by(otp=otp).update(dict(successful= yes))
        db.session.commit()
        return (jsonify({"message": "transaction successful"}))
    else:
        return (jsonify({"message": "transaction not successful"}))
   



if __name__=='__main__':
    app.run(debug=True)


    # https://documenter.getpostman.com/view/4964064/SVYxnaPy?version=latest