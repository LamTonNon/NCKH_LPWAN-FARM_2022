#include <Arduino.h>
#include "HardwareSerial.h"
#include "bg95.h"
#include <time.h>

#define BROKER              "42.115.161.106"
#define SUB_TOPIC1          "NbIoT/Farm/+"
#define SEND_TOPIC1         "NbIoT/Farm/Temp"
#define SEND_TOPIC2         "NbIoT/Farm/Humi"


Bg95 nbiot;

// ls ghi phan xu ly tin hieu nhan ve vao day
void Bg95::checkRecieved(String &received, void *args){
	if (received.indexOf("+QMTSTAT: 1,1") >= 0){
		reset();
		return;
	}
	if (received.indexOf("+QMTRECV:") >= 0){
		//TODO: co the chen them phan xu ly hoac chuyen mode o day tuy thuoc vao quy tac dat giu lieu
		return;
	}
}

void setup() {
  // put your setup code here, to run once:
  // DEBUG.begin(9600);
  // BG95.begin(115200,SERIAL_8N1,16,17);
  // BG95.println("AT");
  // DEBUG.println(BG95.readString());
  // BG95.println("AT+QMTOPEN=1,\"broker.hivemq.com\",1883");
  // DEBUG.println(BG95.readString());
  while(!nbiot.begin());
  nbiot.connectMqtt(BROKER, "localhost","");
  nbiot.subscribeMqtt(SUB_TOPIC1,2);
}

void loop() {
  // put your main code here, to run repeatedly:

}

