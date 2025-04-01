#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Root route
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# GET /restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])

# GET /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant is None:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    # Add restaurant_pizzas to the response data
    restaurant_dict = restaurant.to_dict()
    restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
    restaurant_dict['restaurant_pizzas'] = [rp.to_dict() for rp in restaurant_pizzas]

    return jsonify(restaurant_dict)

# DELETE /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant is None:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    # Delete associated RestaurantPizza records
    RestaurantPizza.query.filter_by(restaurant_id=id).delete()
    db.session.delete(restaurant)
    db.session.commit()

    return '', 204

# GET /pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])

# POST /restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    # Check for required fields
    if not price or not pizza_id or not restaurant_id:
        return jsonify({'errors': ['validation errors']}), 400

    # Validate price
    if price < 1 or price > 30:
        return jsonify({'errors': ['validation errors']}), 400

    # Check if pizza and restaurant exist
    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if not pizza or not restaurant:
        return jsonify({'errors': ['Invalid pizza_id or restaurant_id']}), 400

    try:
        # Create a new RestaurantPizza object
        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()
        
        # Prepare response data
        response_data = restaurant_pizza.to_dict()

        # Add the associated pizza and restaurant details to the response
        response_data['pizza'] = pizza.to_dict()
        response_data['restaurant'] = restaurant.to_dict()

        return jsonify(response_data), 201
    except Exception as e:
        return jsonify({'errors': ['validation errors']}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)
