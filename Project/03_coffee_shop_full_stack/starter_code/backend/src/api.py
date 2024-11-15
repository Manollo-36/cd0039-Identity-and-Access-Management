#import os
#from urllib import response
from flask import Flask, jsonify,request
#from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
with app.app_context():
    db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['GET'])
@requires_auth('get:drinks')
def get_drinks(self):
    try:
        drink_menu = Drink.query.all()
        print (f'drink_menu:{drink_menu}')    
        if len(drink_menu) ==0:
            return not_found(404)
        else:
            drinks= [drink.short() for drink in drink_menu]
            print (f'drinks: {drinks}')
            response = { "success": True, "drinks": drinks}, 200
            return jsonify(response)
    except Exception as ex:
        print(ex)
        return unprocessable(422)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(self):    
    try:
        drink_menu =Drink.query.all()
        print (drink_menu)
        if len(drink_menu ) == 0 :
            return not_found(404)
        else:
            drinks= [drink.long() for drink in drink_menu]
         
            response = { "success": True, "drinks": drinks}, 200
            return jsonify(response)
    except Exception as ex:
        print(ex)
        return unprocessable(422)
    

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(self):  
    new_drink_request = request.get_json()
    new_title = new_drink_request["title"]
    new_recipe = new_drink_request["recipe"]

    try:
        new_drink = Drink(
                title=new_title,
                recipe= json.dumps(new_recipe)
            )
        
        if new_title =='' :
            return bad_request(400)
        else: 
            new_drink.insert()
             
            response = { "success": True, "drinks": new_drink.long()}, 200
            return jsonify(response)
    except Exception as ex:
        print(ex)
        return unprocessable(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(self,drink_id):  
    new_drink_request = request.get_json()
    new_title = new_drink_request["title"]
    new_recipe = new_drink_request["recipe"]

    try:

        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:               
                return not_found(404)  
        else:
            drink.title = new_title
            drink.recipe = json.dumps(new_recipe) 
            
            drink.update()
            response = { "success": True, "drinks": [drink.long()]}, 200
            return jsonify(response)
    except Exception as ex:
        print(ex)
        return unprocessable(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(self,drink_id):
    try:
        print (f"drink_id: {drink_id}")
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        print(f"drink: {drink}")
        if drink is None:
            return not_found(404)
        else: 
            drink.delete()

            response ={"success": True, "delete": drink_id},200
            return jsonify(response)
    except Exception as ex:
        print(ex)
        return unprocessable(422)
    
# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 404,
                    "message": "resource not found",
                }
            ),
            404,
        )
# @app.errorhandler(405)
# def method_not_allowed(error):
#         return (
#             jsonify(
#                 {
#                     "success": False,
#                     "error": 405,
#                     "message": "method not allowed",
#                 }
#             ),
#             405,
#         )

@app.errorhandler(400)
def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400,
        )

'''
@TODO implement error handler for AuthError    
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response =  jsonify({"success":False,"error":ex.status_code,"message":ex.error})
    #response.status_code = ex.status_code
    return response