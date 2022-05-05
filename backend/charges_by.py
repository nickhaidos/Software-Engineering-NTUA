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

class ChargesBy(Resource):
	def get(self, op_ID, date_from, date_to):
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
			
			if (not op_ID) or (not date_from) or (not date_to) or (not date_from.isnumeric()) or (not date_to.isnumeric()) or len(date_to)!=8 or len(date_from)!=8:
				return {}, 400
			
			df = date_from[0:4] + "-" + date_from[4:6] + "-" + date_from[6:8] + " 00:00:00"
			dt = date_to[0:4] + "-" + date_to[4:6] + "-" + date_to[6:8] + " 23:59:59"
			ret = dict()
			cur = sql_connection_to_use.connection.cursor()
			req1 = f""" WITH ops(OP_IDs) AS (
						    SELECT DISTINCT TagOperatorID as OP_IDs
						    FROM passes
						    WHERE TagOperatorID != '{op_ID}'
						),
						ops2(IDDS, Counts, Sums) AS (
						    SELECT OP_IDs, COUNT(Charge), SUM(Charge)
						    FROM `ops` join `passes` ON (passes.TagOperatorID = ops.OP_IDs)
						    WHERE passes.StationOperatorID = '{op_ID}'
						        AND passes.Time_stamp BETWEEN '{df}' AND '{dt}'
						    GROUP BY OP_IDs
						)
						SELECT OP_IDs, IFNULL(Counts,0), IFNULL(Sums,0)
						FROM `ops` left join `ops2` ON (ops.OP_IDs = ops2.IDDS)"""
			cur.execute(req1)
			data = cur.fetchall()
			if (not data):
				return {}, 402
			ret["op_ID"] = op_ID
			ret["RequestTimestamp"] = datetime.datetime.now().strftime(f)
			ret["PeriodFrom"] = df
			ret["PeriodTo"] = dt
			ret["PPOList"] = []
			for i, d in enumerate(data):
				ret["PPOList"].append({"VisitingOperator": d[0], "NumberOfPasses": d[1], "PassesCost": round(d[2], 3)})

			if format_type=="json":
				return ret, 200
			json_obj = json.dumps(ret)
			df = pd.read_json(json_obj)

			return df.to_csv(index=False, line_terminator='\n'), 200
		except:
			return {}, 500
