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


#takes in high/low/openPoint/prev_high/prev_low
#returns plusDM1 and Minus DM1
def S_t(pri, prev_S):
	smoothing = 3.0 #This can change depending on research
	current_S = pri*2.0/(smoothing+1.0)+prev_S*(1.0-2.0/(smoothing+1.0))
	return current_S

def V_t(prev_S, current_S):
	current_V = current_S - prev_S
	return current_V

def A_t(current_V, prev_V, prev_A):
	temp = current_V - prev_V
	smoothing = 7.0 #This can change depending on research
	current_A = temp*2.0/(smoothing+1.0)+prev_A*(1.0-2.0/(smoothing+1.0))
	return temp, current_A

def decision(pri, current_S, current_V, current_A, prev_action):
	if (pri > current_S and current_V > 0 and current_A > 0):
		action = "Buy"
		#sendText(action)

	elif (pri < current_S and current_V < 0 and current_A < 0):
		action = "Sell"
		#sendText(action)

	else:
		action = prev_action

	return action


#start at new hour
def start(pri, timeStamp):
	lastRow = []

	with open('EMA.csv','r+') as f:
		file = csv.reader(f)
		for row in file:
			last = row
	lastRow.append(last)
	flattened_list = [y for x in lastRow for y in x]

	prev_S = float(flattened_list[2])
	current_S = S_t(pri, prev_S)

	current_V = V_t(prev_S, current_S)

	prev_A = float(flattened_list[6])
	prev_V = float(flattened_list[3])
	temp, current_A = A_t(current_V, prev_V, prev_A)

	prev_action = flattened_list[7]
	action = decision(pri, current_S, current_V, current_A, prev_action)
	print action

	with open('EMA.csv','a+') as f:

		f.write('\n')
		f.write(str(timeStamp))
		f.write(',')
		f.write(str(pri))
		f.write(',')
		f.write(str(current_S))
		f.write(',')
		f.write(str(current_V))
		f.write(',')
		f.write(str(current_V))
		f.write(',')
		f.write(str(temp))
		f.write(',')
		f.write(str(current_A))
		f.write(',')
		f.write(str(action))
				
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






