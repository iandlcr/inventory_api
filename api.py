from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Nullable
from flask_restful import Resource, Api, fields, marshal_with, reqparse, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

class ItemModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    volume = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Item(name: {self.name}), volume: {self.volume}, price: {self.price}"

item_args = reqparse.RequestParser()
# item_args.add_argument('id', type=int)
item_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
item_args.add_argument('volume', type=str, required=True, help="Volume cannot be blank")
item_args.add_argument('price', type=float, required=True, help="Price cannot be blank")


itemFields = {
    'id':fields.Integer,
    'name':fields.String,
    'volume':fields.String,
    'price':fields.Float

}

class Items(Resource):
    @marshal_with(itemFields)
    def get(self):
        items = ItemModel.query.all()
        return items
    
    @marshal_with(itemFields)
    def post(self):
        args = item_args.parse_args()

        existing_item = ItemModel.query.filter_by(
            name=args["name"],
            volume=args["volume"],
            price=args["price"]
        ).first()

        if existing_item:
            abort(409, message='Item already exists')

        item = ItemModel(
            name=args["name"],
            volume=args["volume"],
            price=args["price"]
        )
        db.session.add(item)
        db.session.commit()
        items = ItemModel.query.all()
        return items, 201

class Item(Resource):
    @marshal_with(itemFields)
    def get(self, id):
        item = ItemModel.query.filter_by(id=id).first()
        if not item:
            abort(404, message= "item not found")
        return item

    @marshal_with(itemFields)
    def patch(self, name, volume, price):
        args = item_args.parse_args()
        item = ItemModel.query.filter_by(
            name=name,
            volume=volume,
            price=price
        ).first()
        
        if not item:
            abort(404, message= "item not found")

        item.name =args["name"]
        item.volume =args["volume"]
        item.price=args["price"]
        db.session.commit()
        return item

    @marshal_with(itemFields)
    def delete(self, name, volume, price):
        item = ItemModel.query.filter_by(
            name=name,
            volume=volume,
            price=price
        ).first()
            
        if not item:
            abort(404, message= "item not found")
        db.session.delete(item)
        db.session.commit()
        items = ItemModel.query.all()
        return items, 201



api.add_resource(Items, '/api/items/')
api.add_resource(Item, '/api/items/<string:name>/<string:volume>/<float:price>')



@app.route('/')
def home():
    return '<h1> FLASK REST API </h1>'

if __name__ == '__main__':
    app.run(debug=True)


