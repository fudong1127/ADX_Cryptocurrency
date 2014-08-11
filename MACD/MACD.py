import csv
import urllib
import urllib2
import json
import time
import datetime
import threading
from time import gmtime, strftime, time, sleep
import smtplib




#Get to run at the top of every hour
def collectRaw(min):
	sec = min*60
	pause(sec)
	ret = ""
	while (ret == ""):
		try:
			ret = urllib2.urlopen(urllib2.Request('https://api.coindesk.com/v1/bpi/currentprice.json'))
		except:
			print "Exception at " + strftime("%d %b %H:%M", gmtime())
			continue
	pri = json.loads(ret.read())['bpi']['USD']['rate']
	timeStamp = strftime("%d %b %H:%M", gmtime())
	print "The price is " + pri + " at " + timeStamp + "."
	pri = float(pri)
	start(pri, timeStamp)

def MACD_Calc(pri, prev_12, prev_26, prev_signal):
	smoothing12 = 3.0 #This can change depending on research, but paper says 12
	smoothing26 = 7.0 #This can change depending on research, but paper says 26
	smoothing9 = 4.0 #This can change depending on research, but paper says 9
	current_12 = pri*2.0/(smoothing12+1.0)+prev_12*(1.0-2.0/(smoothing12+1.0))
	current_26 = pri*2.0/(smoothing26+1.0)+prev_26*(1.0-2.0/(smoothing26+1.0))
	MACD = current_12 - current_26
	signal = MACD*2.0/(smoothing9+1.0)+prev_signal*(1.0-2.0/(smoothing9+1.0))

	return current_12, current_26, MACD, signal


def centerlineBS(MACD, prev_actionCL):
	if (MACD > 0):
		actionCL = "Buy"
		
	else:
		actionCL = "Sell"

	#if (actionCL != prev_actionCL):
		#sendText(actionCL)
		# later this would be execute trade

	return actionCL

def signallineBS(MACD, prev_MACD, signal, prev_actionSL):
	if (signal < MACD and MACD > prev_MACD):
		actionSL = "Buy"

	elif (signal > MACD and MACD < prev_MACD):
		actionSL = "Sell"

	else:
		actionSL = prev_actionSL

	#if (actionSL != prev_actionSL):
		#sendText(actionSL)
		# later this would be execute trade

	return actionSL

def start(pri, timeStamp):
	lastRow = []

	with open('MACD.csv','r+') as f:
		file = csv.reader(f)
		for row in file:
			last = row
	lastRow.append(last)
	flattened_list = [y for x in lastRow for y in x]

	prev_12 = float(flattened_list[2])
	prev_26 = float(flattened_list[3])
	prev_signal = float(flattened_list[5])
	current_12, current_26, MACD, signal = MACD_Calc(pri, prev_12, prev_26, prev_signal)

	prev_actionCL = flattened_list[6]
	actionCL = centerlineBS(MACD, prev_actionCL)

	prev_actionSL = flattened_list[7]
	prev_MACD = float(flattened_list[4])
	actionSL = signallineBS(MACD, prev_MACD, signal, prev_actionSL)

	print "Centerline says " + actionCL
	print "Singalline says " + actionSL

	with open('MACD.csv','a+') as f:

		f.write('\n')
		f.write(str(timeStamp))
		f.write(',')
		f.write(str(pri))
		f.write(',')
		f.write(str(current_12))
		f.write(',')
		f.write(str(current_26))
		f.write(',')
		f.write(str(MACD))
		f.write(',')
		f.write(str(signal))
		f.write(',')
		f.write(str(actionCL))
		f.write(',')
		f.write(str(actionSL))
				
	print "New line added at " + timeStamp

	pause(3600)

def runThis(min):
	while True:
		collectRaw(min)

def pause(n):
	start = time()
	while (time() - start < n):
		sleep(n - (time() - start))

def sendText(action):
	message = "You should " + action + " bitcoin!"

	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.starttls()
	server.login("btctext9@gmail.com","")
	server.sendmail("btctext9@gmail.com", "", message)
	server.sendmail("btctext9@gmail.com", "", message)
	#server.sendmail("btctext9@gmail.com", "", message)
	server.quit()






