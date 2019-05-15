from __future__ import division
import time
import math
import os
import datetime as DT
from datetime import datetime
import sys
import subprocess
from time import sleep
import mysql.connector as mariadb
from threading import Thread
from os.path import exists
import numpy as np

interface = "wlp3s0"

MaxTemp = 30
MinTemp = 0
CurrentTemp = 0
DesiredTemp = 30
CurrentWIFI = 0
HeatingOn = False
LastMovement = datetime.now()
LastCheck = datetime.now() - DT.timedelta(days=2)
LastChange = datetime.now()
running = True
MorningOn = DT.time(0,0)
MorningOff = DT.time(0,0)
AfternoonOn = DT.time(0,0)
AfternoonOff = DT.time(0,0)
WeekendOn = DT.time(0,0)
WeekendOff = DT.time(0,0)
WeekendAftOn = DT.time(0,0)
WeekendAftOff = DT.time(0,0)
HeatingChangeTime = DT.time(0,0)
HeatingAdvanceTime = DT.time(0,0)
HeatingAlwaysOn = False
TempVariance = 0.5
HeatingAdvance = False
TempDesiredManual = False


def read_DB_rolling_temp(*args):
    temperature = []

    query_string = """
    select temp
    from temp_logger.temperature
    where device in ("RPi_0","RPi_2")
    and ts > date_sub(now(), interval 60 second)
    """

    con = mariadb.connect(host='192.168.0.10', port='3306', user='pi_test', database='temp_logger')
    cur = con.cursor()
    cur.execute(query_string)

    for row in cur:
        temperature.append(row[0])

    con.close()

    return np.mean(temperature)

def Sensor(threadname, *args):
	global running
	global LastMovement
	global CurrentTemp
	global CurrentWIFI
	global MorningOn
	global MorningOff
	global AfternoonOn
	global AfternoonOff
	global WeekendOn
	global WeekendOff
	global WeekendAftOn
	global WeekendAftOff
	global HeatingOn
	global TempVariance
	global HeatingChangeTime
	global HeatingAdvanceTime
	global HeatingAlwaysOn
	global HeatingAdvance

	counter = 0

	while running:

		if(counter > 30):
			try:
				temp = read_DB_rolling_temp()
			except:
				print "SENSOR READ ERROR!"
            if temp is not None:
				CurrentTemp = temp

