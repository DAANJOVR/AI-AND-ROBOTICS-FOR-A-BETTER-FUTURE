#define BLYNK_TEMPLATE_ID "TMPL3wFjDZaaG"
#define BLYNK_TEMPLATE_NAME "Laser Alarm"
#define BLYNK_AUTH_TOKEN "6gugtt5Jl_mH4XBlJ05rhu_ehvsrPoah"

#include <WiFi.h>
#include <BlynkSimpleEsp32.h>

// WiFi
char ssid[] = "KANN_NETWORK";
char pass[] = "sjkmmt123";

// Pins
const int ldrPin    = 4;   // digital DO from LDR module (change if using analog)
const int buzzer    = 15;
const int redLED    = 18;
const int greenLED  = 19;

// Event name in Blynk Console (must match EXACTLY)
const char* BLYNK_EVENT_NAME = "intruder_alert";

bool alertSent = false;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 150; // ms

void setup() {
  Serial.begin(115200);
  delay(100);

  pinMode(ldrPin, INPUT_PULLUP); // use PULLUP to avoid floating; module DO may already handle this
  pinMode(buzzer, OUTPUT);
  pinMode(redLED, OUTPUT);
  pinMode(greenLED, OUTPUT);

  digitalWrite(buzzer, LOW);
  digitalWrite(redLED, LOW);
  digitalWrite(greenLED, HIGH);

  Serial.println();
  Serial.println("Starting up...");

  // Use template-based begin to ensure correct template/device pairing
  // Signature: Blynk.begin(auth, ssid, pass, template_id, device_name)
  Serial.println("Connecting to WiFi and Blynk Cloud...");
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);

  // Wait a moment and print status
  delay(1000);
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi OK, IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi NOT connected!");
  }

  Serial.println("Device setup complete. Check Blynk Console -> Device should show ONLINE.");
}

void loop() {
  Blynk.run(); // must call regularly

  int raw = digitalRead(ldrPin); // read the LDR module DO pin
  // print debug occasionally
  static unsigned long lastPrint = 0;
  if (millis() - lastPrint > 2000) {
    Serial.print("LDR raw: ");
    Serial.println(raw);
    lastPrint = millis();
  }

  // Debounce the sensor so short glitches don't spam notifications
  if (millis() - lastDebounceTime < debounceDelay) {
    // still debouncing
  } else {
    // Adjust logic depending on your module:
    // many LDR modules give LOW when beam is present and HIGH when broken.
    // Invert these if your module behaves opposite.
    bool laserBroken = (raw == HIGH); // <-- set to HIGH if your module outputs HIGH when beam is blocked
    // If your module gives LOW when blocked, change to: bool laserBroken = (raw == LOW);

    if (!laserBroken) {
      // Laser OK
      digitalWrite(greenLED, HIGH);
      digitalWrite(redLED, LOW);
      digitalWrite(buzzer, LOW);
      alertSent = false;
    } else {
      // Laser broken
      digitalWrite(greenLED, LOW);
      digitalWrite(redLED, HIGH);

      // local alarm beep
      for (int i = 0; i < 3; ++i) {
        digitalWrite(buzzer, HIGH);
        delay(120);
        digitalWrite(buzzer, LOW);
        delay(120);
      }

      // Send Blynk Event once
      if (!alertSent) {
        Serial.print("Triggering Blynk event: ");
        Serial.println(BLYNK_EVENT_NAME);
        // IMPORTANT: event name must match EXACTLY the 'event code' in Blynk Template Events
        Blynk.logEvent(BLYNK_EVENT_NAME, "🚨 Intruder detected! Laser beam broken.");
        alertSent = true;
      }
    }

    lastDebounceTime = millis();
  }

  delay(50); // short loop delay
}
