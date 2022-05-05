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

class PassesAnalysis(Resource):
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
			req1 = f"""SELECT PassID, StationNumber, Time_stamp, VehicleID, Charge
							FROM `passes` 
							WHERE TagOperatorID LIKE '{op2_ID}'
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
			ret["NumberOfPasses"] = 0
			ret["PassesList"] = []
			nums = 0
			for i, d in enumerate(data):
				ret["PassesList"].append({"PassIndex": nums, "PassID": d[0], "StationID": op1_ID+f"{d[1]:02d}", "TimeStamp": d[2].strftime(f), "VehicleID": d[3], "PassCharge": d[4]})
				nums += 1
			ret["NumberOfPasses"] = nums

			if format_type=="json":
				return ret, 200
			json_obj = json.dumps(ret)
			df = pd.read_json(json_obj)

			return df.to_csv(index=False, line_terminator='\n'), 200
		except:
			return {}, 500
