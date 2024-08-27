// integration of a simple port that ingests raw-byte type packet handlers 
/*
#ifndef PORT_BARE_H_
#define PORT_BARE_H_

#include "../structure/ports.h"

#define PNAMED_NAME_MAX_CHARS 32

// keys for this layer 
#define PNAMED_NAMEREQ 1
#define PNAMED_NAMERES 2 
#define PNAMED_MSG 3 
#define PNAMED_ACK 4 

class OSAP_Port : public VPort {
  public:
    // -------------------------------- Constructors
    // with a func-that-has-reply-mechanic
    OSAP_Port(const char* _name, size_t (*_onMsgFunction)(uint8_t* data, size_t len, uint8_t* reply));
    // with a dummy func that has no reply 
    OSAP_Port(const char* _name, void (*_onMsgFunction)(uint8_t* data, size_t len));

    // -------------------------------- Port-Facing API
    // we override the onPacket handler, 
    void onPacket(uint8_t* data, size_t len, Route* route, uint16_t sourcePort) override;

  private:
    // the user-provided name and callback
    size_t (*onMsgFunctionWithReply)(uint8_t* data, size_t len, uint8_t* reply) = nullptr;
    void (*onMsgFunctionWithoutReply)(uint8_t* data, size_t len) = nullptr;
};

#endif 
*/