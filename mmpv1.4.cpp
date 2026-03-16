#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#include "SH1106Wire.h"

// --- internal frame buffer access pointer  ---
class SH1106Hack : public SH1106Wire {
  public:
    SH1106Hack(uint8_t address, int sda, int scl) : SH1106Wire(address, sda, scl) {}
    uint8_t* getBufferPtr() { return this->buffer; }
};

const int chipSelect = D8; 
SH1106Hack display(0x3c, SDA, SCL);

const int frameSize = 1024;
uint8_t videoBuffer[1024];
File videoFile;

// --- TIMING VARIABLES ---
uint8_t targetFPS = 30; // Default, will be read from file
unsigned long frameDurationMicros; // Duration of one frame (microseconds)
unsigned long frameStartTime;      // The moment frame processing starts

void setup() {
  Serial.begin(115200);
  
  display.init();
  display.flipScreenVertically();
  display.setContrast(255);
  Wire.setClock(800000); // I2C clock speed

  if (!SD.begin(chipSelect)) {    //sd card/module test
    Serial.println("SD Error!");
    display.drawString(0,0,"SD Error");
    display.display();
    while(1);
  }

  videoFile = SD.open("video.bin");   //looking for the video file in the sd card with the name "video.bin"
  if (!videoFile) {
    Serial.println("File not found!");
    while(1);
  }

  // --- FPS READING SECTION ---
  if (videoFile.available()) {
    targetFPS = videoFile.read(); // Read the first byte (FPS value)
    Serial.print("FPS Read From File: ");
    Serial.println(targetFPS);
    
    // If FPS is invalid (0 or too high), fall back to default
    if (targetFPS == 0 || targetFPS > 100) targetFPS = 30;
    
    // 1 second (1,000,000 microseconds) / FPS = duration of 1 frame
    frameDurationMicros = 1000000 / targetFPS;
  }
}

void loop() {
  // 1. Start the timer
  frameStartTime = micros();

  // If video has ended, rewind (skipping the header)
  if (!videoFile.available()) {
    videoFile.seek(1); // Byte 0 is FPS, so we seek to byte 1
  }

  // 2. Read and Draw
  videoFile.read(videoBuffer, frameSize);
  
  uint8_t* internalBuffer = display.getBufferPtr();
  memcpy(internalBuffer, videoBuffer, frameSize);
  
  display.display();

  // 3. TIMING CONTROL (Frame Pacing)
  unsigned long processTime = micros() - frameStartTime; // How long did processing take?
  
  // If processing finished faster than the target duration, wait
  if (processTime < frameDurationMicros) {
    unsigned long waitTime = frameDurationMicros - processTime;
    delayMicroseconds(waitTime);
  }
  // If processing took too long (hardware was too slow), skip the wait and move to the next frame immediately.
}
