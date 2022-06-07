#include <Arduino.h>
#include "HardwareSerial.h"
#include "bg95.h"
#include <time.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#include <Wire.h>

#define BROKER                        "broker.hivemq.com"
#define SUB_TOPIC_SEVER_SEND          "bg95/test1"
#define SEND_TOPIC_TEMPERATURE        "bg95/test1"
#define SEND_TOPIC_HUMIDITY           "bg95/test1"
#define SEND_TOPIC_REPORT             "bg95/test1"    


#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME680 bme; // I2C



Bg95 nbiot;
int mode;
float temperature, humidity;


void receiveData(void *arg){
  while(1){
    String data;
    nbiot.readMqtt(data);
    if (data.indexOf("QMTRECV:")){
      if (data.indexOf("gg") >= 0) {
        data = "jj";
        nbiot.sendMqtt (SEND_TOPIC_REPORT, data, 2);
      }
    }else if (data.indexOf ("QMTSTAT: 1,1")){
      nbiot.connectMqtt (BROKER, "localhost", "");
    }
  vTaskDelay (1000/portTICK_PERIOD_MS);
  }
}

void sendData (void *arg){
  String data = String (temperature) + "C";
  nbiot.sendMqtt (SEND_TOPIC_TEMPERATURE, data, 2);
  data = String (humidity) + "%";
  nbiot.sendMqtt (SEND_TOPIC_HUMIDITY, data ,2);
  vTaskDelay (1000/portTICK_PERIOD_MS);
}

void readSensorData(void *arg){
  while(1){
    if (! bme.performReading()) {
      Serial.println("Failed to perform reading :(");
    }
    temperature = bme.temperature;
    humidity = bme.humidity;
    vTaskDelay(1000/portTICK_PERIOD_MS);
  }
}


void setup() {
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

  nbiot.begin();
  nbiot.connectMqtt(BROKER, "localhost","");
  nbiot.subscribeMqtt(SUB_TOPIC_SEVER_SEND,2);
  String data = "123";
  nbiot.sendMqtt(SEND_TOPIC_REPORT, data, 2);

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

}

void loop() {
  // put your main code here, to run repeatedly:
  


}

