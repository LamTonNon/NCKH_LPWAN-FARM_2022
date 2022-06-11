import paho.mqtt.client as mqtt
import time
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import subprocess

Time_pump1 ='23:52'
Time_pump2 ='23:54'
Delay_pump = '1'

IP   = ""
Temp = "xx"
Humi = "xx"
Pump = 0

# Host config
IP = subprocess.check_output("hostname -I | cut -d\' \' -f1", shell = True ) #IP="192.168.1.79 "
broker_address = str(IP,'utf-8')[:-1]  # Broker address
port = 1883  # Broker port
# user = "yourUser"                    #Connection username
# password = "yourPassword"            #Connection password

class Pump_control_time:
	def __init__(self, time_start='hh:mm',how_long='mm'):
		self.hour = int(time_start[0:2])
		self.minu = int(time_start[3:5])
		if how_long != 'mm':
			self.delay = int(how_long[0:])
		else:
			self.delay = 0

timepump1 = Pump_control_time(time_start = Time_pump1, how_long = Delay_pump)
timepump2 = Pump_control_time(time_start = Time_pump2, how_long = Delay_pump)

# ssd_i2c config
# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)
# Display Parameters
WIDTH = 128
HEIGHT = 64
BORDER = 5
# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)
# Clear display.
oled.fill(0)
oled.show()
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (oled.width, oled.height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
# Draw a white background
draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)
font = ImageFont.truetype('PixelOperator.ttf', 16)
#font = ImageFont.load_default()

def on_connect(client, userdata, flags, rc):
    # print("Connected with result code " + str(rc)) #rc=0 connected 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("NbIoT/Farm/+", 2)
def on_message(client, userdata, message):
    # print("Message received: " + message.topic + " : " + str(message.payload,'utf-8')[:-1])
    cmd = "date +%x | cut -d\' \' -f1"
    Date = subprocess.check_output(cmd, shell = True )
    cmd = "date +%X | cut -d\' \' -f1"
    Time = subprocess.check_output(cmd, shell = True )
    with open('/home/pi/Gateway_LPwan/mqtt_update.txt', 'a+') as f:
        f.write(str(Date,'utf-8')[:8]+"_"+str(Time,'utf-8')[:8]+"_")
    if message.topic == 'NbIoT/Farm/Temp':
        with open('/home/pi/Gateway_LPwan/mqtt_update.txt', 'a+') as f:
            f.write("T:"+str(message.payload,'utf-8')[:-1]+"\n")
    if message.topic == 'NbIoT/Farm/Humi':
        with open('/home/pi/Gateway_LPwan/mqtt_update.txt', 'a+') as f:
            f.write("H:"+str(message.payload,'utf-8')[:-1]+"\n")
    if message.topic == 'NbIoT/Farm/Pump':
        with open('/home/pi/Gateway_LPwan/mqtt_update.txt', 'a+') as f:
            f.write("P:0"+str(message.payload,'utf-8')+"\n")
def on_publish(client, userdata, mid):
    # print("Message " + str(mid) + " published.")
    pass

client = mqtt.Client()  # create new instance
# client.username_pw_set(user, password=password)    #set username and password
client.on_connect = on_connect  # attach function to callback
client.on_message = on_message  # attach function to callback
client.on_publish = on_publish  # attach function to callback
client.connect(broker_address, port=port)  # connect to broker

while True:
    
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    
    cmd = "date +%x | cut -d\' \' -f1"
    Date = subprocess.check_output(cmd, shell = True )
    cmd = "date +%X | cut -d\' \' -f1"
    Hour = subprocess.check_output(cmd, shell = True )
    cmd = "date +%H | cut -d\' \' -f1"
    Time_ref = Pump_control_time(time_start = str(Hour,'utf-8')[:-4])
    draw.text((0, 0), "IP: " + str(IP,'utf-8'), font=font, fill=255)
    draw.text((0, 16), "Time: " + str(Hour,'utf-8')[:-4], font=font, fill=255)
    draw.text((73, 16), " " + str(Date,'utf-8'), font=font, fill=255)
    client.loop_start()
    client.loop_stop()
    cmd = " tail -1 /home/pi/Gateway_LPwan/mqtt_update.txt | cut -d\' \' -f1"
    ToH = subprocess.check_output(cmd, shell = True )
    ToH = str(ToH,'utf-8')
    # print("/"+ToH[18:19]+"/")
    if ToH[18:19] == "T":
        Temp = ToH[20:22]
    elif ToH[18:19] == "H":
        Humi = ToH[20:22]
    draw.text((0, 32), "Temp: " + Temp +"'C", font=font, fill=255)
    draw.text((68, 32), "Humi: "+ Humi +"%", font=font, fill=255)

    if (Time_ref.hour == timepump1.hour and Time_ref.minu == timepump1.minu) and Pump == 0:
        client.publish("NbIoT/Farm/Pump", "1", qos=2)
        Pump = 1
        print('ok')
    elif (Time_ref.hour == timepump1.hour and Time_ref.minu == timepump1.minu + timepump1.delay) and Pump == 1:
        client.publish("NbIoT/Farm/Pump", "0", qos=2)
        Pump = 0
    elif (Time_ref.hour == timepump2.hour and Time_ref.minu == timepump2.minu) and Pump == 0:
        client.publish("NbIoT/Farm/Pump", "1", qos=2)
        Pump = 1
    elif (Time_ref.hour == timepump2.hour and Time_ref.minu == timepump2.minu + timepump2.delay) and Pump == 1:
        client.publish("NbIoT/Farm/Pump", "0", qos=2)
        Pump = 0
    
    
    if Pump == 1:
        draw.text((0, 48), "Pump: "+ "On", font=font, fill=255)
    else:
        draw.text((0, 48), "Pump: "+ "Off", font=font, fill=255)
    oled.image(image)
    oled.show()