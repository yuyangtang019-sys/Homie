#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <BH1750.h>
#include <DHT.h>
#include <ESP32Servo.h>

// ==================== 传感器配置 ====================
#define DHTPIN 4
#define DHTTYPE DHT22
#define MOTOR_PIN 13
#define BUTTON_PIN 2

#define LIGHT_THRESHOLD 100
#define TEMP_THRESHOLD_HIGH 26
#define TEMP_THRESHOLD_LOW 23

// ==================== WiFi ====================
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASS";

// Homie 服务接口
const char* homie_server = "http://YOUR_SERVER_IP:8000/api/hardware/sensor";

// ==================== 初始化 ====================
DHT dht(DHTPIN, DHTTYPE);
BH1750 lightMeter;
Servo doorMotor;

bool doorState = false;

struct AIResult {
  bool ac_on;
  bool curtain_open;
  bool door_open;
  int ac_temp;
};

AIResult fallback_decision(float temp, int light, bool buttonPressed) {
  AIResult result;
  result.ac_on = (temp > TEMP_THRESHOLD_HIGH);
  result.curtain_open = (light < LIGHT_THRESHOLD);
  result.door_open = buttonPressed;
  result.ac_temp = temp > TEMP_THRESHOLD_HIGH ? 24 : 26;
  return result;
}

AIResult homie_decision(float temp, int light, float humidity, bool buttonPressed) {
  AIResult result;
  HTTPClient http;
  http.begin(homie_server);
  http.addHeader("Content-Type", "application/json");

  String json = "{";
  json += ""temp":" + String(temp, 2) + ",";
  json += ""light":" + String(light) + ",";
  json += ""humidity":" + String(humidity, 2) + ",";
  json += ""button_pressed":" + String(buttonPressed ? "true" : "false");
  json += "}";

  int httpCode = http.POST(json);

  if (httpCode == 200) {
    String payload = http.getString();
    result.ac_on = payload.indexOf(""ac_on":true") > 0;
    result.curtain_open = payload.indexOf(""curtain_open":true") > 0;
    result.door_open = payload.indexOf(""door_open":true") > 0;

    int tempIdx = payload.indexOf(""ac_temp":");
    if (tempIdx > 0) {
      String sub = payload.substring(tempIdx + 10);
      int commaIdx = sub.indexOf(",");
      int endIdx = commaIdx > 0 ? commaIdx : sub.indexOf("}");
      result.ac_temp = sub.substring(0, endIdx).toInt();
    } else {
      result.ac_temp = 24;
    }

    Serial.println("Homie 决策成功");
  } else {
    Serial.println("Homie 决策失败，使用本地兜底");
    result = fallback_decision(temp, light, buttonPressed);
  }

  http.end();
  return result;
}

// ==================== 控制函数 ====================
void turnOnAC(int temp) { 
  Serial.printf("AC ON, target=%d
", temp); 
}

void turnOffAC() { 
  Serial.println("AC OFF"); 
}

void openCurtains() { 
  Serial.println("Curtains OPEN"); 
}

void closeCurtains() { 
  Serial.println("Curtains CLOSE"); 
}

void openDoor() {
  doorMotor.write(90);
  doorState = true;
  Serial.println("Door OPEN");
}

void closeDoor() {
  doorMotor.write(0);
  doorState = false;
  Serial.println("Door CLOSE");
}

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting WiFi...");
  }
  Serial.println("WiFi Connected");

  Wire.begin();
  lightMeter.begin();
  dht.begin();
  doorMotor.attach(MOTOR_PIN);
}

// ==================== LOOP ====================
void loop() {
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  int light = (int)lightMeter.readLightLevel();
  bool buttonPressed = digitalRead(BUTTON_PIN) == LOW;

  Serial.printf("Temp: %.2f, Humidity: %.2f, Light: %d, Button: %d\n", temp, humidity, light, buttonPressed);

  AIResult decision = homie_decision(temp, light, humidity, buttonPressed);

  if (decision.ac_on) turnOnAC(decision.ac_temp);
  else turnOffAC();

  if (decision.curtain_open) openCurtains();
  else closeCurtains();

  if (decision.door_open && !doorState) openDoor();
  else if (!decision.door_open && doorState) closeDoor();

  delay(3000);
}
