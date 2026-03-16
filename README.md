# Mini-Macintosh

This repository includes the code, step and stl files used in the project. To explain briefly, Mini Macintosh project lets you play any video you want on a miniature diy Macintosh lookalike small device. The device when fully built contains an oled display  module, a sd card module and a microcontroller.

I built this version of the device to work on a WEMOS D1 ESP8266 board and used the following components:

  mini sd card module,
  1.3" 128x64 OLED display (ssh1106),
  WEMOS D1 Mini.

For the first version that's all you need. In future versions I'm planning on adding multimedia buttons, a web server control panel and maybe even a built in battery.

So how do you use it ? I'll explain step by step. 

1) Download the video you want to play on the player in .mp4 format and name it "input.mp4".
2) Copy the code or install the .py file inside the same folder as the "input.mp4".
3) Run the code and copy the "video.bin" into the sd card module.
4) Insert the sd card into the module.
5) Upload the mmpvx.cpp/mmpvx.ino to the WEMOS D1 Mini.
6) Solder the connections.
7) Print the parts and place the components in the model.
8) Plug in the power and watch your favorite video play on the cute little player you made!

   ----CONNECTIONS AND SOME IMPORTANT STUFF ABOUT THE CONVERTER-----

-Depending on the video you want to convert you'll be asked if the input video is monochrome or colorful. For badd apple like videos choose monochrome.

-CONNECTIONS:
  WEMOS        OLED         SD CARD MODULE
  D1           SCL              ---
  D2           SDA              ---
  D5           ---              SCK
  D6           ---              MISO
  D7           ---              MOSI
  D8           ---              CS
  GND          GND              GND
  5V           VCC              VCC          
  (if ur using a dedicated battery you'll have to use the 3V3 pin but please consider that some     components doesn't work in that voltage range)

For people who want to know more about how does the code work, I explained briefly.


