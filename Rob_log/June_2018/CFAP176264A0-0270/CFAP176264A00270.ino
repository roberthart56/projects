//=============================================================================
// "Arduino" example program for Crystalfontz ePaper. 
//
// This project is for the CFAP17664A0-0270 :
//
//   https://www.crystalfontz.com/product/cfap176264A00270
//
// It was written against a Seeduino v4.2 @3.3v. An Arduino UNO modified to
// operate at 3.3v should also work.
//-----------------------------------------------------------------------------
// This is free and unencumbered software released into the public domain.
// 
// Anyone is free to copy, modify, publish, use, compile, sell, or
// distribute this software, either in source code form or as a compiled
// binary, for any purpose, commercial or non-commercial, and by any
// means.
// 
// In jurisdictions that recognize copyright laws, the author or authors
// of this software dedicate any and all copyright interest in the
// software to the public domain. We make this dedication for the benefit
// of the public at large and to the detriment of our heirs and
// successors. We intend this dedication to be an overt act of
// relinquishment in perpetuity of all present and future rights to this
// software under copyright law.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
// EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
// MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
// IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
// OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
// ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
// OTHER DEALINGS IN THE SOFTWARE.
// 
// For more information, please refer to <http://unlicense.org/>
//=============================================================================
// Connecting the Arduino to the display
//
//			|Adapter		|			|
//			|(pin 1 towards	|			|
// ARDUINO	|jumper headers)|Wire Color	|Function
// ---------+---------------+-----------+--------------------
// D2		|19				|Yellow		|BS1 Not Used
// D3		|17				|Green		|Busy Line
// D4		|18				|Brown		|Reset Line
// D5		|15				|Purple		|Data/Command Line
// D10		|16				|Blue		|Chip Select Line
// D11		|14				|White		|MOSI
// D13		|13				|Orange		|Clock
// 3.3V		|5				|Red		|Power
// GND		|3				|Black		|Ground
//
// Short the following pins on the adapter board:
// GND -> BS2
// 0.47 -> RESE
//=============================================================================
// Creating image data arrays
//
// Bmp_to_epaper is code that will aid in creating bitmaps necessary from .bmp files.
// The code can be downloaded from the Crystalfontz website: https://www.Crystalfontz.com
// or it can be downloaded from github: https://github.com/crystalfontz/bmp_to_epaper
//=============================================================================

// The display is SPI, include the library header.
#include <SPI.h>

// Include LUTs
#include "LUTs_for_CFAP176264A00270.h"

// Include the images. These images were prepared with "bmp_to_epaper" which
// is available on the Crystalfontz site.
#include "Images_for_CFAP176264A00270.h"

// This module is 176x264 pixels. Make sure that the image files make sense.
#if ((WIDTH_PIXELS != (176)) || (HEIGHT_PIXELS  != (264)))
#error "IMAGE INCLUDE FILE IS WRONG SIZE"
#endif

#define ePaper_RST_0  (digitalWrite(EPD_RESET, LOW))
#define ePaper_RST_1  (digitalWrite(EPD_RESET, HIGH))
#define ePaper_CS_0   (digitalWrite(EPD_CS, LOW))
#define ePaper_CS_1   (digitalWrite(EPD_CS, HIGH))
#define ePaper_DC_0   (digitalWrite(EPD_DC, LOW))
#define ePaper_DC_1   (digitalWrite(EPD_DC, HIGH))

#define EPD_READY   3
#define EPD_RESET   4
#define EPD_DC      5
#define EPD_CS      10

//=============================================================================
//this function will take in a byte and send it to the display with the 
//command bit low for command transmission
void writeCMD(uint8_t command)
{
	ePaper_DC_0;
	ePaper_CS_0;
	SPI.transfer(command);
	ePaper_CS_1;
}

//this function will take in a byte and send it to the display with the 
//command bit high for data transmission
void writeData(uint8_t data)
{
	ePaper_DC_1;
	ePaper_CS_0;
	SPI.transfer(data);
	ePaper_CS_1;
}

