 Flight Price Tracker
 
1. Overview

The Flight Price Tracker is a Flask-based API system designed to track and analyze flight ticket prices for different routes over time. It can:

Track ticket prices over given intervals (e.g., every 15 days)

Update prices dynamically

Suggest the best (lowest) deal automatically



2. Features

Automated Price Tracking: Generates time-series data of ticket prices between today and the flight date

Price Update API: Allows updating the latest flight price manually

Best Deal Finder: Finds and returns the cheapest date and price for any selected route, airline, and flight date

MongoDB Integration: Can store and retrieve flight data from MongoDB 



3. Endpoints

---Health Check

Method: GET

Endpoint: /

Description: Checks if the API is running

--- Track Prices

Method: POST

Endpoint: /track_prices

Description: Generates tracked prices over a given interval

Example Body:

{
  "route": "LHE→BKK",
  "airline": "Thai Airways",
  "flight_date": "2026-02-10",
  "interval_days": 15
}

--- Update Price

Method: POST

Endpoint: /update_price

Description: Updates a specific flight’s price

Example Body:

{
  "route": "LHE→BKK",
  "airline": "Thai Airways",
  "flight_date": "2026-02-10",
  "new_price": 560
}

--- Best Deal

Method: GET

Endpoint: /best_deal

Description: Finds the best (lowest) deal

Example Query:

?route=LHE→BKK&airline=Thai Airways&flight_date=2026-02-10



4. Sample Dataset (dataset.json)
[
  {"route":"LHE→BKK","airline":"Thai Airways","flight_date":"2026-02-10","price":{"2025-08-01":500,"2025-09-01":530,"2025-10-01":550}},
  {"route":"KHI→IST","airline":"Turkish Airlines","flight_date":"2026-03-05","price":{"2025-09-01":900,"2025-10-01":950,"2025-11-01":1000}}
]



5. Tools Used

Python 3 / Flask — Backend API

Postman — API testing

MongoDB — Database for flight data 

JSON — Data storage format



6. Example Responses

/track_prices

{
  "route": "LHE→BKK",
  "airline": "Thai Airways",
  "flight_date": "2026-02-10",
  "interval_days": 15,
  "tracked_prices": [
    {"date": "2025-10-22", "price": 529.98},
    {"date": "2025-11-06", "price": 529.94}
  ]
}


/update_price

{
  "message": "Price updated successfully!",
  "new_price": 560,
  "updated_date": "2025-10-21"
}


/best_deal

{
  "route": "LHE→BKK",
  "airline": "Thai Airways",
  "best_date": "2026-02-05",
  "best_price": 551.0,
  "message": "Best deal found successfully!"
}



7. How to Run

Open terminal in the project folder

Run the Flask app:

python app.py


Test endpoints using Postman:

POST http://127.0.0.1:5000/track_prices

POST http://127.0.0.1:5000/update_price

GET http://127.0.0.1:5000/best_deal?route=LHE→BKK&airline=Thai
 Airways&flight_date=2026-02-10
