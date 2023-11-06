#include "MirfSpiDriver.h"

#ifndef __MIRF_SOFTWARE_SPI_DRIVER
#define __MIRF_SOFTWARE_SPI_DRIVER 

class MirfSoftwareSpiDriver : public MirfSpiDriver {

	public: 
		virtual uint8_t transfer(uint8_t data);
		virtual void begin();
		virtual void end();
		virtual void sckHi();
		virtual void sckLo();
		virtual void mosiHi();
		virtual void mosiLo();
		virtual uint8_t getMiso();
};

extern MirfSoftwareSpiDriver MirfSoftwareSpi;

#endif
