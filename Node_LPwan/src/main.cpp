#include <Arduino.h>
#include "HardwareSerial.h"
#include "bg95.h"
#include <time.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#include <Wire.h>

//broker va cac topic 
#define BROKER                        "broker.hivemq.com"
#define SUB_TOPIC_SEVER_SEND          "NbIoT/Farm/Pump"
#define SEND_TOPIC_TEMPERATURE        "NbIoT/Farm/Temp"
#define SEND_TOPIC_HUMIDITY           "NbIoT/Farm/Humi"
#define SEND_TOPIC_REPORT             "NbIoT/Farm/Pump"    
#define RELAY                         23

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME680 bme; // I2C



Bg95 nbiot;
int mode = 0;
float temperature, humidity;

//TODO: viet phan xu ly tin hieu nhan ve o day
void receiveData(void *arg){
  while(1){
    String data;
    nbiot.readMqtt(data);
    if (data.indexOf("QMTRECV:")){
      for (int i = 0; i < 3; i++){
        data = data.substring(data.indexOf(",")+1);
      }
      Serial.println(data);
      if (data.indexOf("0") >= 0) {
        mode = 0;
      }else if(data.indexOf("1") >= 0){
        mode = 1;
      }
    }
    
    else if (data.indexOf ("QMTSTAT: 1,1")){
      nbiot.reconnectMqtt();
    }


  vTaskDelay (1000/portTICK_PERIOD_MS);
  }
}

//TODO: viet phan xu ly tin hieu gui di o day
void sendData (void *arg){
  while(1){
    String data = String (temperature);
    nbiot.sendMqtt (SEND_TOPIC_TEMPERATURE, data, 1);
    delay(3000);
    data = String (humidity);
    nbiot.sendMqtt (SEND_TOPIC_HUMIDITY, data ,1);
    delay (3000);
    vTaskDelay (3000/portTICK_PERIOD_MS);
  }
}

// doc tin hieu tu cam bien
void readSensorData(void *arg){
  while(1){
    if (! bme.performReading()) {
      Serial.println("Failed to perform reading :(");
    }
    temperature = bme.temperature;
    humidity = bme.humidity;
    delay(1000);
    vTaskDelay(1000/portTICK_PERIOD_MS);
  }
}

void control(void *arg){
  while(1){
    if (mode == 1){
      digitalWrite(RELAY, LOW);
      Serial.println("relay on");
    }
    else if (mode == 0){
      digitalWrite(RELAY, HIGH);
      Serial.println("relay off");
    }
    delay (1000);
    vTaskDelay(1000/portTICK_PERIOD_MS);
  }
} 


void setup() {
// tao ket noi mqtt
  pinMode(RELAY, OUTPUT);
  nbiot.begin();
  nbiot.connectMqtt(BROKER, "localhost","");
  nbiot.subscribeMqtt(SUB_TOPIC_SEVER_SEND,2);

//ket noi cam bien 
  if (!bme.begin()) {
    Serial.println("Could not find a valid BME680 sensor, check wiring!");
    while (1);
  }

  // Set up oversampling and filter initialization
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); // 320*C for 150 ms

    // tao cac task
  xTaskCreate(
    receiveData,
    "receiveData",
    2048,
    NULL,
    1,
    NULL
  );

  xTaskCreate(
    sendData,
    "sendData",
    2048,
    NULL,
    2,
    NULL
  );

  xTaskCreate(
    readSensorData,
    "readSensorData",
    2048,
    NULL,
    3,
    NULL
  );

  xTaskCreate(
    control,
    "control",
    1024,
    NULL,
    3,
    NULL
  );

}

void loop(){

}
