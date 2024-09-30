# Import the dependencies.
from flask import Flask, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
#################################################
# Database Setup
#################################################
# Create the engine to the SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)
session = Session()



#################################################
# Flask Setup
#################################################
climate_app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@climate_app.route('/')
def index():
    return (
        "Welcome to the Climate API!<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start><br/>" #start = Start date
        "/api/v1.0/<start>/<end><br/>" #end = End Date
    )

@climate_app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)

    # Query the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

@climate_app.route('/api/v1.0/stations')
def stations():
    # Query all stations
    results = session.query(Station.station).all()
    stations_list = [station[0] for station in results]
    return jsonify(stations=stations_list)

@climate_app.route('/api/v1.0/tobs')
def tobs():
    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)

    # Query the dates and temperature observations of the most-active station for the previous year
    most_active_station_id = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the results to a list of dictionaries
    tobs_data = [{'date': date, 'temperature': tobs} for date, tobs in results]
    
    return jsonify(tobs_data)

@climate_app.route('/api/v1.0/<start>')
def start(start):
    # Query the minimum, average, and maximum temperatures for a specified start date
    results = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp'),
        func.max(Measurement.tobs).label('max_temp')
    ).filter(Measurement.date >= start).all()

    if not results or results[0].min_temp is None:
        return jsonify({"error": "No data available for the specified start date."}), 404

    # Convert the results to a dictionary
    temp_stats = {
        'Start Date': start,
        'Min Temperature': results[0].min_temp,
        'Avg Temperature': results[0].avg_temp,
        'Max Temperature': results[0].max_temp
    }
    
    return jsonify(temp_stats)

@climate_app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    # Query the minimum, average, and maximum temperatures for a specified start-end range
    results = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp'),
        func.max(Measurement.tobs).label('max_temp')
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    if not results or results[0].min_temp is None:
        return jsonify({"error": "No data available for the specified date range."}), 404

    # Convert the results to a dictionary
    temp_stats = {
        'Start Date': start,
        'End Date': end,
        'Min Temperature': results[0].min_temp,
        'Avg Temperature': results[0].avg_temp,
        'Max Temperature': results[0].max_temp
    }

    return jsonify(temp_stats)
       

if __name__ == '__main__':
    climate_app.run(debug=True)



