from flask import Flask, request
from controller import accessCollectionC, addTextbookC, genTestData, getQRcodeC, getTextbookC, removeTextbookC 

# initialize flask and define database and models
app = Flask(__name__)

genTestData() # place the student and the textbooks test data into the database 
# student passsword is "testStudent"

"""
This route allows for the user to get access to his/her own set of collection of textbooks 

type: GET
route: '/textbook/get'
request body should have the fields "email" and "password"
Possible response will have the field:
    "error", if there was an error with the input or during the process
    "textbook", corresponds to a list of textbook objects
"""
@app.route('/textbook/get', methods=['GET'])
def textbook_get(): 
    return getTextbookC(request.json, ['email', 'password'])

"""
This route allows for the user to add textbook to his/her own set of collection of textbooks

type: PATCH
route: '/textbook/add'
request body should have the fields "book_id", "email", and "password"
Possible response will have the field:
    "error", if there was an error with the input or during the process
    "success", if the indicated textbook has been successfully added
"""
@app.route('/textbook/add', methods=['PATCH'])
def textbook_add():
    return addTextbookC(request.json, ['book_id', 'email', 'password'])

"""
This route allows for the user to remove textbook from his/her own set of collection of textbooks

type: DELETE
route: 'textbook/remove'
request body should have the fields "book_id", "email", and "password"
Possible response will have the field:
    "error", if there was an error with the input or during the process
    "success", if the indicated textbook has been successfully removed
"""
@app.route('/textbook/remove', methods=['DELETE'])
def textbook_remove():
    return removeTextbookC(request.json, ['book_id', 'email', 'password'])

"""
This route allows for the user to get a QR Code that embeds a link to their collection of textbooks
The collection of textbooks linked to will only return the name of the textbooks

type: GET
route: 'share/qrcode'
request body should have the fields "email", and "password"
Possible response could be:
    "error", if there was an error with the input or during the process
    a .png image that displays the QR Code
"""
@app.route('/share/qrcode', methods=['GET'])
def share_barcode(): 
    return getQRcodeC(request.json, ['email', 'password'])

"""
This route allows for everyone to access the speicified collection of books

type: GET
route: 'share/<string: id>'
No request body
Possible response could be:
    "error", if there was an error with the input or during the process
    "collection", the set of collection of textbooks names 
"""
@app.route('/share/<id>', methods=['GET'])
def share_access(id):
    return accessCollectionC(id)
    
if __name__ == "__main__":
    app.run()