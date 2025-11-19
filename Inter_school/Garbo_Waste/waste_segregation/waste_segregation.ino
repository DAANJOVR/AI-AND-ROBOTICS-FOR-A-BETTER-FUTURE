#include <Servo.h>

Servo wasteServo;

const int moisturePin = 3; // Digital moisture sensor
const int irPin = 2;       // IR sensor
const int servoPin = 9;    // Servo
const int buzzerPin = 4;   // Buzzer pin

// Servo angles (adjust physically)
const int restAngle = 90;
const int dryAngle = 20;
const int wetAngle = 160;

// Time to wait for moisture sensor stabilization (ms)
const int stabilizationTime = 300;

void setup() {
  Serial.begin(9600);
  wasteServo.attach(servoPin);
  wasteServo.write(restAngle);

  pinMode(moisturePin, INPUT);
  pinMode(irPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
}

void loop() {
  int irState = digitalRead(irPin);

  if(irState == LOW) { // Object detected
    Serial.println("Object detected! Waiting 5 seconds...");
    
    delay(3000);  // <<< ----- NEW 5 SECOND DELAY HERE

    Serial.println("Waiting for moisture sensor...");

    // Wait for moisture sensor to stabilize
    int moistureState;
    unsigned long startTime = millis();
    int stableValue = digitalRead(moisturePin);

    while(millis() - startTime < stabilizationTime) {
      moistureState = digitalRead(moisturePin);
      if(moistureState != stableValue) {
        stableValue = moistureState;  // Reset timer if fluctuates
        startTime = millis();
      }
    }

    moistureState = stableValue;
    Serial.print("Moisture Digital State: ");
    Serial.println(moistureState);

    // Move servo and sound buzzer
    if(moistureState == HIGH) { // Dry waste
      Serial.println("Dry Waste Detected");
      wasteServo.write(dryAngle);
      digitalWrite(buzzerPin, HIGH);
      delay(100);
      digitalWrite(buzzerPin, LOW);
    }
    else { // LOW → Wet waste
      Serial.println("Wet Waste Detected");
      wasteServo.write(wetAngle);

      for(int i=0; i<2; i++){
        digitalWrite(buzzerPin, HIGH);
        delay(100);
        digitalWrite(buzzerPin, LOW);
        delay(100);
      }
    }

    delay(2000);                 // Allow waste to fall
    wasteServo.write(restAngle);  // Return to rest
    delay(500);

    // Wait until object is removed before next cycle
    while(digitalRead(irPin) == LOW) {
      delay(100);
    }
  }
  else {
    Serial.println("Waiting for object...");
    delay(500);
  }
}