#### Need to work out what 'movement' is referring to
		if GPIO.input(17):
			#print ("Movement")
			LastMovement = datetime.now()
		if(counter>60):
			try:
                proc = subprocess.Popen(["iwconfig", interface],stdout=subprocess.PIPE, universal_newlines=True)
                out, err = proc.communicate()
                WIFI = 0
                for line in out.split("\n"):
                    if("Link Quality=" in line):
                        line = line.replace("Link Quality=","")
                        quality = line.split()[0].split('/')
                        WIFI = int(round(float(quality[0]) / float(quality[1]) * 100))
                        CurrentWIFI = WIFI
                        #print("WIFI : "+str(WIFI)+" %")
            except:
                print("WIFI READOUT ERROR!")
		if(counter>60):
			counter = 0
		else:
			counter = counter+1

		#
		if(CurrentTemp > 0):
			try:
			#if(CurrentTemp > 1):
				CurrentTime = DT.datetime.now()
				MorningOnTime = CurrentTime.replace(hour=MorningOn.hour,minute=MorningOn.minute,second=MorningOn.second)
				MorningOffTime = CurrentTime.replace(hour=MorningOff.hour,minute=MorningOff.minute,second=MorningOff.second)
				AfternoonOnTime = CurrentTime.replace(hour=AfternoonOn.hour, minute=AfternoonOn.minute, second=AfternoonOn.second)
				AfternoonOffTime = CurrentTime.replace(hour=AfternoonOff.hour, minute=AfternoonOff.minute, second=AfternoonOff.second)
				WeekendOnTime = CurrentTime.replace(hour=WeekendOn.hour, minute=WeekendOn.minute, second=WeekendOn.second)
				WeekendOffTime = CurrentTime.replace(hour=WeekendOff.hour, minute =WeekendOff.minute, second=WeekendOff.second)
				WeekendAftOnTime = CurrentTime.replace(hour=WeekendAftOn.hour, minute=WeekendAftOn.minute, second=WeekendAftOn.second)
				WeekendAftOffTime = CurrentTime.replace(hour=WeekendAftOff.hour, minute=WeekendAftOff.minute, second=WeekendAftOff.second)

				MovementDelta = LastMovement + DT.timedelta(0,1800)
				#OnChangeDelta = HeatingChangeTime + DT.timedelta(0,3600)
				if(CurrentTime.isoweekday() in range(1,6)):
					#print "Weekday loop"
					if(CurrentTime > MorningOnTime and CurrentTime < MorningOffTime):
						#
						MorningOnDelta = MorningOnTime + DT.timedelta(0,3600)
						if(CurrentTime < MorningOnDelta):
							if(CurrentTemp + TempVariance < DesiredTemp):
								if(HeatingOn == False):
									HeatingOn = True
							elif(int(CurrentTemp) >= int(DesiredTemp)):
								if(HeatingOn == True):
									HeatingOn = False
						elif(CurrentTime > MovementDelta):
							if(HeatingOn == True):
								HeatingOn = False
						else:
							if(CurrentTemp + TempVariance  < DesiredTemp):
								if(HeatingOn == False):
									HeatingOn = True
							elif(int(CurrentTemp) >= int(DesiredTemp)):
								if(HeatingOn == True):
									HeatingOn = False
						#
					elif(CurrentTime > AfternoonOnTime and CurrentTime < AfternoonOffTime):
						#
						#print "Afternoon loop"
						AfternoonOnDelta = AfternoonOnTime + DT.timedelta(0,3600)
						if(CurrentTime < AfternoonOnDelta):
							if(CurrentTemp + TempVariance < DesiredTemp):
								if(HeatingOn == False):
									HeatingOn = True
							elif(int(CurrentTemp) >= int(DesiredTemp)):
								if(HeatingOn == True):
									HeatingOn = False
						elif(CurrentTime > MovementDelta):
							#print "Movement Loop"
							if(HeatingOn == True):
								HeatingOn = False
						else:
							#print "No Movement"
							if(CurrentTemp + TempVariance < DesiredTemp):
								if(HeatingOn == False):
									HeatingOn = True
							elif(int(CurrentTemp) >= int(DesiredTemp)):
								if(HeatingOn == True):
									HeatingOn = False
					else:
						if(HeatingOn == True):
							HeatingOn = False
				#Else its the weekend
				else:
					if(CurrentTime > WeekendOnTime and CurrentTime < WeekendOffTime):
						#
						WeekendDelta = WeekendOnTime + DT.timedelta(0,3600)
						if(CurrentTime < WeekendDelta):
							if(CurrentTemp + TempVariance < DesiredTemp):
								if(HeatingOn == False):
									HeatingOn = True
							elif(int(CurrentTemp) >= int(DesiredTemp)):
								if(HeatingOn == True):
									HeatingOn = False
						elif(CurrentTime > MovementDelta):
							if(HeatingOn == True):
								HeatingOn = False
						else:
							if(CurrentTemp+TempVariance < DesiredTemp):
								if(HeatingOn == False):
									HeatingOn = True
							elif(int(CurrentTemp) >= int(DesiredTemp)):
								if(HeatingOn == True):
									HeatingOn = False
					elif(CurrentTime > WeekendAftOnTime and CurrentTime < WeekendAftOffTime):
					#	#
						WeekendAftDelta = WeekendAftOnTime + DT.timedelta(0,3600)
						if(CurrentTime < WeekendAftDelta):
							if(CurrentTemp + TempVariance < DesiredTemp):
								if(HeatingOn == False):
									HeatingOn = True
							elif(int(CurrentTemp) >= int(DesiredTemp)):
								if(HeatingOn == True):
									HeatingOn = False
						elif(CurrentTime > MovementDelta):
							if(HeatingOn == True):
								HeatingOn = False
						else:
							if(CurrentTemp + TempVariance < DesiredTemp):
								if(HeatingOn == False):
									HeatingOn = True
							elif(int(CurrentTemp) >= int(DesiredTemp)):
								if(HeatingOn == True):
									HeatingOn = False
					else:
						if(HeatingOn == True):
							HeatingOn = False
			except:
				print "Time Calcs Error!"


		if(HeatingAdvance):
			HeatingAdvanceDelta = HeatingAdvanceTime + DT.timedelta(0,1800)
			if(CurrentTime > HeatingAdvanceDelta):
				HeatingAdvance = False
			else:
				HeatingOn = True
		if(HeatingAlwaysOn):
			HeatingOn = True

		#
		time.sleep(1)
	GPIO.cleanup()

