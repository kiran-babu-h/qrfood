import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# =======================
# PostgreSQL configuration using environment variables
# =======================
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "qr_food")

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =======================
# Database model
# =======================
class Order(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    table_no = db.Column(db.Integer)
    customer_name = db.Column(db.String(100))
    items = db.Column(db.JSON)
    total = db.Column(db.Float)
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# =======================
# Home route
# =======================
@app.route("/")
def home():
    return "QR Food Backend is running with PostgreSQL"

# =======================
# Customer: Place Order
# =======================
@app.route("/api/order", methods=["POST"])
def place_order():
    data = request.json

    order = Order(
        id=str(uuid.uuid4()),
        table_no=data["table_no"],
        customer_name=data["customer_name"],
        items=data["items"],
        total=data["total"],
        status="Pending"
    )

    db.session.add(order)
    db.session.commit()
    return jsonify({"message": "Order placed successfully"})

# =======================
# Admin: Get all orders
# =======================
@app.route("/api/admin/orders")
def get_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([
        {
            "id": o.id,
            "table_no": o.table_no,
            "customer_name": o.customer_name,
            "items": o.items,
            "total": o.total,
            "status": o.status,
            "created_at": o.created_at
        }
        for o in orders
    ])

# =======================
# Admin: Update Order Status
# =======================
@app.route("/api/admin/order/<id>/status", methods=["POST"])
def update_status(id):
    order = Order.query.get(id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    order.status = request.json["status"]
    db.session.commit()
    return jsonify({"message": "Status updated"})

# =======================
# Admin: Remove Order
# =======================
@app.route("/api/admin/order/<id>/remove", methods=["DELETE"])
def remove_order(id):
    order = Order.query.get(id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order removed"})

# =======================
# Run app
# =======================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates table if it doesn't exist
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
