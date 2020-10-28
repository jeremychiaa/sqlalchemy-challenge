# Import dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create session from Python to the database
    session = Session(engine)

    # Query all precipition data
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Close this session
    session.close()

    # Create a dictionary from the row data and append to a list of all precipitation
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    # Return JSON representation of dictionary
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():

    # Create session from Python to the database
    session = Session(engine)
    
    # Query all stations
    results = session.query(Station.station, Station.name,
                            Station.latitude, Station.longitude, Station.elevation).all()

    # Close this session
    session.close()
    
    # Create a dictionary from the row data and append to a list of all stations
    all_stations = []
    for station, name, latitude, longitude, elevation in results:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations_dict["latitude"] = latitude
        stations_dict["longitude"] = longitude
        stations_dict["elevation"] = elevation
        all_stations.append(stations_dict)

    # Return JSON representation of dictionary
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")

def tobs():
# Create session from Python to the database
    session = Session(engine)
    
    # Query dates and temperature observations of the most active station for the last year of data
    
    # Query most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()

    # Unpack and convert result to string
    (most_active_station, ) = most_active_station

    # Find last data point date for most active station
    last_data_point = session.query(Measurement.date).\
    order_by(Measurement.date.desc()).\
    filter(Measurement.station == most_active_station).first()

    # Convert result to string and formatting
    (latest_date,) = last_data_point
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    latest_date = latest_date.date()

    # Find date 1 year from last entry
    date_year_ago = latest_date - dt.timedelta(days=365)

    # Query most active station's temperature observation data for the year
    most_active_tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= date_year_ago)

    # Close this session
    session.close()

    # Create a dictionary from the row data and append to a list of date and remperature observations
    most_active_dates_tobs = []
    for date, tobs in most_active_tobs:
        active_dict = {}
        active_dict["date"] = date
        active_dict["tobs"] = tobs
        most_active_dates_tobs.append(active_dict)

    # Return JSON representation of dictionary
    return jsonify(most_active_dates_tobs)

#@app.route("/api/v1.0/<start>")

#@app.route("/api/v1.0/<start>/<end>")

if __name__ == "__main__":
    app.run(debug=True)