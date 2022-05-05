from flask import Flask, request, render_template, abort
from flask_mysqldb import MySQL
from flask_restful import Resource, Api, reqparse
import datetime
import string
import pandas as pd
import json


sql_connection_to_use = None
f = '%Y-%m-%d %H:%M:%S'

def set_connection(item):
	global sql_connection_to_use
	sql_connection_to_use = item

class HealthCheck(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('format', type=str)
		args = parser.parse_args()

		if args['format']!="json" and args['format']!="csv" and args['format']:
			return {}, 400

		if (not args['format']) or args['format']=="json" or (args['format']!="json" and args['format']!="csv"):
			format_type = "json"
		else:
			format_type = "csv"
			
		try:
			db_con = sql_connection_to_use.connection
			ret = {"status": "ok", "dbconnection" : "app.config['MYSQL_HOST'] = 'localhost' app.config['MYSQL_PORT'] = 3306 app.config['MYSQL_USER'] = 'root' app.config['MYSQL_PASSWORD'] = '' app.config['MYSQL_DB'] = 'interoperability_ver1' mysql = MySQL(app) db_con = mysql.connection"}
			if format_type=="json":
				return ret, 200

			return "status,dbconnection\nok,app.config['MYSQL_HOST'] = 'localhost' app.config['MYSQL_PORT'] = 3306 app.config['MYSQL_USER'] = 'root' app.config['MYSQL_PASSWORD'] = '' app.config['MYSQL_DB'] = 'interoperability_ver1' mysql = MySQL(app) db_con = mysql.connection", 200
		except:
			ret = {"status": "failed", "dbconnection" : "app.config['MYSQL_HOST'] = 'localhost' app.config['MYSQL_PORT'] = 3306 app.config['MYSQL_USER'] = 'root' app.config['MYSQL_PASSWORD'] = '' app.config['MYSQL_DB'] = 'interoperability_ver1' mysql = MySQL(app) db_con = mysql.connection"}
			if format_type=="json":
				return ret, 500

			return "status,dbconnection\nfailed,app.config['MYSQL_HOST'] = 'localhost' app.config['MYSQL_PORT'] = 3306 app.config['MYSQL_USER'] = 'root' app.config['MYSQL_PASSWORD'] = '' app.config['MYSQL_DB'] = 'interoperability_ver1' mysql = MySQL(app) db_con = mysql.connection", 500
