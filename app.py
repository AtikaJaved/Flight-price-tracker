from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["flight_tracker"]
flights_collection = db["flights"]

@app.route('/')
def home():
    return jsonify({"message": "Flight Price Tracker API is running!"})

@app.route('/seed', methods=['GET', 'POST'])
def seed_data():
    sample_flights = [
        {"route": "LHE→JED", "airline": "PIA", "flight_date": "2026-01-01", "price": {"2025-07-01": 600, "2025-08-01": 650, "2025-09-01": 700}},
        {"route": "LHE→BKK", "airline": "Thai Airways", "flight_date": "2026-02-10", "price": {"2025-08-01": 500, "2025-09-01": 530, "2025-10-01": 550}},
        {"route": "ISB→DXB", "airline": "Emirates", "flight_date": "2026-01-15", "price": {"2025-07-15": 700, "2025-08-15": 720, "2025-09-15": 760}},
        {"route": "KHI→IST", "airline": "Turkish Airlines", "flight_date": "2026-03-05", "price": {"2025-09-01": 900, "2025-10-01": 950, "2025-11-01": 1000}},
        {"route": "LHE→DXB", "airline": "FlyDubai", "flight_date": "2026-02-01", "price": {"2025-07-01": 450, "2025-08-01": 460, "2025-09-01": 470}},
        {"route": "ISB→DOH", "airline": "Qatar Airways", "flight_date": "2026-03-20", "price": {"2025-08-01": 800, "2025-09-01": 820, "2025-10-01": 850}},
        {"route": "KHI→LHR", "airline": "British Airways", "flight_date": "2026-04-10", "price": {"2025-09-01": 1000, "2025-10-01": 1020, "2025-11-01": 1050}},
        {"route": "LHE→KUL", "airline": "Malaysia Airlines", "flight_date": "2026-05-15", "price": {"2025-10-01": 700, "2025-11-01": 710, "2025-12-01": 730}},
        {"route": "ISB→JED", "airline": "Saudia", "flight_date": "2026-06-01", "price": {"2025-09-01": 620, "2025-10-01": 640, "2025-11-01": 660}},
        {"route": "KHI→BKK", "airline": "Thai Airways", "flight_date": "2026-02-25", "price": {"2025-07-01": 480, "2025-08-01": 500, "2025-09-01": 520}}
    ]

    flights_collection.insert_many(sample_flights)
    return jsonify({"message": "Sample flights added successfully!"})

# 🆕 View all flights
@app.route('/flights', methods=['GET'])
def get_flights():
    flights = list(flights_collection.find({}, {"_id": 0}))  # hide MongoDB _id field
    return jsonify(flights)


from datetime import datetime


@app.route('/search', methods=['GET'])
def search_flights():
    route = request.args.get('route')
    airline = request.args.get('airline')
    flight_date = request.args.get('flight_date')  # optional

    query = {}
    if route:
        query['route'] = route
    if airline:
        query['airline'] = airline
    if flight_date:
        query['flight_date'] = flight_date

    results = flights_collection.find(query)

    flights_list = []
    for flight in results:
        flights_list.append({
            "route": flight["route"],
            "airline": flight["airline"],
            "flight_date": flight["flight_date"],
            "price_time_series": [{"date": d, "price": p} for d, p in flight["price"].items()]
        })



# Remove duplicates
    seen = set()
    unique_flights = []
    for f in flights_list:
        key = (f["route"], f["airline"], f["flight_date"])
        if key not in seen:
            seen.add(key)
            unique_flights.append(f)

    return jsonify(unique_flights)

# Ranked search
@app.route("/search_ranked", methods=["GET"])
def search_ranked():
    route = request.args.get("route", "").strip()
    airline = request.args.get("airline", "").strip()
    flight_date = request.args.get("flight_date", "").strip()

    results = []
    for flight in flights_collection.find():
        route_score = 1 if flight["route"] == route else 0.5 if route in flight["route"] else 0
        airline_score = 1 if flight["airline"].lower() == airline.lower() else 0
        date_score = 0

        if flight_date:
            try:
                fd_request = datetime.strptime(flight_date, "%Y-%m-%d")
                fd_flight = datetime.strptime(flight["flight_date"], "%Y-%m-%d")
                days_diff = abs((fd_flight - fd_request).days)
                date_score = 1 / (1 + days_diff / 30)
            except ValueError:
                date_score = 0

        total_score = round(0.5*route_score + 0.3*airline_score + 0.2*date_score, 2)

        results.append({
            "route": flight["route"],
            "airline": flight["airline"],
            "flight_date": flight["flight_date"],
            "price_time_series": [{"date": d, "price": p} for d, p in flight["price"].items()],
            "score": total_score
        })

    # Remove duplicates
    seen = set()
    unique_results = []
    for f in results:
        key = (f["route"], f["airline"], f["flight_date"])
        if key not in seen:
            seen.add(key)
            unique_results.append(f)

    # Sort by score descending
    unique_results.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(unique_results)




