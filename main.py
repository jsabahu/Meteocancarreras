#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import os
import glob
import sys
import re
import subprocess
import MySQLdb as mdb
import datetime
import mysql.connector as mariadb
import smbus
import Adafruit_DHT

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(19, GPIO.IN)
#state = GPIO.input(19)

#if (state is True):
	#print ("ay mama que nos morimos")
#else:
	#print ("estamos en la salvacion")



##### BLOC DH22 ############################################################################

# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
sensor = Adafruit_DHT.DHT22

# Example using a Raspberry Pi with DHT sensor
# connected to GPIO23.
pindh = 22

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
humiditydh, temperaturedh = Adafruit_DHT.read_retry(sensor, pindh)

# Note that sometimes you won't get a reading and
# the results will be null (because Linux can't
# guarantee the timing of calls to read the sensor).
# If this happens try again!

#if humiditydh is not None and temperaturedh is not None:
#    print('Temperatura DH 22: {0:0.1f}*C  Humitat DH22: {1:0.1f}%'.format(temperaturedh, humiditydh))
#else:
#    print('Failed to get reading. Try again!')






###### BLOC BMP280 ################################################################################

def read_bmp280():
	# Get I2C bus
	bus = smbus.SMBus(1)
	# BMP280 address, 0x76(118)
	# Read data back from 0x88(136), 24 bytes
	b1 = bus.read_i2c_block_data(0x76, 0x88, 24)
	# Convert the data
	# Temp coefficents
	dig_T1 = b1[1] * 256 + b1[0]
	dig_T2 = b1[3] * 256 + b1[2]
	if dig_T2 > 32767 :
        	dig_T2 -= 65536
	dig_T3 = b1[5] * 256 + b1[4]
	if dig_T3 > 32767 :
        	dig_T3 -= 65536
	# Pressure coefficents
	dig_P1 = b1[7] * 256 + b1[6]
	dig_P2 = b1[9] * 256 + b1[8]
	if dig_P2 > 32767 :
        	dig_P2 -= 65536
	dig_P3 = b1[11] * 256 + b1[10]
	if dig_P3 > 32767 :
        	dig_P3 -= 65536
	dig_P4 = b1[13] * 256 + b1[12]
	if dig_P4 > 32767 :
        	dig_P4 -= 65536
	dig_P5 = b1[15] * 256 + b1[14]
	if dig_P5 > 32767 :
        	dig_P5 -= 65536
	dig_P6 = b1[17] * 256 + b1[16]
	if dig_P6 > 32767 :
        	dig_P6 -= 65536
	dig_P7 = b1[19] * 256 + b1[18]
	if dig_P7 > 32767 :
        	dig_P7 -= 65536
	dig_P8 = b1[21] * 256 + b1[20]
	if dig_P8 > 32767 :
        	dig_P8 -= 65536
	dig_P9 = b1[23] * 256 + b1[22]
	if dig_P9 > 32767 :
        	dig_P9 -= 65536
	# BMP280 address, 0x76(118)
	# Select Control measurement register, 0xF4(244)
	# 0x27(39) Pressure and Temperature Oversampling rate = 1
	# Normal mode
	bus.write_byte_data(0x76, 0xF4, 0x27)
	# BMP280 address, 0x76(118)
	# Select Configuration register, 0xF5(245)
	# 0xA0(00) Stand_by time = 1000 ms
	bus.write_byte_data(0x76, 0xF5, 0xA0)
	time.sleep(0.5)
	# BMP280 address, 0x76(118)
	# Read data back from 0xF7(247), 8 bytes
	# Pressure MSB, Pressure LSB, Pressure xLSB, Temperature MSB, Temperature LSB,
	# Temperature xLSB and two unused bytes (BMP280 has no humidity sensor)
	data = bus.read_i2c_block_data(0x76, 0xF7, 8)
	# The BMP280 does not supply humidity data
	# Convert pressure and temperature data to 19-bits
	adc_p = ((data[0] * 65536) + (data[1] * 256) + (data[2] & 0xF0)) / 16
	adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16
	# Temperature offset calculations
	var1 = ((adc_t) / 16384.0 - (dig_T1) / 1024.0) * (dig_T2)
	var2 = (((adc_t) / 131072.0 - (dig_T1) / 8192.0) * ((adc_t)/131072.0 - (dig_T1)/8192.0)) * (dig_T3)
	t_fine = (var1 + var2)
	cTemp = (var1 + var2) / 5120.0
	fTemp = cTemp * 1.8 + 32
	# Pressure offset calculations
	var1 = (t_fine / 2.0) - 64000.0
	var2 = var1 * var1 * (dig_P6) / 32768.0
	var2 = var2 + var1 * (dig_P5) * 2.0
	var2 = (var2 / 4.0) + ((dig_P4) * 65536.0)
	var1 = ((dig_P3) * var1 * var1 / 524288.0 + ( dig_P2) * var1) / 524288.0
	var1 = (1.0 + var1 / 32768.0) * (dig_P1)
	p = 1048576.0 - adc_p
	p = (p - (var2 / 4096.0)) * 6250.0 / var1
	var1 = (dig_P9) * p * p / 2147483648.0
	var2 = p * (dig_P8) / 32768.0
	pressure = (p + (var1 + var2 + (dig_P7)) / 16.0) / 100
	# Output data to screen
	#print "Temperatura BMP280 : %.2f C" %cTemp
	#print "Pressio BMP280 : %.2f hPa " %pressure
	return (cTemp,pressure)
