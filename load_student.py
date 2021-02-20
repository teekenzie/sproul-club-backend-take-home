from passlib.hash import pbkdf2_sha256 

# creates a new student in dictionary form
def get_new_student():
    return {
        "full_name" : "Test Student",
        "email" : "testStudent@gmail.com",
        "password" : pbkdf2_sha256.hash("testStudent"),
        "list_of_textbooks": [], 
        "textbook_names" : [] 
        # this field stores the names of the textbook so we don't have to request for every single book name when it is shared.
        }

# verifies the two password inputted
def is_verified(inputPass, actualPass):
    return pbkdf2_sha256.verify(inputPass, actualPass)