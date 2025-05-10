// Código Arduino para sistema de peaje con sensor ultrasónico HC-SR04
#include <Servo.h>

// Definición de pines
const int trigPin = 11;  // Pin TRIG del sensor HC-SR04
const int echoPin = 12;  // Pin ECHO del sensor HC-SR04
const int servoPin = 13; // Pin para el servomotor

// Variables
Servo servo;
long duration;
int distance;
unsigned long tiempoDeteccion = 0;
bool vehiculoDetectado = false;
const int DISTANCIA_DETECCION = 25; // Distancia en cm para detectar vehículo

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  servo.attach(servoPin);
  servo.write(90);  // Barrera cerrada al inicio (90 grados)
  
  Serial.println("Sistema de peaje inicializado");
  delay(1000);
}

void loop() {
  // Medir distancia con el sensor ultrasónico
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2; // Cálculo de distancia en cm
  
  // Mostrar distancia en monitor serial
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");
  
  // Detectar vehículo cuando la distancia es menor al umbral
  if (distance <= DISTANCIA_DETECCION && !vehiculoDetectado) {
    // Registrar tiempo de detección
    tiempoDeteccion = millis();
    
    // Abrir barrera
    servo.write(180);  // Abrir a 180 grados
    
    // Enviar datos por serial (para ser recogidos por el script Python)
    Serial.print("VEHICULO_DETECTADO,");
    Serial.println(tiempoDeteccion);
    
    vehiculoDetectado = true;
    delay(500);  // Pequeña pausa para estabilidad
  }
  
  // Si ya no se detecta un vehículo y la barrera está abierta
  if (distance > DISTANCIA_DETECCION && vehiculoDetectado) {
    // Dejamos la barrera abierta por un tiempo para que pase el vehículo
    delay(3000);
    servo.write(90);  // Cerrar barrera (90 grados)
    
    // Notificar que el vehículo pasó
    Serial.println("VEHICULO_PASO");
    
    vehiculoDetectado = false;
    delay(500);  // Pequeña pausa para estabilidad
  }
  
  delay(100); // Pequeña pausa entre lecturas
}