#temperaturebmp,pressurebmp = read_bmp280()
#print('Temperatura BMP 280: {0:0.1f}*C  Pressio BMP 280: {1:0.1f}hpa'.format(temperaturebmp, pressurebmp))

####BLOC DS18B20 ################################################################################################

databaseUsername="" #YOUR MYSQL USERNAME, USUALLY ROOT
databasePassword="" #YOUR MYSQL PASSWORD
databaseName="WordpressDB" #do not change unless you named the Wordpress database with some other name

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def saveToDatabase(temperature,temperaturedh,humidity,temperaturebmp,pressure,rainfall):

        con=mariadb.connect(host="localhost", user=databaseUsername, password=databasePassword, database=databaseName)
        currentDate=datetime.datetime.now().date()

        now=datetime.datetime.now()
        midnight=datetime.datetime.combine(now.date(),datetime.time())
        minutes=((now-midnight).seconds)/60 #minutes after midnight, use datead$

        cur=con.cursor()
        cur.execute("INSERT INTO temperaturesm (temperature,temperaturedh, humidity,temperaturebmp,pressure,rainfall, dateMeasured, hourMeasured) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(temperature,temperaturedh,humidity,temperaturebmp,pressure,rainfall,currentDate, minutes))
        con.commit()
        #print "Saved temperature"
        return "true"






def read_temp_raw():
        catdata = subprocess.Popen(['cat',device_file],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = catdata.communicate()
        out_decode = out.decode('utf-8')
        lines = out_decode.split('\n')
        return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
#        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c#, temp_f



#check if table is created or if we need to create one
try:
        queryFile=file("createTable2.sql","r")

        con=mariadb.connect(host="localhost", user=databaseUsername,password=databasePassword,database=databaseName)
        currentDate=datetime.datetime.now().date()

        line=queryFile.readline()
        query=""
        while(line!=""):
                query+=line
                line=queryFile.readline()

        cur=con.cursor()
        cur.execute(query)

        #now rename the file, because we do not need to recreate the table everytime this script is run
        queryFile.close()
        os.rename("createTable2.sql","createTable2.sql.bkp")


except IOError:
        pass #table has already been created



#saveToDatabase(read_temp())



#### BLOC RAINFALL ##############################################################################################

# this many mm per bucket tip
CALIBRATION = 0.2794
# which GPIO pin the gauge is connected to
PIN = 6
# file to log rainfall data in
GPIO.setmode(GPIO.BCM)  
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# variable to keep track of how much rain
rain = 0

# the call back function for each bucket tip
def cb(channel):
	global rain
	rain = rain + CALIBRATION

# register the call back for pin interrupts
GPIO.add_event_detect(PIN, GPIO.FALLING, callback=cb, bouncetime=300)

# display and log results
while True:

	currentDate=datetime.datetime.now().date()

        now=datetime.datetime.now()
        midnight=datetime.datetime.combine(now.date(),datetime.time())
        minutes=((now-midnight).seconds)/60 #minutes after midnight, use datead$


	humiditydh, temperaturedh = Adafruit_DHT.read_retry(sensor, pindh)
	temperaturebmp,pressurebmp = read_bmp280()
	temperatureds = read_temp()

	saveToDatabase(read_temp(),temperaturedh,humiditydh,temperaturebmp,pressurebmp,rain)




	#line = "%i,%f" % (minutes, rain)
	#print(line)
	#file.write(line + "\n")
	#file.flush()
	rain = 0
	time.sleep(300)
# close the log file and exit nicely

GPIO.cleanup()
