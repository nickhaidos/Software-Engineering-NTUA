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

class PassesCost(Resource):
	def get(self, op1_ID, op2_ID, date_from, date_to):
		try:
			parser = reqparse.RequestParser()
			parser.add_argument('format', type=str)
			args = parser.parse_args()

			if args['format']!="json" and args['format']!="csv" and args['format']:
				return {}, 400

			if (not args['format']) or args['format']=="json" or (args['format']!="json" and args['format']!="csv"):
				format_type = "json"
			else:
				format_type = "csv"
			
			if (not op1_ID) or (op1_ID==op2_ID) or (not op2_ID) or (not date_from) or (not date_to) or (not date_from.isnumeric()) or (not date_to.isnumeric()) or len(date_to)!=8 or len(date_from)!=8:
				return {}, 400
			
			df = date_from[0:4] + "-" + date_from[4:6] + "-" + date_from[6:8] + " 00:00:00"
			dt = date_to[0:4] + "-" + date_to[4:6] + "-" + date_to[6:8] + " 23:59:59"
			ret = dict()
			cur = sql_connection_to_use.connection.cursor()
			req1 = f"""SELECT COUNT(*), SUM(Charge)
							FROM `passes` 
							WHERE TagOperatorID = '{op2_ID}'
									AND StationOperatorID = '{op1_ID}'
									AND Time_stamp BETWEEN '{df}' AND '{dt}'"""
			cur.execute(req1)
			data = cur.fetchall()
			if (not data):
				return {}, 402
			ret["op1_ID"] = op1_ID
			ret["op2_ID"] = op2_ID
			ret["RequestTimestamp"] = datetime.datetime.now().strftime(f)
			ret["PeriodFrom"] = df
			ret["PeriodTo"] = dt
			ret["NumberOfPasses"] = data[0][0]
			if data[0][0]==0:
				ret["PassesCost"] = 0
			else:
				ret["PassesCost"] = round(data[0][1], 3)

			if format_type=="json":
				return ret, 200
			df = pd.DataFrame([ret])
			
			return df.to_csv(index=False, line_terminator='\n'), 200
		except:
			return {}, 500
