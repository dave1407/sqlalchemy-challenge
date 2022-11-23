import numpy as np
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc, cast, Date, extract

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD  'Enter the start date in the date format shown, to query starting from the given date'<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD 'Enter the start date followed by the end date in the format shown, to query a range of dates'"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation values and dates"""
    # Query all dates
    dates = session.query(Measurement.date).all()

    # Query all precipitacion values
    precipitation = session.query(Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    dates_list = list(np.ravel(dates))
    precipitation_list = list(np.ravel(precipitation))

    measurement_dict = {dates_list[i]: precipitation_list[i] for i in range(len(dates_list))}

    return jsonify(measurement_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    station_results = session.query(Station.station).distinct().all()

    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_results))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    measurement_latest_year = session.query(extract('year',Measurement.date)).order_by(desc(Measurement.date)).first()[0]
    measurement_latest_month = session.query(extract('month',Measurement.date)).order_by(desc(Measurement.date)).first()[0]
    measurement_latest_day = session.query(extract('day',Measurement.date)).order_by(desc(Measurement.date)).first()[0]

    # Calculate the date one year from the last date in data set.
    measurement_1year_back = dt.date(measurement_latest_year, measurement_latest_month, measurement_latest_day) - dt.timedelta(days=365)

    # Calculate the station frequency in data set.
    station_freq = session.query(Measurement.station, func.count(Measurement.station).\
                        label('count')).\
                        group_by(Measurement.station).order_by(desc('count')).\
                        all()

    # Perform a query to retrieve the date and temperature observations of the most active station in data set for the last year 
    year_tobs = session.query(Measurement.tobs).\
                filter(Measurement.date > measurement_1year_back).\
                filter(Measurement.station == f'{station_freq[0][0]}').\
                all()

    session.close()

    # Convert list of tuples into normal list
    tobs_last_year = list(np.ravel(year_tobs))

    return jsonify(tobs_last_year)

@app.route("/api/v1.0/<start>")
def temperature_openrange(start):
    temp_oprange_labels = ['TMIN', 'TAVG', 'TMAX']
    temp_oprange_values = []

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the minimun temperature starting on a given date in data set.
    oprange_temp_min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).all()
    temp_oprange_values.append(oprange_temp_min[0][0])

    # Calculate the average temperature starting on a given date in data set.
    oprange_temp_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    temp_oprange_values.append(oprange_temp_avg[0][0])

    # Calculate the maximum temperature starting on a given date in data set.
    oprange_temp_max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    temp_oprange_values.append(oprange_temp_max[0][0])

    session.close()

    temp_oprange_dict = {temp_oprange_labels[i]: temp_oprange_values[i] for i in range(len(temp_oprange_labels))}

    return jsonify(temp_oprange_dict)

@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end):
    temp_range_labels = ['TMIN', 'TAVG', 'TMAX']
    temp_range_values = []

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the minimun temperature from a given date range in data set.
    range_temp_min = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temp_range_values.append(range_temp_min[0][0])

    # Calculate the average temperature from a given date range in data set.
    range_temp_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temp_range_values.append(range_temp_avg[0][0])

    # Calculate the maximum temperature from a given date range in data set.
    range_temp_max = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temp_range_values.append(range_temp_max[0][0])

    session.close()

    temp_range_dict = {temp_range_labels[i]: temp_range_values[i] for i in range(len(temp_range_labels))}

    return jsonify(temp_range_dict)

if __name__ == '__main__':
    app.run(debug=True)

