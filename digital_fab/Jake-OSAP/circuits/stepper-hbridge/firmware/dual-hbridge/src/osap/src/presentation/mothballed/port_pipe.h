// data send-er, one-sided, one-channeled 
/*
#ifndef PORT_PIPE_H_
#define PORT_PIPE_H_

#include "../structure/ports.h"

#define PONEPIPE_SETUP 44
#define PONEPIPE_SETUP_RES 45 
#define PONEPIPE_MSG 77 

class OSAP_Port_Pipe : public VPort {
  public:
    OSAP_Port_Pipe(const char* _name);
    void onPacket(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort) override;
    void write(uint8_t* data, size_t len);
  private:
    uint16_t portNumberAtReciever = 0;
    Route routeToReciever;
    uint8_t outBuffer[OSAP_CONFIG_PACKET_MAX_SIZE];
};

#endif 
*/