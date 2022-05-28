import paho.mqtt.client as mqtt
import time
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import subprocess

broker_address = "192.168.1.79"  # Broker address
port = 1883  # Broker port
# user = "yourUser"                    #Connection username
# password = "yourPassword"            #Connection password

Temp = ""
Humi = ""

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
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("NbIoT/Farm/+", 2)
def on_message(client, userdata, message):
    print("Message received: " + message.topic + " : " + str(message.payload,'utf-8'))
    cmd = "date +%x | cut -d\' \' -f1"
    Date = subprocess.check_output(cmd, shell = True )
    cmd = "date +%X | cut -d\' \' -f1"
    Time = subprocess.check_output(cmd, shell = True )
    with open('/home/pi/mqtt_update.txt', 'a+') as f:
        f.write(str(Date,'utf-8')[:8]+"_"+str(Time,'utf-8')[:8]+"_")
    if message.topic == 'NbIoT/Farm/Temp':
        with open('/home/pi/mqtt_update.txt', 'a+') as f:
            f.write("T:"+str(message.payload,'utf-8')+"\n")
    if message.topic == 'NbIoT/Farm/Humi':
        with open('/home/pi/mqtt_update.txt', 'a+') as f:
            f.write("H:"+str(message.payload,'utf-8')+"\n")
    
    #     
    # if message.topic == 'NbIoT/Farm/Humi':
    #     Humi = str(message.payload)
    #     with open('/home/pi/mqtt_update.txt', 'a+') as f:
    #         f.write("received Farm/Humi"+str(message.payload)+"\n")
    



client = mqtt.Client()  # create new instance
# client.username_pw_set(user, password=password)    #set username and password
client.on_connect = on_connect  # attach function to callback
client.on_message = on_message  # attach function to callback
client.connect(broker_address, port=port)  # connect to broker

while True:
    
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell = True )
    cmd = "date +%x | cut -d\' \' -f1"
    Date = subprocess.check_output(cmd, shell = True )
    cmd = "date +%X | cut -d\' \' -f1"
    Hour = subprocess.check_output(cmd, shell = True )
    draw.text((0, 0), "IP: " + str(IP,'utf-8'), font=font, fill=255)
    draw.text((0, 16), "LT: " + str(Hour,'utf-8'), font=font, fill=255)
    draw.text((73, 16), " " + str(Date,'utf-8'), font=font, fill=255)
    # print("ok")
    client.loop_start()
    client.loop_stop()
    cmd = " tail -1 mqtt_update.txt | cut -d\' \' -f1"
    ToH = subprocess.check_output(cmd, shell = True )
    ToH = str(ToH,'utf-8')
    # print("/"+ToH[18:19]+"/")
    if ToH[18:19] == "T":
        Temp = ToH[20:22]
    else:
        Humi = ToH[20:22]
    draw.text((0, 32), "Temperature: " + Temp +"'C", font=font, fill=255)
    draw.text((0, 48), "Humidity: "+ Humi +" %", font=font, fill=255)
    oled.image(image)
    oled.show()
    #print("ok2")
    
# draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
# draw.text((25, 0), "Temp: " + Temp +"'C", font=font, fill=255)
# draw.text((25, 16), "Humi: "+ Humi +" %", font=font, fill=255) 
# oled.image(image)
# oled.show()
# time.sleep(.1)
# client.loop_stop()
# client.loop_forever()