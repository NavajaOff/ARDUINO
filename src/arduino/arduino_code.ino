// Código Arduino para sistema de peaje con sensor ultrasónico HC-SR04
#include <Servo.h>

// Definición de pines
const int trigPin = 11;  // Pin TRIG del sensor HC-SR04
const int echoPin = 12;  // Pin ECHO del sensor HC-SR04
const int servoPin = 13; // Pin para el servomotor

// Modificar las constantes
const unsigned long TIEMPO_MINIMO_ENTRE_DETECCIONES = 5000;  // 5 segundos mínimo entre detecciones
const unsigned long TIEMPO_ESPERA_BARRERA = 1000;   // 1 segundo para que pase el vehículo
const int DISTANCIA_DETECCION = 25;                // Distancia en cm para detectar vehículo
const int LECTURAS_CONFIRMACION = 3;               // Número de lecturas consecutivas para confirmar

// Variables
Servo servo;
long duration;
int distance;
unsigned long tiempoDeteccion = 0;
bool vehiculoDetectado = false;

// Variables adicionales
int lecturas_consecutivas = 0;
int lecturas_salida = 0;
unsigned long ultima_deteccion = 0;
bool procesando_vehiculo = false;

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
  distance = duration * 0.034 / 2;
  
  unsigned long tiempo_actual = millis();
  
  // Mostrar distancia en monitor serial
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // Si hay un vehículo en proceso
  if (procesando_vehiculo) {
    if (distance > DISTANCIA_DETECCION) {
      procesando_vehiculo = false;
      vehiculoDetectado = false;
      servo.write(90);  // Cerrar barrera inmediatamente
      Serial.println("VEHICULO_SALIO");
      lecturas_salida = 0;
      lecturas_consecutivas = 0;
    }
    delay(50);
    return;
  }

  // Detección de nuevo vehículo
  if (distance <= DISTANCIA_DETECCION && !procesando_vehiculo) {
    lecturas_consecutivas++;
    if (lecturas_consecutivas >= LECTURAS_CONFIRMACION &&
        (tiempo_actual - ultima_deteccion) >= TIEMPO_MINIMO_ENTRE_DETECCIONES) {
        
        procesando_vehiculo = true;
        vehiculoDetectado = true;
        ultima_deteccion = tiempo_actual;
        
        servo.write(180);  // Abrir barrera
        Serial.println("VEHICULO_DETECTADO");
    }
  } else {
    lecturas_consecutivas = 0;
  }

  delay(50);
}