# Import libraries, class, etc...
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# Connecting to Database, reflecting tables and creating session
engine = create_engine(f"sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station


# Create app
app = Flask(__name__)


# Define routes
# Homepage
#List all routes that are available.
@app.route("/")
def home():
    return(
        f"<h1 align=center>Welcome to Hawaii Weather Page</h1><br/>"
        f"<u>List of available routes </u> - <i>access data using paths below:</i><br/>"
        f"Precipitation:  /api/v1.0/precipitation<br/>"
        f"Stations:   /api/v1.0/stations<br/>"
        f"Temperatures:  /api/v1.0/tobs<br/>"
        f"Start Date: /api/v1.0/start<br/>"
        f"Trip Start-End Date:  /api/v1.0/start/end"
    )


# Precipitation - 
# Convert the query results to a dictionary using date as the key and prcp as the value.  
# Return the JSON representation of the dictionary.
@app.route("/api/v1.0/precipitation")
def Precipitation():
    session = Session(engine)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').\
                     group_by(Measurement.date).all()
    session.close()
    # Convert results to dictionary
    all_p_dict = []
    for date, prcp in precipitation_data:
        p_dict = {}
        p_dict['date'] = date
        p_dict['precipitation'] = prcp
        all_p_dict.append(p_dict)
    return jsonify(all_p_dict)

# Stations - Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def Stations():
    session = Session(engine)
    stations = session.query(Station.station, Station.name).all()
    session.close()
    # Convert results to list
    s_list = list(np.ravel(stations))
    return jsonify(s_list)

# Temperatures - Query the dates and temperature observations of the most active station for the last year of data.  
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def temperatures():
    session = Session(engine)
    temperatures = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station =='USC00519281').\
                    filter(Measurement.date >= '2016-08-23').all()
    session.close()
    # Convert results to list
    t_list = list(np.ravel(temperatures))
    return jsonify(t_list)

# Trip Dates -
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    ttemperatures = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                    filter(Measurement.station == Station.station).\
                    filter(Measurement.date >= '2016-08-23').\
                    group_by(Measurement.date).all()

                    
    session.close()
    
    # Convert results to dictionary
    all_tminmaxavg_dict = []
    for date, tmin, tmax, tavg in ttemperatures:
        t_dict = {}
        t_dict['date'] = date
        t_dict['tmin'] = tmin
        t_dict['tmax'] = tmax
        t_dict['tavg'] = tavg
        all_tminmaxavg_dict.append(t_dict)
    return jsonify(all_tminmaxavg_dict)

    

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    trip_temps = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                    filter(Measurement.station == Station.station).\
                    filter(Measurement.date >= '2014-02-28').\
                    filter(Measurement.date <= '2014-03-05').\
                    group_by(Measurement.date).all()
    session.close()

    # Convert results to dictionary
    all_triptemps_dict = []
    for date, tmin, tmax, tavg in trip_temps:
        tr_dict = {}
        tr_dict['date'] = date
        tr_dict['tmin'] = tmin
        tr_dict['tmax'] = tmax
        tr_dict['tavg'] = tavg
        all_triptemps_dict.append(tr_dict)
    return jsonify(all_triptemps_dict)
    


# Define main behavior
if __name__=="__main__":
    app.run(debug=True)