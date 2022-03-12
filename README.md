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

NiceToHave:
 - better errorhandling

<b>HowTo-Start:</b>

1.) Install all necessary packages to get you python system to run.

2.) Copy the 3 files to the folder "/opt/solar"

3.) add your script to the crontab: "crontab -e"

  "*  *   *   *   *     /opt/solar/solar.sh >> /opt/solar/logging.txt  2>&1"
