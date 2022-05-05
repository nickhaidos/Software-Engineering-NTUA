from flask import Flask, request, render_template, abort
from flask_mysqldb import MySQL
from flask_restful import Resource, Api, reqparse
import datetime
import string
import pandas as pd
import json
import os
dir_path = os.path.dirname(__file__)

sql_connection_to_use = None
f = '%Y-%m-%d %H:%M:%S'

def set_connection(item):
	global sql_connection_to_use
	sql_connection_to_use = item

class ResetPasses(Resource):
	def post(self):
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
			cur = sql_connection_to_use.connection.cursor()
			cur.execute("TRUNCATE `passes`")
			sql_connection_to_use.connection.commit()

			ret = {"status": "ok"}
			if format_type=="json":
				return ret, 200

			return "status\nok", 200
		except:
			ret = {"status": "failed"}
			if format_type=="json":
				return ret, 500

			return "status\nfailed", 500
