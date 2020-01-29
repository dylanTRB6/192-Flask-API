from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 
from flask_cors import CORS, cross_origin
import os 

# File Initializations
app = Flask(__name__)
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Database Models
class Eatery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    address = db.Column(db.String(256), nullable=False, default='Unknown')
    contact = db.Column(db.String(20), nullable=False, default='Unknown')
    why_flag = db.Column(db.Text, default='')
    flag = db.Column(db.Boolean, nullable=False, default=False)
    rating = db.Column(db.Float, nullable=False, default=0)
    reviews = db.relationship('Review', backref='eatery', lazy=True)

    def __init__(self, name, address, contact):
        self.name = name 
        self.address = address
        self.contact = contact

    def __repr__(self):
        return 'Eatery ' + str(self.id)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_text = db.Column(db.Text, nullable=False, default='')
    rating = db.Column(db.Float, nullable=False, default=0)
    why_flag = db.Column(db.Text, default='')
    flag = db.Column(db.Boolean, nullable=False, default=False)
    flagged_before = db.Column(db.Boolean, nullable=False, default=False)
    eatery_id = db.Column(db.Integer, db.ForeignKey('eatery.id'), nullable=False)

    def __init__(self, review_text, rating, eatery_id):
        self.review_text = review_text
        self.rating = rating 
        self.eatery_id = eatery_id

    def __repr__(self): 
        return 'Review ' + str(self.id)

# Schema For Sending Json Data
class EaterySchema(ma.Schema):
    class Meta: 
        fields = ('id', 'name', 'address', 'contact', 'why_flag', 'flag', 'rating')

class ReviewSchema(ma.Schema):
    class Meta:
        fields = ('id', 'review_text', 'rating', 'why_flag', 'flag', 'flagged_before', 'eatery_id')

eatery_schema = EaterySchema()
eateries_schema = EaterySchema(many=True)
review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)

# Endpoints for Eatery Related Data
@app.route('/eatery', methods=['GET'])
def get_eateries():
    eateries = Eatery.query.all()

    return eateries_schema.jsonify(eateries)

@app.route('/eatery/<int:id>', methods=['GET'])
def get_eatery(id):
    eatery = Eatery.query.get(id)

    return eatery_schema.jsonify(eatery)

@app.route('/eatery/add', methods=['POST'])
def add_eatery():
    
    name = request.get_json(force=True)['name']
    address = request.get_json(force=True)['address']
    contact = request.get_json(force=True)['contact']

    new_eatery = Eatery(name, address, contact)

    db.session.add(new_eatery)
    db.session.commit()

    return eatery_schema.jsonify(new_eatery)

@app.route('/eatery/<int:id>/delete', methods=['DELETE'])
def delete_eatery(id):
    eatery = Eatery.query.get(id)
    reviews = Review.query.filter_by(eatery_id=id).all()

    for review in reviews:
        db.session.delete(review)
    db.session.delete(eatery)
    db.session.commit()

    return eatery_schema.jsonify(eatery)

@app.route('/eatery/<int:id>/update', methods=['PUT'])
def update_eatery(id):
    eatery = Eatery.query.get(id)

    eatery.name = request.get_json(force=True)['name']
    eatery.address = request.get_json(force=True)['address']
    eatery.contact = request.get_json(force=True)['contact']

    db.session.commit()

    return eatery_schema.jsonify(eatery)

@app.route('/eatery/<int:id>/flag', methods=['PUT'])
def flag_eatery(id):
    eatery = Eatery.query.get(id)

    eatery.flag = True 
    eatery.why_flag = request.get_json(force=True)['why_flag']

    db.session.commit()

    return eatery_schema.jsonify(eatery)

@app.route('/eatery/<int:id>/unflag', methods=['PUT'])
def unflag_eatery(id):
    eatery = Eatery.query.get(id)

    eatery.flag = False
    eatery.why_flag = ''
    
    db.session.commit()

    return eatery_schema.jsonify(eatery)

# Endpoints For Review Related Data
@app.route('/eatery/<int:id>/review', methods=['GET'])
def get_reviews(id):
    reviews = Review.query.filter_by(eatery_id=id).all()
    
    return reviews_schema.jsonify(reviews)

@app.route('/eatery/<int:id>/review/add', methods=['POST'])
def add_review(id):
    eatery = Eatery.query.get(id)
    reviews = Review.query.filter_by(eatery_id=id).all()

    review_text = request.get_json(force=True)['review_text']
    rating = request.get_json(force=True)['rating']

    eatery.rating = ((eatery.rating*len(reviews)) + float(rating))/(len(reviews) + 1)

    new_review = Review(review_text, rating, id)

    db.session.add(new_review)
    db.session.commit()

    return review_schema.jsonify(new_review)

@app.route('/eatery/<int:e_id>/review/<int:r_id>/delete', methods=['DELETE'])
def delete_review(e_id, r_id):
    eatery = Eatery.query.get(e_id)
    reviews = Review.query.filter_by(eatery_id=e_id).all()
    review = Review.query.get(r_id)

    eatery.rating = ((eatery.rating*len(reviews)) - float(review.rating))/(len(reviews) - 1)

    db.session.delete(review)
    db.session.commit()

    return review_schema.jsonify(review)

@app.route('/eatery/<int:e_id>/review/<int:r_id>/flag', methods=['PUT'])
def flag_review(e_id, r_id):
    review = Review.query.get(r_id)

    review.flag = True 
    review.flagged_before = True 
    review.why_flag = request.get_json(force=True)['why_flag']

    db.session.commit()

    return review_schema.jsonify(review)

@app.route('/eatery/<int:e_id>/review/<int:r_id>/unflag', methods=['PUT'])
def unflag_review(e_id, r_id):
    review = Review.query.get(r_id)

    review.flag = False 
    review.why_flag = ''

    db.session.commit()

    return review_schema.jsonify(review)

if __name__ == '__main__':
    app.run(debug=True)