def SQLSender(threadname, *args):
	global running
	global CurrentTemp
	global CurrentWIFI
	global CurrentHumid
	global DesiredTemp
	global HeatingOn
	global HotWaterOn
	global LastTemps
	global LastHumids
	global LastHeatings
	global LastCheck
	global MorningOn
	global MorningOff
	global AfternoonOn
	global AfternoonOff
	global TempVariance
	global WeekendOn
	global WeekendOff
	global WeekendAftOn
	global WeekendAftOff
	global HeatingAdvanceTime
	global HeatingAlwaysOn
	global HeatingAdvance
	global HeatingDesiredManual

	firstrun = True
	Heating = 0

	while(running):
		try:
			if(CurrentWIFI > 0):
				dsn = 'sqlserverdatasource'
				user = 'user'
				password = 'password'
				database = 'TDB'
				con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn,user,password,database)
        			print "SQL Trying to connect"
				cnxn = pyodbc.connect(con_string)
				cnxn.timeout = 120
				print "SQL Connected"
				cursor = cnxn.cursor()

				if(firstrun):
					firstrun = False
					parameters = []
					parameters.append(datetime.now())
					cursor.execute("UPDATE CONFIGTABLE SET varData=? WHERE varName='LASTBOOT'",parameters)
					cnxn.commit()

				cursor.execute("SELECT varData FROM CONFIGTABLE WHERE varName='HEATINGADVANCE'")
				row = cursor.fetchone()
				if row:
					if(int(row[0]) > 0):
						if(HeatingAdvance == False):
							HeatingAdvance = True
							HeatingAdvanceTime = DT.datetime.now()
					else:
						HeatingAdvance = False
				cursor.execute("SELECT varData FROM CONFIGTABLE WHERE varName='HEATINGALWAYSON'")
				row = cursor.fetchone()
				if row:
					if(int(row[0]) > 0):
						HeatingAlwaysOn = True
					else:
						HeatingAlwaysOn = False
				LastCheckDelta = LastCheck + DT.timedelta(hours=2)
				if(datetime.now() > LastCheckDelta):
					if(TempDesiredManual == False):
						cursor.execute("SELECT varData FROM CONFIGTABLE WHERE varName='DESIREDTEMP'")
						row = cursor.fetchone()
						if row:
							DesiredTemp = int(row[0])
					else:
						HeatingDesiredManual = False
						parameters = []
						parameters.append(DesiredTemp)
						cursor.execute("UPDATE CONFIGTABLE SET varData = ? WHERE varName='DESIREDTEMP'",parameters)
						cnxn.commit()
					cursor.execute("EXEC calcTimes")
					row = cursor.fetchone()
					if row:
						MorningOn = row[0]
						MorningOff = row[1]
						AfternoonOn = row[2]
						AfternoonOff = row[3]
						WeekendOn = row[4]
						WeekendOff = row[5]
						WeekendAftOn = row[6]
						WeekendAftOff = row[7]
						LastCheck = datetime.now()
						#print MorningOn
					cursor.execute("SELECT varData FROM CONFIGTABLE WHERE varName='TEMPVARIANCE'")
					row = cursor.fetchone()
					if row:
						TempVariance = float(row[0])

				parameters = []
				parameters.append(datetime.now())
				parameters.append(CurrentWIFI)
				parameters.append(CurrentTemp)
				parameters.append(CurrentHumid)
				MovementDelta = LastMovement + DT.timedelta(0,300)
				if(datetime.now() > MovementDelta):
					parameters.append(0)
				else:
					parameters.append(1)
				parameters.append(DesiredTemp)
				parameters.append(HeatingOn)
				parameters.append(HotWaterOn)
				if(CurrentTemp > 0):
					print "Inserting"
					cursor.execute("INSERT INTO DATATABLE VALUES(?, ?, ?, ?,?,?,?,?)",parameters)
					cnxn.commit()
					print "Complete"

				cursor.execute("SELECT varData FROM CONFIGTABLE WHERE varName = 'REBOOTDEVICE'")
				if row:
					row = cursor.fetchone()
					SQLReboot = int(row[0])
					if(SQLReboot > 0):
						cursor.execute("UPDATE CONFIGTABLE SET varData='0' WHERE varName='REBOOTDEVICE'")
						cnxn.commit()
						comand = "/usr/bin/sudo /sbin/reboot"
						process = subprocess.Popen(comand.split(), stdout=subprocess.PIPE)
						output = process.communicate()[0]

				cursor.close()
				cnxn.close()

		except:
			print "SQL THREAD ERROR"
		time.sleep((60*5))



#Thread(target=main, args=('Main',1)).start()
#launch the pulse thread
Thread(target=Sensor, args=('Sensor',1)).start()

Thread(target=SQLSender, args=('SQL',1)).start()
