from importlib.metadata import requires
import os
from pickle import TRUE
from tkinter import N
from flask import Flask, request, jsonify, abort
from sqlalchemy import JSON, exc, true
import json
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .database.models import db_drop_and_create_all, setup_db, Drink, db
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

@app.route('/drinks', methods=['GET'])
def all_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id.desc()).all()
        
        return jsonify(
        {
            "success": True,
            "drinks":[Drink.short(drink) for drink in drinks]
        }
        )
    
    except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(500)   
    
    
    
    


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''



@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drink_detail(self):
    try:
        drinks = Drink.query.all() 
        return jsonify(
        {
            "success": True,
            "drinks": [Drink.long(drink) for drink in drinks]
        }
        )    

    except:
        abort(500)        

    

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(self):
    try:
        body = request.get_json()
        title = body.get('title')
        recipe = body.get('recipe')
        # convert list to string
        recipe = json.dumps(recipe)
        
        if title == None or recipe == None:
            abort(400)
        drink = Drink(
        title=title,
        recipe= recipe
        )
        
        drink.insert()
        return jsonify({
                'success': True,
                'created':drink.long()
                
        })


    except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(500)       

    

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

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(self,id):
    body = request.get_json()
    
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        
        if drink is None:
            abort(404)
        if 'title' in body:
            drink.title = str(body.get('title'))
        if 'recipe' in body:
            recipe = str(body.get('recipe')) 
            # replace all single qoutes with double quotes
            recipe = recipe.replace("\'", "\"") 
            drink.recipe = recipe
            
        
        drink.update()      
            
                
        return jsonify(
            {
                "success":True,
                "drinks": [drink.long()]
            }
            )
    except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(500)            

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

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(self,id):
    try:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)
        Drink.delete(drink) 

        return jsonify({
            'success': True,
            'delete':id
        })

    except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            else:
                abort(500)          

    

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400    

@app.errorhandler(401)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Not Authorized"
    }), 401        

@app.errorhandler(403)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