from random import randint, uniform
from datetime import timedelta

@app.route('/track', methods=['GET'])
def track_flight():
    route = request.args.get('route')
    airline = request.args.get('airline')
    flight_date = request.args.get('flight_date')
    interval_days = int(request.args.get('interval', 15))  # default 15 days

    if not route or not airline or not flight_date:
        return jsonify({"error": "Please provide route, airline, and flight_date"}), 400

    # Find flight
    flight = flights_collection.find_one({
        "route": route,
        "airline": airline,
        "flight_date": flight_date
    })

    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    # Simulate price tracking every N days before flight date
    flight_day = datetime.strptime(flight_date, "%Y-%m-%d")
    today = datetime.now()
    days_diff = (flight_day - today).days

    prices = []
    current_price = list(flight["price"].values())[-1] if flight["price"] else 500

    for d in range(days_diff, 0, -interval_days):
        date_point = (flight_day - timedelta(days=d)).strftime("%Y-%m-%d")
        # simulate small price fluctuation
        price_change = uniform(-0.05, 0.05)
        current_price = round(current_price * (1 + price_change), 2)
        prices.append({"date": date_point, "price": current_price})

    return jsonify({
        "route": route,
        "airline": airline,
        "flight_date": flight_date,
        "interval_days": interval_days,
        "tracked_prices": prices
    })



@app.route('/update_price', methods=['POST'])
def update_price():
    data = request.get_json()

    route = data.get("route")
    airline = data.get("airline")
    flight_date = data.get("flight_date")
    date = data.get("date")
    price = data.get("price")

    if not all([route, airline, flight_date, date, price]):
        return jsonify({"error": "Missing required fields"}), 400

    # Find and update the flight
    result = flights_collection.update_one(
        {"route": route, "airline": airline, "flight_date": flight_date},
        {"$set": {f"price.{date}": price}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Flight not found"}), 404

    return jsonify({
        "message": "Price updated successfully!",
        "updated_date": date,
        "new_price": price
    })




from datetime import timedelta
import random

@app.route('/track_prices', methods=['POST'])
def track_prices():
    data = request.get_json()
    route = data.get("route")
    airline = data.get("airline")
    flight_date = data.get("flight_date")
    interval_days = data.get("interval_days", 15)  # default 15 days

    if not all([route, airline, flight_date]):
        return jsonify({"error": "route, airline, and flight_date are required"}), 400

    # find the flight in MongoDB
    flight = flights_collection.find_one(
        {"route": route, "airline": airline, "flight_date": flight_date}
    )
    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    # get the earliest price from the existing data
    price_values = list(flight["price"].values())
    if not price_values:
        return jsonify({"error": "No price data found for this flight"}), 400

    current_price = sum(price_values) / len(price_values)

    tracked_prices = []
    start_date = datetime.today()
    end_date = datetime.strptime(flight_date, "%Y-%m-%d")

    while start_date < end_date:
        # simulate price fluctuation randomly
        change_percent = random.uniform(-0.05, 0.05)
        current_price = round(current_price * (1 + change_percent), 2)
        tracked_prices.append({
            "date": start_date.strftime("%Y-%m-%d"),
            "price": current_price
        })
        start_date += timedelta(days=interval_days)

    return jsonify({
        "route": route,
        "airline": airline,
        "flight_date": flight_date,
        "interval_days": interval_days,
        "tracked_prices": tracked_prices
    })





@app.route('/best_deal', methods=['POST'])
def best_deal():
    data = request.get_json()

    # Validate request
    required_fields = ['route', 'airline', 'flight_date', 'interval_days']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    route = data['route']
    airline = data['airline']
    flight_date = data['flight_date']
    interval_days = data['interval_days']

    # Dummy price data (simulate tracking)
    prices = [
        {"date": "2025-10-23", "price": 575.28},
        {"date": "2025-11-07", "price": 554.77},
        {"date": "2025-11-22", "price": 564.19},
        {"date": "2025-12-07", "price": 563.83},
        {"date": "2025-12-22", "price": 571.94},
        {"date": "2026-01-06", "price": 589.39},
        {"date": "2026-01-21", "price": 573.12},
        {"date": "2026-02-05", "price": 551.00}
    ]

    # Find the lowest price
    best_deal = min(prices, key=lambda x: x['price'])

    return jsonify({
        "message": "Best deal found successfully!",
        "best_price": best_deal['price'],
        "best_date": best_deal['date'],
        "route": route,
        "airline": airline
    }), 200




if __name__ == '__main__':
    app.run(debug=True)
