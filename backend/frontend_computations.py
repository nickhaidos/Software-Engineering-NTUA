from flask import Flask, request, render_template, abort
from flask_mysqldb import MySQL
import datetime
import string
import json
import os
import numpy as np

import warnings
warnings.filterwarnings("ignore")

sql_connection_to_use = None
f = '%Y-%m-%d %H:%M:%S'

def set_connection(item):
	global sql_connection_to_use
	sql_connection_to_use = item

def correction(num1):
	num = str(num1)
	if len(num)==1:
		return "0"+num
	else:
		return num

def compute(df, dt):
	df = df + " 00:00:00"
	dt = dt + " 23:59:59"
	operators = ["AO", "EG", "GF", "KO", "MR", "NE", "OO"]


	# TOP RIGHT DIAGRAM
	cur = sql_connection_to_use.connection.cursor()
	req1 = f""" SELECT StationOperatorID, COUNT(*) 
				FROM `passes` 
				WHERE TagOperatorID != StationOperatorID AND Time_stamp BETWEEN '{df}' AND '{dt}'
				GROUP BY StationOperatorID"""
	cur.execute(req1)
	temp = cur.fetchall()
	total_passes_labels = [temp[i][0] for i in range(len(temp))]
	total_passes = [temp[i][1] for i in range(len(temp))]
	#-----------------

	# TOP LEFT DIAGRAM
	cur = sql_connection_to_use.connection.cursor()
	req2 = f""" SELECT StationOperatorID, StationNumber, COUNT(*) AS Passes 
				FROM `passes` 
				WHERE Time_stamp BETWEEN '{df}' AND '{dt}'
				GROUP BY StationOperatorID, StationNumber
				ORDER BY Passes DESC LIMIT 10
				"""
	cur.execute(req2)
	temp = cur.fetchall()
	station_passes_labels = [temp[i][0]+correction(temp[i][1]) for i in range(len(temp))]
	station_passes = [temp[i][2] for i in range(len(temp))]
	#-----------------


	# BOTTOM LEFT DIAGRAM
	cur = sql_connection_to_use.connection.cursor()
	debts_labels = []
	debts = []
	ows = dict()
	for operator in operators:
		ows[operator]=dict()
		req3 = f"""WITH ops(OP_IDs) AS (
					    SELECT DISTINCT TagOperatorID as OP_IDs
					    FROM passes
					    WHERE TagOperatorID != '{operator}'
					),
					ops2(IDDS, Counts, Sums) AS (
                        SELECT OP_IDs, COUNT(Charge), SUM(Charge)
                        FROM `ops` join `passes` ON (passes.StationOperatorID = ops.OP_IDs)
                        WHERE passes.TagOperatorID = '{operator}'
                        AND passes.Time_stamp BETWEEN '{df}' AND '{dt}'
                        GROUP BY OP_IDs
                    )
					SELECT OP_IDs, IFNULL(Sums,0)
					FROM `ops` left join `ops2` ON (ops.OP_IDs = ops2.IDDS)
					"""
		cur.execute(req3)       # returns what the Operator ows
		temp = cur.fetchall()
		for i in range(len(temp)):
			ows[operator][temp[i][0]]=temp[i][1]
		req4 = f""" WITH ops(OP_IDs) AS (
						    SELECT DISTINCT TagOperatorID as OP_IDs
						    FROM passes
						    WHERE TagOperatorID != '{operator}'
						),
						ops2(IDDS, Counts, Sums) AS (
						    SELECT OP_IDs, COUNT(Charge), SUM(Charge)
						    FROM `ops` join `passes` ON (passes.TagOperatorID = ops.OP_IDs)
						    WHERE passes.StationOperatorID = '{operator}'
						        AND passes.Time_stamp BETWEEN '{df}' AND '{dt}'
						    GROUP BY OP_IDs
						)
						SELECT OP_IDs, IFNULL(Sums,0)
						FROM `ops` left join `ops2` ON (ops.OP_IDs = ops2.IDDS)
					"""
		cur.execute(req4)            # returns what the Operator is owed
		temp = cur.fetchall()
		for i in range(len(temp)):
			ows[operator][temp[i][0]]= max(0, ows[operator][temp[i][0]]-temp[i][1])
		debts_labels.append(operator)
		debts.append(sum(ows[operator].values()))
	#-----------------

	# BOTTOM RIGHT DIAGRAM
	cur = sql_connection_to_use.connection.cursor()
	time_bins_labels = ["00-01", "01-02", "02-03", "03-04", "04-05", "05-06", "06-07", "07-08", "08-09", "09-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17", "17-18", "18-19", "19-20", "20-21", "21-22", "22-23", "23-24"]

	req5 = f""" WITH times(time_bins) AS (
				    SELECT DISTINCT HOUR(Time_stamp)
				    FROM `passes`
				    WHERE 1
				),
				finale(stamps, bins) AS(
				    SELECT passes.Time_stamp as stamps, times.time_bins as bins
				    FROM `passes` right outer join `times` ON (HOUR(passes.Time_stamp) = times.time_bins)
				    WHERE passes.Time_stamp BETWEEN "{df}" AND "{dt}"
				)
				SELECT times.time_bins, IFNULL(COUNT(finale.bins),0)
				FROM finale right join times ON (finale.bins = times.time_bins)
				GROUP BY times.time_bins
				ORDER BY times.time_bins ASC
				"""
	cur.execute(req5)
	temp = cur.fetchall()
	temp = np.array(temp)
	time_bins_passes = (temp[:, 1]).tolist()
	#-----------------

	return (total_passes_labels, total_passes, station_passes_labels, station_passes, debts_labels, debts, time_bins_labels, time_bins_passes)
