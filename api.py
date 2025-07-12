# Flask REST API for LCBO (Liquor Control Board of Ontario) items
# This API provides CRUD operations for alcoholic beverage items

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Nullable
from flask_restful import Resource, Api, fields, marshal_with, reqparse, abort

# Initialize Flask application
app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///database.db'

# Initialize SQLAlchemy with the Flask app
db = SQLAlchemy(app)

# Initialize Flask-RESTful API
api = Api(app)

# Database Model for LCBO items
class ItemModel(db.Model):
    """SQLAlchemy model representing an LCBO item"""
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String, nullable=False)    # Item name (required)
    volume = db.Column(db.String(80), nullable=False)  # Volume/size (required)
    price = db.Column(db.Float, nullable=False)    # Price (required)

    def __repr__(self):
        """String representation of the item"""
        return f"Item(name: {self.name}), volume: {self.volume}, price: {self.price}"

# Request parser for validating incoming data
item_args = reqparse.RequestParser()

# Add required fields to the parser
item_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
item_args.add_argument('volume', type=str, required=True, help="Volume cannot be blank")
item_args.add_argument('price', type=float, required=True, help="Price cannot be blank")

# Define the response format for API endpoints
itemFields = {
    'id': fields.Integer,
    'name': fields.String,
    'volume': fields.String,
    'price': fields.Float
}

class Items(Resource):
    """Resource class for handling multiple items (GET all, POST new)"""
    
    @marshal_with(itemFields)
    def get(self):
        """GET endpoint to retrieve all items"""
        items = ItemModel.query.all()
        return items
    
    @marshal_with(itemFields)
    def post(self):
        """POST endpoint to create a new item"""
        # Parse and validate the request arguments
        args = item_args.parse_args()

        # Check if item already exists to prevent duplicates
        existing_item = ItemModel.query.filter_by(
            name=args["name"],
            volume=args["volume"],
            price=args["price"]
        ).first()

        # Return 409 Conflict if item already exists
        if existing_item:
            abort(409, message='Item already exists')

        # Create new item instance
        item = ItemModel(
            name=args["name"],
            volume=args["volume"],
            price=args["price"]
        )
        
        # Add to database and commit
        db.session.add(item)
        db.session.commit()
        
        # Return all items with 201 Created status
        items = ItemModel.query.all()
        return items, 201

class Item(Resource):
    """Resource class for handling individual items (GET, PATCH, DELETE)"""
    
    @marshal_with(itemFields)
    def get(self, id):
        """GET endpoint to retrieve a specific item by ID"""
        item = ItemModel.query.filter_by(id=id).first()
        if not item:
            abort(404, message="item not found")
        return item

    @marshal_with(itemFields)
    def patch(self, name, volume, price):
        """PATCH endpoint to update an existing item"""
        # Parse and validate the request arguments
        args = item_args.parse_args()
        
        # Find the item to update
        item = ItemModel.query.filter_by(
            name=name,
            volume=volume,
            price=price
        ).first()
        
        # Return 404 if item not found
        if not item:
            abort(404, message="item not found")

        # Update item properties
        item.name = args["name"]
        item.volume = args["volume"]
        item.price = args["price"]
        
        # Commit changes to database
        db.session.commit()
        return item

    @marshal_with(itemFields)
    def delete(self, name, volume, price):
        """DELETE endpoint to remove an item"""
        # Find the item to delete
        item = ItemModel.query.filter_by(
            name=name,
            volume=volume,
            price=price
        ).first()
            
        # Return 404 if item not found
        if not item:
            abort(404, message="item not found")
        
        # Delete item and commit
        db.session.delete(item)
        db.session.commit()
        
        # Return all remaining items with 201 status
        items = ItemModel.query.all()
        return items, 201

# Register API resources with their endpoints
api.add_resource(Items, '/api/items/')  # GET all, POST new
api.add_resource(Item, '/api/items/<string:name>/<string:volume>/<float:price>')  # GET, PATCH, DELETE specific

# Home route
@app.route('/')
def home():
    """Simple home page route"""
    return '<h1> FLASK REST API </h1>'

# Run the application if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True)


