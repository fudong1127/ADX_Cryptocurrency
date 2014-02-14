import csv
import urllib
import urllib2
import json
import time
import datetime
import threading
from time import localtime, strftime, time, sleep
import smtplib





def collectRaw():
	timeStamp = strftime("%d %b %H:%M", localtime())
	datapoints = []
	temp = 0
	while len(datapoints) < 60:
		try:
			temp = collectRawHelper()
			datapoints.append(temp)
			pause(58)
		except:
			print "Exception at " + strftime("%d %b %H:%M", localtime())
			continue
	#exit loop when all 60 are a gathered
	maxPoint = max(datapoints)
	minPoint = min(datapoints)
	closePoint = datapoints[-1]
	openPoint = datapoints[0]   # first element of hour; NOT close of previous hour
	start(openPoint, maxPoint, minPoint, closePoint, timeStamp)

#returns the last publically excecuted trade
def collectRawHelper():
	#TODO get last publically excecuted trade
	method = "/prices/spot_rate"
	ret = urllib2.urlopen(urllib2.Request('https://coinbase.com/api/v1' + method))
	pri = json.loads(ret.read())['amount']
	return float(pri)


#takes in high/low/openPoint/prev_high/prev_low
#returns plusDM1 and Minus DM1
def trend1(openPoint,high,low,prev_high,prev_low):
	tr1 = max(high - low,abs(high - openPoint),abs(low - openPoint))
	# Calculate +DM1 and -DM1
	if (high - prev_high)>(prev_low - low):
		minusDM1 = 0
		if (high-prev_high)>0:
			plusDM1 = high - prev_high
		else:
			plusDM1 = 0
	else:
		plusDM1 = 0
		if (prev_low - low)>0:
			minusDM1 = prev_low - low
		else:
			minusDM1 = 0
	return tr1, plusDM1, minusDM1

#takes in prev_tr14/prev_minusDM14/prev_plusDM14/tr1, plusDM1, minusDM1
#returns plusDM14 and minus DM14
def trend14(tr1, plusDM1, minusDM1, prev_tr14,prev_plusDM14,prev_minusDM14):
	tr14 = (prev_tr14*13/14)+tr1
	minusDM14 = (prev_minusDM14*13/14)+minusDM1
	plusDM14 = (prev_plusDM14*13/14)+plusDM1
	return tr14, plusDM14, minusDM14


def adx(tr14, plusDM14, minusDM14, prev_ADX):
	plusDI14 = plusDM14/tr14*100
	minusDI14 = minusDM14/tr14*100
	diffDI14 = abs(plusDI14-minusDI14)
	sumDI14 = plusDI14+minusDI14
	DX = (diffDI14/sumDI14)*100
	ADX = (prev_ADX*13+DX)/14
	return plusDI14, minusDI14, diffDI14, sumDI14, DX, ADX


def decision(plusDI14,minusDI14, ADX, previous_trendExist):
	if (plusDI14>minusDI14):
		direction = "Up"
	else:
		direction = "Down"

	if (ADX > 25):
		if (previous_trendExist == "newTrend"    or   previous_trendExist == "currentTrend"):
				current_trendExist = "currentTrend"
		else:
				current_trendExist = "newTrend"
	else:
		current_trendExist = "noTrend"
	return direction, current_trendExist

#Put in email and text alert
def execute(direction, current_trendExist):
	if (current_trendExist == "newTrend"):
		if (direction == "Up"):
			action = "Buy"
			sendText(action)
				
		else:
			action = "Sell"
			sendText(action)
		
	else:
		action = "Hold"
	return action


#start at new hour
def start(openPoint, high, low, closePoint, timeStamp):
	lastRow = []

	with open('BTC.csv','r+') as f:
		file = csv.reader(f)
		for row in file:
			last = row

	lastRow.append(last)

	flattened_list = [y for x in lastRow for y in x]

		#write to csv

	prev_high = float(flattened_list[2])
	prev_low = float(flattened_list[3])
	tr1, plusDM1, minusDM1 = trend1(openPoint, high, low, prev_high, prev_low)
		#write to csv

	prev_tr14 = float(flattened_list[8])
	prev_minusDM14 = float(flattened_list[10])
	prev_plusDM14 = float(flattened_list[9])
	tr14, plusDM14, minusDM14 = trend14(tr1, plusDM1, minusDM1, prev_tr14,prev_plusDM14,prev_minusDM14);
		#write to csv

	prev_ADX = float(flattened_list[16])
	plusDI14, minusDI14, diffDI14, sumDI14, DX, ADX = adx(tr14, plusDM14, minusDM14, prev_ADX)
		#write to csv

	previous_trendExist = flattened_list[17]
	direction, current_trendExist = decision(plusDI14,minusDI14, ADX, previous_trendExist)
		#write to csv

	action = execute(direction, current_trendExist)

	with open('BTC.csv','a+') as f:

		f.write('\n')
		f.write(str(timeStamp))
		f.write(',')
		f.write(str(openPoint))
		f.write(',')
		f.write(str(high))
		f.write(',')
		f.write(str(low))
		f.write(',')
		f.write(str(closePoint))
		f.write(',')
		f.write(str(tr1))
		f.write(',')
		f.write(str(plusDM1))
		f.write(',')
		f.write(str(minusDM1))
		f.write(',')
		f.write(str(tr14))
		f.write(',')
		f.write(str(plusDM14))
		f.write(',')
		f.write(str(minusDM14))
		f.write(',')
		f.write(str(plusDI14))
		f.write(',')
		f.write(str(minusDI14))
		f.write(',')
		f.write(str(diffDI14))
		f.write(',')
		f.write(str(sumDI14))
		f.write(',')
		f.write(str(DX))
		f.write(',')
		f.write(str(ADX))
		f.write(',')
		f.write(str(current_trendExist))
		f.write(',')
		f.write(str(direction))
		f.write(',')
		f.write(str(action))
		
	print "New line added at " + timeStamp

def runThis():
	while True:
		collectRaw()

def pause(n):
	start = time()
	while (time() - start < n):
		sleep(n - (time() - start))

def sendText(action):
	message = "You should " + action + " bitcoin!"

	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.starttls()
	server.login("btctext9@gmail.com","26kDiwo3lP!K4&g")
	server.sendmail("btctext9@gmail.com", "3038754511@txt.att.net", message)
	server.sendmail("btctext9@gmail.com", "sscolnick@gmail.com", message)
	#server.sendmail("btctext9@gmail.com", "3032500788@txt.att.net", message)
	server.quit()






