#include <PulseSensorPlayground.h>
#include <LiquidCrystal_I2C.h>

//-------------------- Pins and Thresholds
const int PulseWire = A0;      // Pulse sensor
const int LED_3 = D3;          // LED for pulse blink
const int BUZZER_PIN = D6;     // Active buzzer
int Threshold = 260;            // Sensor threshold
int DangerousBPM = 120;         // Dangerous BPM

//-------------------- Objects
PulseSensorPlayground pulseSensor;
LiquidCrystal_I2C lcd(0x27, 16, 2); // Your working LCD

//-------------------- Setup
void setup() {
  Serial.begin(115200);

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  // PulseSensor config
  pulseSensor.analogInput(PulseWire);
  pulseSensor.blinkOnPulse(LED_3);
  pulseSensor.setThreshold(Threshold);
  pulseSensor.begin();

  // LCD setup
  lcd.init();
  lcd.clear();
  lcd.backlight();
  lcd.setCursor(2,0);
  lcd.print("Pulse Monitor");
  lcd.setCursor(2,1);
  lcd.print("Initializing...");
  delay(2000);
  lcd.clear();
}

//-------------------- Loop
void loop() {
  int myBPM = pulseSensor.getBeatsPerMinute(); 

  if (pulseSensor.sawStartOfBeat()) {
    Serial.print("BPM: ");
    Serial.println(myBPM);

    // Display BPM
    lcd.setCursor(0,0);
    lcd.print("BPM: ");
    lcd.print(myBPM);
    lcd.print("    "); // Clear leftovers

    // Check dangerous BPM
    if(myBPM > DangerousBPM){
      alertBuzzer();
      startBreathingExercise();
    }
  }

  delay(20);
}

//-------------------- Buzzer Alert
void alertBuzzer(){
  // 3 short beeps
  for(int i=0;i<3;i++){
    tone(BUZZER_PIN, 1000); // 1kHz tone
    delay(200);
    noTone(BUZZER_PIN);
    delay(200);
  }
}

//-------------------- Breathing Exercise with Soft Buzzer
void startBreathingExercise(){
  // Inhale (2s)
  lcd.clear();
  lcd.setCursor(2,0);
  lcd.print("Breathe In...");
  tone(BUZZER_PIN, 400); // soft low tone
  delay(2000);
  noTone(BUZZER_PIN);

  // Hold (1s)
  lcd.clear();
  lcd.setCursor(4,0);
  lcd.print("Hold...");
  tone(BUZZER_PIN, 500); // gentle tone
  delay(1000);
  noTone(BUZZER_PIN);

  // Exhale (2s)
  lcd.clear();
  lcd.setCursor(2,0);
  lcd.print("Breathe Out");
  tone(BUZZER_PIN, 350); // soft calming tone
  delay(2000);
  noTone(BUZZER_PIN);

  // Back to BPM display
  lcd.clear();
  lcd.setCursor(2,0);
  lcd.print("Back to BPM");
  delay(1000);
}
