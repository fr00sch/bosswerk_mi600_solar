from asyncio import exceptions
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
import os
import re
import paho.mqtt.client as mqtt
import math
from datetime import datetime
import configparser

status_m = 10
status = {0: 'Online', 2: "DataError", 3: 'Offline', 4:"TimeoutError", 10:"undefined"}


def getIntegerOfID(wait ,htmlID):
  ret = float("NaN")
  try:
    value = wait.until(EC.presence_of_element_located((By.ID, htmlID))).text
    #print(value)
    value_array=re.findall("\d+",value)
    if len(value_array)>0:
      ret = float(value_array[0])
    else:
      print(value)
      status_m = 2
  except TimeoutException as e:
    #print(e)
    status_m = 4
  return ret

def getFloatOfID(wait ,htmlID):
  ret = float("NaN")
  try:
    value = wait.until(EC.presence_of_element_located((By.ID, htmlID))).text
    #print(value)
    value_array=re.findall("\d+\.\d+",value)
    if len(value_array)>0:
      ret = float(value_array[0])
    else:
      print(value)
      status_m = 2
  except TimeoutException as e:
    #print(e)
    status_m = 4
  return ret


def getDataFromBosswerk(url, sn):
 ret0 = float("NaN")
 ret1 = float("NaN")
 ret2 = float("NaN")
 with Display(visible=0, size=(1280, 1024)) as display:
  s=Service('/usr/local/bin/geckodriver')
  with webdriver.Firefox(service=s) as browser:
    try:
      browser.get(url)
      wait = WebDriverWait(browser, 10) 
      try:
        frame1 = wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME,'child_page')))
        sn = wait.until(EC.text_to_be_present_in_element((By.ID,"webdata_sn"), sn))
        ret0 = getIntegerOfID(wait, "webdata_now_p")
        ret1 = getFloatOfID(wait, "webdata_today_e")
        ret2 = getFloatOfID(wait, "webdata_total_e")
        if math.isnan(ret0) or math.isnan(ret1) or math.isnan(ret2):
         status_m=2
        else:
         status_m=0
      except TimeoutException as e:
        #print(e)
        status_m = 4
      finally:
        browser.quit()
    except WebDriverException as e:
      #print(e)
      status_m = 3
 return ret0, ret1, ret2, status_m

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+":"+str(msg.payload))

def connectMQTT(ip, port, username, password):
 #https://pypi.org/project/paho-mqtt/
 client = mqtt.Client()
 client.username_pw_set(username, password)
 client.on_connect = on_connect
 client.on_message = on_message
 #with mqtt.Client(client_id="0", clean_session=True, userdata=None, protocol="MQTTv311", transport="tcp") as client:
 client.connect(ip , port, 60)
 return client

def sendData(client, in1, in2, in3, status_m):
 in1=float(in1)
 in2=float(in2)
 in3=float(in3)
 #client.will_set("bosswerk/status",payload="Offline", qos=0, retain=True)
 client.publish("bosswerk/status_m",payload=status_m,qos=0, retain=True) 
 client.publish("bosswerk/status",payload=status[status_m],qos=0, retain=True) 
 if status_m==0:
   client.publish("bosswerk/power",payload=in1,qos=0,retain=False)
   client.publish("bosswerk/today",payload=in2,qos=0,retain=True)
   client.publish("bosswerk/total",payload=in3,qos=0,retain=True)
   client.publish("bosswerk/lastDataUpdate",payload=datetime.today().strftime('%Y-%m-%d %H:%M:%S'),qos=0,retain=True)
 if status_m==3:
   client.publish("bosswerk/power",payload=0,qos=0,retain=False)
 client.disconnect()

if __name__=='__main__':
  config = configparser.ConfigParser()
  path = os.path.dirname(__file__)
  config.read(path+'/config.ini')
  url1 = config['BOSSWERK']['url']
  sn1 = config['BOSSWERK']['sn']
  mqtt_ip = config['MQTT']['ip']
  mqtt_port = int(config['MQTT']['port'])
  mqtt_username = config['MQTT']['username']
  mqtt_password = config['MQTT']['password']

  print(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
  getDataCount = 0
  while getDataCount<10:
    print("Try-Number: "+str(getDataCount))
    power, today, total, status_r = getDataFromBosswerk(url1,sn1)
    print("Power: "+str(power)+" W")
    print("Today: "+str(today)+" kWh")
    print("Total: "+str(total)+" kWh")
    if status_r <= 1:
      break
    else:
      getDataCount = getDataCount + 1
  client = connectMQTT(mqtt_ip, mqtt_port, mqtt_username, mqtt_password)
  sendData(client, power, today, total, status_r)
  print("Status: "+status[status_r])
