#include <DHT.h>

// ----------- USER SETTINGS -------------
#define MQ_PIN A0          // MQ sensor analog output
#define DHTPIN 2           // DHT11 signal pin
#define DHTTYPE DHT11

#define RELAY1 7           // Relay Channel 1 → AQI
#define RELAY2 8           // Relay Channel 2 → Temperature

int TEMP_THRESHOLD = 30;   // °C
int MQ_THRESHOLD   = 30;   // Adjust based on your sensor readings
// ---------------------------------------

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();

  pinMode(RELAY1, OUTPUT);
  pinMode(RELAY2, OUTPUT);

  // Relay modules are often ACTIVE LOW
  digitalWrite(RELAY1, HIGH);
  digitalWrite(RELAY2, HIGH);

  pinMode(MQ_PIN, INPUT);
}

void loop() {
  // --------- Read Temperature ----------
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  // Handle DHT11 errors
  if (isnan(temp) || isnan(hum)) {
    Serial.println("DHT11 reading error!");
    delay(1000);
    return;
  }

  // --------- Read MQ Sensor ------------
  int mqValue = analogRead(MQ_PIN);

  // --------- Print values --------------
  Serial.print("Temp: ");
  Serial.print(temp);
  Serial.print("  Humidity: ");
  Serial.print(hum);
  Serial.print("  MQ: ");
  Serial.println(mqValue);

  // --------- Relay Logic ---------------
  // Relay 1 → AQI
  if (mqValue > MQ_THRESHOLD) {
    digitalWrite(RELAY1, LOW);   // Turn ON
  } else {
    digitalWrite(RELAY1, HIGH);  // Turn OFF
  }

  // Relay 2 → Temperature
  if (temp > TEMP_THRESHOLD) {
    digitalWrite(RELAY2, LOW);   // Turn ON
  } else {
    digitalWrite(RELAY2, HIGH);  // Turn OFF
  }

  delay(1000);
}
