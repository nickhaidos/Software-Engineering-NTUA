from flask import Flask, request, render_template, abort, redirect
from flask_mysqldb import MySQL
from flask_restful import Resource, Api, reqparse
import datetime
import string
import pandas as pd
import json

import health_check
import passes_per_station
import reset_stations
import reset_passes
import reset_vehicles
import passes_analysis
import passes_cost
import charges_by
import frontend_computations

f = '%Y-%m-%d %H:%M:%S'
app = Flask(__name__)
api = Api(app)

mysql = MySQL()
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'interoperability_ver1'

mysql = MySQL(app)


health_check.set_connection(mysql)
passes_per_station.set_connection(mysql)
reset_stations.set_connection(mysql)
reset_passes.set_connection(mysql)
reset_vehicles.set_connection(mysql)
passes_analysis.set_connection(mysql)
passes_cost.set_connection(mysql)
charges_by.set_connection(mysql)
frontend_computations.set_connection(mysql)



@app.route('/interoperability/frontend/', methods=["GET", "POST"])
def front_end():

	if request.method == "POST":
		req = request.form
		df = req["date_from"]
		dt = req["date_to"]
		data = frontend_computations.compute(df, dt)
		return render_template("index.html", dataa=data, df=df, dt=dt)

	#dd = datetime.datetime.today().strftime('%Y-%m-%d')
	data = frontend_computations.compute("2021-07-14", "2021-08-14")

	return render_template("index.html", dataa=data, df="2021-07-14", dt="2021-08-14")



api.add_resource(health_check.HealthCheck, '/interoperability/api/admin/healthcheck/')
api.add_resource(reset_passes.ResetPasses, '/interoperability/api/admin/resetpasses/')
api.add_resource(reset_stations.ResetStations, '/interoperability/api/admin/resetstations/')
api.add_resource(reset_vehicles.ResetVehicles, '/interoperability/api/admin/resetvehicles/')

api.add_resource(passes_per_station.PassesPerStation, '/interoperability/api/PassesPerStation/<string:stationID>/<string:date_from>/<string:date_to>/')
api.add_resource(passes_analysis.PassesAnalysis, '/interoperability/api/PassesAnalysis/<string:op1_ID>/<string:op2_ID>/<string:date_from>/<string:date_to>/')
api.add_resource(passes_cost.PassesCost, '/interoperability/api/PassesCost/<string:op1_ID>/<string:op2_ID>/<string:date_from>/<string:date_to>/')
api.add_resource(charges_by.ChargesBy, '/interoperability/api/ChargesBy/<string:op_ID>/<string:date_from>/<string:date_to>/')

if __name__=='__main__':
	app.run(debug=False, port=9103)