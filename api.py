""" 
---LICENSE---
Author: John Matthew L. Villaluz
This is a course requirement for CS 192
Software Engineering II under the
supervision of Asst. Prof. Ma. Rowena C.
Solamo of the Department of Computer
Science, College of Engineering, University
of the Philippines, Diliman for the AY 2019-
2020.

---HISTORY---
1/20/20 John Matthew L. Villaluz - Created file, Made Models and Routing

---ABOUT---
Created: 1/20/20
Dev Group: RUPE Group 1
Client: Rowena Solamo
Desc: This contains relevant code for the API of RUPE. It has the 
Models and Routing of the backend.
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 
from flask_cors import CORS, cross_origin
import os 

# File Initializations
app = Flask(__name__) # creates the flask app 
CORS(app) # enables cross origin resource sharing
basedir = os.path.abspath(os.path.dirname(__file__)) # sets up the path for the sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite') # configures sqlite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # removes sqlite warnings

db = SQLAlchemy(app) # creates database object
ma = Marshmallow(app) # creates schema object

# Database Models
class Eatery(db.Model):
     id = db.Column(db.Integer, primary_key=True) # primary key of the eatery table
     name = db.Column(db.String(256), nullable=False) # name of the eatery
     address = db.Column(db.String(256), nullable=False, default='Unknown') # address of the eatery
     contact = db.Column(db.String(20), nullable=False, default='Unknown') # contact number of the eatery
     why_flag = db.Column(db.Text, default='') # reason for why the eatery was flagged
     flag = db.Column(db.Boolean, nullable=False, default=False) # whether or not the eatery is flagged
     rating = db.Column(db.Float, nullable=False, default=0) # overall rating of the eatery
     reviews = db.relationship('Review', backref='eatery', lazy=True) # database relationship of eatery and review

     """
     Method Name: __init__
     Creation: 1/20/20
     Purpose: to make the creating eatery objects easier
     Arguments: self, name, address, contact
     Required Tables: eatery
     Return Value: none
     """
     def __init__(self, name, address, contact):
          self.name = name # set passed name to the object's name
          self.address = address # set passed address to the object's address
          self.contact = contact # set passed contact to the object's contact

     """
     Method Name: __repr__
     Creation: 1/20/20
     Purpose: for displaying in terminal
     Arguments: self
     Required Tables: eatery
     Return Value: string containing the id
     """
     def __repr__(self):
          return 'Eatery ' + str(self.id)

class Review(db.Model):
     id = db.Column(db.Integer, primary_key=True) # primary key of the review table
     review_text = db.Column(db.Text, nullable=False, default='') # review of an eatery
     rating = db.Column(db.Float, nullable=False, default=0) # rating of an eatery
     why_flag = db.Column(db.Text, default='') # reason for why the review was flagged
     flag = db.Column(db.Boolean, nullable=False, default=False) # whether or not the review is flagged
     flagged_before = db.Column(db.Boolean, nullable=False, default=False) # whether or not the review has been flagged before
     eatery_id = db.Column(db.Integer, db.ForeignKey('eatery.id'), nullable=False) # foreign key of review to eatery

     """
     Method Name: __init__
     Creation: 1/20/20
     Purpose: to make creating review objects easier
     Arguments: self, review_text, rating, eatery_id
     Required Tables: review
     Return Value: none
     """
     def __init__(self, review_text, rating, eatery_id):
          self.review_text = review_text # set passed review_text to object's review_text
          self.rating = rating # set passed rating to object's rating
          self.eatery_id = eatery_id # set passed eatery_id to object's eatery_id

     """
     Method Name: __repr__
     Creation: 1/20/20
     Purpose: for displaying in terminal
     Arguments: self 
     Required Tables: review
     Return Value: string containing the id
     """
     def __repr__(self): 
          return 'Review ' + str(self.id)

# Schema For Sending Json Data
class EaterySchema(ma.Schema):
     class Meta: 
          fields = ('id', 'name', 'address', 'contact', 'why_flag', 'flag', 'rating') # format of json data for eateries

class ReviewSchema(ma.Schema):
     class Meta:
          fields = ('id', 'review_text', 'rating', 'why_flag', 'flag', 'flagged_before', 'eatery_id') # format of json data for reviews

eatery_schema = EaterySchema() # holds the schema structure for a single eatery
eateries_schema = EaterySchema(many=True) # holds the schema structure for multiple eateries
review_schema = ReviewSchema() # holds the schema structure for a single review
reviews_schema = ReviewSchema(many=True) # holds the schema structure for multiple reviews

# Endpoints for Eatery Related Data
"""
Method Name: get_eatery
Creation: 1/20/20
Purpose http get request for a single eatery 
Arguments: id 
Required Tables: eatery 
Return Value: single eatery in json format 
"""
@app.route('/eatery/<int:id>', methods=['GET'])
def get_eatery(id):
     eatery = Eatery.query.get(id) # query single eatery 

     return eatery_schema.jsonify(eatery)	 

"""
Method Name: get_eateries
Creation: 1/20/20
Purpose: http get request for all eateries
Arguments: none
Required Tables: eatery
Return Value: all eateries in json format
"""
@app.route('/eatery', methods=['GET'])
def get_eateries():
     eateries = Eatery.query.all() # query all eateries

     return eateries_schema.jsonify(eateries)

"""
Method Name: add_eatery
Creation: 1/20/20
Purpose: http post request to add an eatery
Arguments: none
Required Tables: eatery
Return Value: added eatery in json format
"""
@app.route('/eatery/add', methods=['POST'])
def add_eatery():
     name = request.get_json(force=True)['name'] # get name from POST request
     address = request.get_json(force=True)['address'] # get address from POST request
     contact = request.get_json(force=True)['contact'] # get contact from POST request

     new_eatery = Eatery(name, address, contact) # create new eatery object

     db.session.add(new_eatery) # add new eatery to the database
     db.session.commit() # save the change to the database

     return eatery_schema.jsonify(new_eatery)

# Endpoints For Review Related Data
"""
Method Name: get_reviews
Creation: 1/20/20
Purpose: http get request for all reviews of an eatery 
Arguments: id 
Required Tables: review
Return Value: all reviews of an eatery in json format
"""
@app.route('/eatery/<int:id>/review', methods=['GET'])
def get_reviews(id):
     reviews = Review.query.filter_by(eatery_id=id).all() # query all reviews from the eatery with an id of id
     
     return reviews_schema.jsonify(reviews)

"""
Method Name: add_review
Creation: 1/20/20
Purpose: http post request to add a review to an eatery
Arguments: id
Required Tables: eatery, review
Return Value: added review in json format
"""
@app.route('/eatery/<int:id>/review/add', methods=['POST'])
def add_review(id):
     eatery = Eatery.query.get(id) # query eatery with id of id
     reviews = Review.query.filter_by(eatery_id=id).all() # query all reviews from the eatery with an id of id

     review_text = request.get_json(force=True)['review_text'] # get review_text from POST request
     rating = request.get_json(force=True)['rating'] # get rating from POST request

     eatery.rating = ((eatery.rating*len(reviews)) + float(rating))/(len(reviews) + 1) # compute for the new rating given the current rating, amount of reviews, and latest rating

     new_review = Review(review_text, rating, id) # create new review object

     db.session.add(new_review) # add new review to the database
     db.session.commit() # save the change to the database

     return review_schema.jsonify(new_review)

if __name__ == '__main__':
     app.run(debug=True)
