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

class PassesPerStation(Resource):
	def get(self, stationID, date_from, date_to):
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
			
			if (not stationID) or (not date_from) or (not date_to) or (not date_from.isnumeric()) or (not date_to.isnumeric()) or len(date_to)!=8 or len(date_from)!=8:
				return {}, 400
			
			df = date_from[0:4] + "-" + date_from[4:6] + "-" + date_from[6:8] + " 00:00:00"
			dt = date_to[0:4] + "-" + date_to[4:6] + "-" + date_to[6:8] + " 23:59:59"
			ret = dict()

			cur = sql_connection_to_use.connection.cursor()

			req1 = f"""SELECT PassID, Time_stamp, Charge, VehicleID, TagOperatorID
							FROM `passes` 
							WHERE StationOperatorID LIKE '{stationID[0:2]}'
									AND StationNumber = {stationID[2:4]}
									AND Time_stamp BETWEEN '{df}' AND '{dt}'"""
			cur.execute(req1)
			data = cur.fetchall()

			req2 = f"""SELECT count(*)
							FROM `passes` 
							WHERE StationOperatorID LIKE '{stationID[0:2]}'
									AND StationNumber = {stationID[2:4]}
									AND Time_stamp BETWEEN '{df}' AND '{dt}'"""
			cur.execute(req2)
			nums = cur.fetchall()

			if (not data):
				return {}, 402

			ret["Station"] = stationID
			ret["StationOperator"] = stationID[0:2]
			ret["RequestTimestamp"] = datetime.datetime.now().strftime(f)
			ret["PeriodFrom"] = df
			ret["PeriodTo"] = dt
			ret["NumberOfPasses"] = nums[0][0]
			ret["PassesList"] = []
			for i, d in enumerate(data):
				if d[4]==stationID[0:2]:
					ptype = "home"
				else:
					ptype = "visitor"
				ret["PassesList"].append({"PassIndex": i, "PassID": d[0],"PassTimeStamp": d[1].strftime(f), "VehicleID": d[3], "TagProvider": d[4],"PassType": ptype, "PassCharge": d[2]})
			
			if format_type=="json":
				return ret, 200
			json_obj = json.dumps(ret)
			df = pd.read_json(json_obj)

			return df.to_csv(index=False, line_terminator='\n'), 200
		except:
			return {}, 500
