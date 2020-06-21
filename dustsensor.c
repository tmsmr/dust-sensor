/*
- measures dust particle concentration using a PPD42 sensor
- tested on a raspberry pi 2
*/

// needs http://abyz.me.uk/rpi/pigpio/index.html
// compile with: gcc -Wall -pthread -o dustsensor dustsensor.c -lpigpio -lrt -lm
// run with: sudo ./dustsensor

#include <stdio.h>
#include <pigpio.h>
#include <math.h>

#define DUST_PIN 4
#define SAMPLETIME_MS 30000.0

uint32_t lowOccupancy = 0; //in ms
uint32_t fallingStart = 0; //in us

void edge_detected(int gpio, int level, uint32_t tick) {
  if(0 == level)
    fallingStart = tick;
  if(1 == level && fallingStart != 0)
    lowOccupancy += (tick - fallingStart) / 1000; //reduce resolution to ms
}

int main() {
  if(gpioInitialise() < 0) return 1; // init pigpio lib
  if(gpioSetMode(DUST_PIN, PI_INPUT) < 0) return 1; // configure DUST_PIN as input
  if(gpioSetAlertFunc(DUST_PIN, edge_detected) < 0) return 1; // configure interrupt routine for DUST_PIN
  if(gpioDelay(SAMPLETIME_MS * 1000) < 0) return 1; // wait SAMPLETIME_MS (gpioDelay wants us)
  gpioTerminate(); // try to terminate pigpio lib

  float ratio = (lowOccupancy / SAMPLETIME_MS) * 100; // calculate low occupancy in percent

  /*
  calculate particle concentration
  -> amount of particles per 283ml | particle size > 1um
  eqation for calculation from http://www.howmuchsnow.com/arduino/airquality/grovedust/
  */
  float concentration = 1.1 * pow(ratio, 3) - 3.8 * pow(ratio, 2) + 520 * ratio + 0.62;

  printf("%d %f %f", lowOccupancy, ratio, concentration);

  return 0;
}