//===========================================================================
void setup(void)
{
	//delay(50);
	//Debug port / Arduino Serial Monitor (optional)
	Serial.begin(9600);

	// Configure the pin directions   
	pinMode(EPD_CS, OUTPUT);
	pinMode(EPD_RESET, OUTPUT);
	pinMode(EPD_DC, OUTPUT);
	pinMode(EPD_READY, INPUT);

	//Set up SPI interface
	SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE0));
	SPI.begin();


	//reset driver
	ePaper_RST_0;
	delay(200);
	ePaper_RST_1;
	delay(200);

	//-----------------------------------------------------------------------------
	//more detail on the following commands and additional commands not used here	
	//can be found on the CFAP176264A0-0270 datasheet on the Crystalfontz website	
	//-----------------------------------------------------------------------------

	//Power Setting
	writeCMD(0x01);
	writeData(0x03);
	writeData(0x00);
	writeData(0x2B);
	writeData(0x2B);
	writeData(0x09);

	//Power On
	writeCMD(0x04);
	//wait until powered on
	while (0 == digitalRead(EPD_READY));


	//Booster Soft Start
	writeCMD(0x06);
	writeData(0x07);
	writeData(0x07);
	writeData(0x17);
	
	//Power optimization
	writeCMD(0xF8);
	writeData(0x60);
	writeData(0xA5);

	writeCMD(0xF8);
	writeData(0x89);
	writeData(0xA5);

	writeCMD(0xF8);
	writeData(0x90);
	writeData(0x00);

	writeCMD(0xF8);
	writeData(0x93);
	writeData(0x2A);
	
	//Reset DFV_EN
	//this command resets the DFV_EN by sending a partial refresh command
	writeCMD(0x16);
	writeData(0x00);

	//PLL Control
	writeCMD(0x30);
	writeData(0x3A);

	
	//VCM DS Settings
	writeCMD(0x82);
	writeData(0x12);

	writeCMD(0x50);
	writeData(0x87);

	//set LUTs and panel setting
	//setRegisterLUT();
	setOTPLUT();

	//Resolution
	writeCMD(0x61);
	writeData(0x00);	//first half of 2 bytes:  0		
	writeData(0xB0);	//second half of 2 bytes: 176
	writeData(0x01);	//first half of 2 bytes:  256
	writeData(0x08);	//second half of 2 bytes: 8
						//	176	 x	264

	Serial.println("setup complete");
}

void setRegisterLUT()
{
	//set LUTs
	//The following block allows the LUTs to be changed.
	//In order for these LUTs to take effect, command 0x00 must have bit 5 set to "1"
	//set panel setting to call LUTs from the register
	writeCMD(0x00);
	writeData(0xEF); //11101111

	//VCOM_LUT_LUTC
	writeCMD(0x20);
	for (int i = 0; i < 44; i++)
	{
		writeData(pgm_read_byte(&VCOM_LUT_LUTC[i]));
	}
	//W2W_LUT_LUTWW
	writeCMD(0x21);
	for (int i = 0; i < 42; i++)
	{
		writeData(pgm_read_byte(&W2W_LUT_LUTWW[i]));
	}
	//B2W_LUT_LUTBW_LUTR
	writeCMD(0x22);
	for (int i = 0; i < 42; i++)
	{
		writeData(pgm_read_byte(&B2W_LUT_LUTBW_LUTR[i]));
	}
	//B2B_LUT_LUTBB_LUTB
	writeCMD(0x23);
	for (int i = 0; i < 42; i++)
	{
		writeData(pgm_read_byte(&B2B_LUT_LUTBB_LUTB[i]));
	}
	//W2B_LUT_LUTWB_LUTW
	writeCMD(0x24);
	for (int i = 0; i < 42; i++)
	{
		writeData(pgm_read_byte(&W2B_LUT_LUTWB_LUTW[i]));
	}
}

void setOTPLUT()
{
	//set panel setting to call LUTs from OTP
	writeCMD(0x00);
	writeData(0xCF); //11001111
}


