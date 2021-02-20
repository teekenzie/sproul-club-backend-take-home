from flask import jsonify, send_file
from pymongo.mongo_client import MongoClient
from pyqrcode import QRCode
from bson import ObjectId
from load_student import get_new_student, is_verified
from load_textbooks import get_texbooks

DOMAIN = "http://127.0.0.1:5000"

# variables for error messages
INVALID_INPUT_MSG = 'The provided body should have the fields '
DATABASE_ERROR_MSG = "There was an error with the database. Please try again!" 
INCORRECT_PASSWORD_MSG = "Password provided is incorrect" 
INVALID_STUD_MSG = "There is no such student with this email"

client = MongoClient('localhost', 27017)
db = client['sproul-club']
students = db['students']
textbooks = db['textbooks']

def genTestData():
    # insert the student and the textbooks into the database  
    students.insert_one(get_new_student()) # password is "testStudent" 
    textbooks.insert_many(get_texbooks())

# check to make sure that we are provided with proper input
def is_validInput(body, requiredInpts):
    if body == None:
        return False
    for field in requiredInpts:
        if field not in body:
            return False 
    return True

# handle accessing self collection of textbook
def getTextbookC(body, requiredInpts):
    if (not is_validInput(body, requiredInpts)):
        return jsonify({"error": INVALID_INPUT_MSG + ', '.join(requiredInpts)}), 400

    # look for the corresponding student
    try:
        stud = students.find_one({"email": body["email"]})
    except Exception as err: 
        print(err)
        return jsonify({"error": DATABASE_ERROR_MSG}), 500

    # check to make sure that we have a valid user
    if (not stud):
        return jsonify({"error": INVALID_STUD_MSG}), 404

    # check to make sure it is actually the user himself/herself
    if (not is_verified(body["password"], stud['password'])):
        return jsonify({"error": INCORRECT_PASSWORD_MSG}), 401 
    
    return jsonify({"textbooks": stud['list_of_textbooks']}), 200

# handle adding textbook to collection
def addTextbookC(body, requiredInpts):
    if (not is_validInput(body, requiredInpts)):
        return jsonify({"error": INVALID_INPUT_MSG + ', '.join(requiredInpts)}), 400

    # look for the corresponding textbook and student
    try:
        textbook = textbooks.find_one({"id": body['book_id']})
        stud = students.find_one({"email": body['email']})
    except Exception as err:
        print(err)
        return jsonify({"error": DATABASE_ERROR_MSG}), 500

    # check to make sure we have a valid textbook and a valid student
    if (not textbook): 
        return jsonify({"error": "There is no such textbook with this id"}), 404
    if (not stud):
        return jsonify({"error": INVALID_STUD_MSG}), 404

    # check to make sure it is actually the user himself/herself
    if (not is_verified(body["password"], stud['password'])):
        return jsonify({"error": INCORRECT_PASSWORD_MSG}), 401
    
    # make sure that the book doesn't already exist
    for book in stud['list_of_textbooks']:
        if book['id'] == body['book_id']:
            return jsonify({"error": "The book already exist in the student's collection"}), 400
    
    textbook.pop('_id') # remove the object id field so we don't store it in our list

    # add the book for the corresponding student
    try:
        students.find_one_and_update(
            {"_id": stud['_id']}, 
            {'$push': {'list_of_textbooks': textbook, 'textbook_names': textbook['name']}})
    except Exception as err:
        print(err)
        return jsonify({"error": DATABASE_ERROR_MSG}), 500

    return jsonify({"success": True }), 200

def removeTextbookC(body, requiredInpts):
    if (not is_validInput(body, requiredInpts)):
        return jsonify({"error": INVALID_INPUT_MSG + ', '.join(requiredInpts)}), 400

    # look for the corresponding textbook and student
    try:
        stud = students.find_one({"email": body['email']})
    except Exception as err:
        print(err)
        return jsonify({"error": DATABASE_ERROR_MSG}), 500

    # check to make sure we have a valid student
    if (not stud):
        return jsonify({"error": INVALID_STUD_MSG}), 404

    # check to make sure it is actually the user himself/herself
    if (not is_verified(body["password"], stud['password'])):
        return jsonify({"error": INCORRECT_PASSWORD_MSG}), 401
    
    # find the textbook within the collection of the student
    textbook = None
    for book in stud['list_of_textbooks']:
        if book['id'] == body['book_id']:
            textbook = book
    if not textbook:
        return jsonify({"error": "The book id doesn't within the collection of the student"}), 400
    
    # remove the book for the corresponding student
    try: 
        students.find_one_and_update(
            {'_id': stud['_id']}, 
            {'$pull': {'list_of_textbooks': textbook, 'textbook_names': textbook['name']}})
    except Exception as err:
        print(err)
        return jsonify({"error": DATABASE_ERROR_MSG}), 500
    
    return jsonify({"success": True }), 200

# handle request for qr code that is to be shared 
def getQRcodeC(body, requiredInpts):
    if (not is_validInput(body,requiredInpts)):
        return jsonify({"error": INVALID_INPUT_MSG + ', '.join(requiredInpts)}), 400
     
    # look for the corresponding student
    try:
        stud = students.find_one({"email": body["email"]})
    except Exception as err: 
        print(err)
        return jsonify({"error": DATABASE_ERROR_MSG}), 500

    # check to make sure that we have a valid user
    if (not stud):
        return jsonify({"error": INVALID_STUD_MSG}), 404

    # check to make sure it is actually the user himself/herself
    if (not is_verified(body["password"], stud['password'])):
        return jsonify({"error": INCORRECT_PASSWORD_MSG}), 401

    # generate qr code with the embeded link
    dest = DOMAIN + '/share/' + str(stud['_id'])
    fileName = stud['full_name'] + ' QR code.png' 
    qr = QRCode(dest)
    qr.png(fileName, scale=8)

    return send_file(fileName, as_attachment=True, mimetype='image/png')

# handle request to the collection through the qr code 
def accessCollectionC(id):
    # look for the student that corresponds to the barcode
    try:
        stud = students.find_one({"_id": ObjectId(id)})
    except Exception as err:
        print(err)
        return jsonify({'error': DATABASE_ERROR_MSG}), 500

    # deal with invalid barcode
    if not stud:
        return jsonify({'error': 'Please provide a valid id'}), 404
    
    return jsonify({"collection": stud['textbook_names']}), 200