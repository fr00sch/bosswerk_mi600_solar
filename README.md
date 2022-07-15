# Bosswerk to Mqtt Mi300/Mi600 solar micro inverter
To get data from the webpage of the solar micro inverter Bosswerk Mi600 or Mi300 and pushs them to an mqtt server.
The script gets the data for:
 - the acutal power
 - the produced energy of today
 - the produced energy over all
The webservice of the inverter is manly driven by javascript, so it needs selenium (with firefox and geckodriver) and a virtual display to extract the data.

Different errors are treated:
 - The inverter is "Offline" for exaample during night.
 - It can't find the data on the webside of the inverter
 - it takes to long to get the data of the system.

TODOs:
 - mqtt publish path in the config file
 - make a better installation description
 - better errorhandling with the mqtt server

<b>HowTo-Start:</b>

1.) Install all necessary packages to get you python system to run.

2.) Copy the 3 files to the folder "/opt/solar" and configure the "config.ini" file
 
2.1) The SerialNumber (SN) can be found on the main-Page and is needed to see, if the side is correctly loaded 

3.) add your script to the crontab: "crontab -e"

  "*  *   *   *   *     /opt/solar/solar.sh >> /opt/solar/logging.txt  2>&1"

Hint: Please notice, that different python modules are needed. Depends on missing modules use:

4.0) apt-get install python3-pip
4.1) pip install selenium
4.2) pip install pyvirtualdisplay
4.3) pip install paho-mqtt