//=============================================================================
#define SHUTDOWN_BETWEEN_UPDATES (0)
void loop()
{
	//Display the splash screen
	writeCMD(0x10);
	for (int i = 0; i < 5808; i++)
	{
		writeData(pgm_read_byte(&Splash_Mono_1BPP[i]));
	}

	//start data transmission 2: red data
	writeCMD(0x13);
	for (int i = 0; i < 5808; i++)
	{
		writeData(pgm_read_byte(&Splash_Red_1BPP[i]));
	}

	//refresh the display
	writeCMD(0x12);
	while (0 == digitalRead(EPD_READY));
	delay(5000);


	//The remaining block of code is to demonstrate partial updates
	//Set the LUT from the OTP since we're doing partial refreshes
	setOTPLUT();

	//start data transmission 1: B&W data
	writeCMD(0x10);
	for (int i = 0; i < 5808; i++)
	{
		writeData(pgm_read_byte(&Mono_1BPP[i]));
	}

	//start data transmission 2: red data
	writeCMD(0x13);
	for (int i = 0; i < 5808; i++)
	{
		writeData(pgm_read_byte(&Red_1BPP[i]));
	}

	//refresh the display
	writeCMD(0x12);
	while (0 == digitalRead(EPD_READY));
	delay(5000);

	//currently we're setting the register LUTs for partial refresh due to an
	//issue where the OTP LUTs cause black lines to appear across the screen
	//when performing a partial update. 
	setRegisterLUT();
	
	//partial updating the screen: Black
	writeCMD(0x14);
	writeData(0x00);	//1st half x
	writeData(0x20);	//2nd half x
	writeData(0x00);	//1st half y
	writeData(0x4F);	//2nd half y
	writeData(0x00);	//1st half w
	writeData(0x40);	//2nd half w
	writeData(0x00);	//1st half l
	writeData(0x3C);	//2nd half l

	for (int h = 0; h < 60; h++)
	{
		for (int i = 0; i < 8; i++) 
		{
			writeData(0x00);
		}
	}

	//partial refresh of the same area as the partial update
	writeCMD(0x16);
	writeData(0x00);	//1st half x
	writeData(0x20);	//2nd half x
	writeData(0x00);	//1st half y
	writeData(0x4F);	//2nd half y
	writeData(0x00);	//1st half w
	writeData(0x40);	//2nd half w
	writeData(0x00);	//1st half l
	writeData(0x3C);	//2nd half l
	
	while (0 == digitalRead(EPD_READY));
	//wait so you can view the screen
	delay(5000);



	//partial updating the screen: Black
	writeCMD(0x14);
	writeData(0x00);	//1st half x
	writeData(0x20);	//2nd half x
	writeData(0x00);	//1st half y
	writeData(0x4F);	//2nd half y
	writeData(0x00);	//1st half w
	writeData(0x40);	//2nd half w
	writeData(0x00);	//1st half l
	writeData(0x3C);	//2nd half l

	for (int h = 0; h < 60; h++)
	{
		for (int i = 0; i < 8; i++)
		{
			writeData(0x00);
		}
	}
	//partial updating the screen: Red
	writeCMD(0x15);
	writeData(0x00);	//1st half x
	writeData(0x20);	//2nd half x
	writeData(0x00);	//1st half y
	writeData(0x4F);	//2nd half y
	writeData(0x00);	//1st half w
	writeData(0x40);	//2nd half w
	writeData(0x00);	//1st half l
	writeData(0x3C);	//2nd half l

	for (int h = 0; h < 60; h++)
	{
		for (int i = 0; i < 8; i++)
		{
			writeData(0xFF);
		}
	}
	//partial refresh of the same area as the partial update
	writeCMD(0x16);
	writeData(0x00);	//1st half x
	writeData(0x20);	//2nd half x
	writeData(0x00);	//1st half y
	writeData(0x4F);	//2nd half y
	writeData(0x00);	//1st half w
	writeData(0x40);	//2nd half w
	writeData(0x00);	//1st half l
	writeData(0x3C);	//2nd half l

	while (0 == digitalRead(EPD_READY));
	//wait so you can view the screen
	delay(5000);

	

}
//=============================================================================
