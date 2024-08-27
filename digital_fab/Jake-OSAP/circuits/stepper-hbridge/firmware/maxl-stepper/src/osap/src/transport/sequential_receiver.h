
#ifndef SEQUENTIAL_RX
#define SEQUENTIAL_RX 

#include "../structure/ports.h"

class OSAP_Sequential_Receiver : public VPort {
  public:
    // -------------------------------- Constructors
    OSAP_Sequential_Receiver(const char* _name, const char* _typeName);

    // -------------------------------- Port-Facing API
    // we override the onPacket handler of the port class, 
    void onPacket(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort) override;

    // and provide an overrideable to our consumer, 
    virtual size_t onData(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort, uint8_t* reply); // = 0;

};

#endif 

/*
// there's a possible version of the same that uses a handover-style function ingest, 
// but which then requires static functions to ingest; rather than instances of classes... 
// it would be possible to allow for either style in the same object, I'm leaving that option out for clarity 

// .h 
class OSAP_Sequential_Receiver : public VPort {
  public:
    // -------------------------------- Constructors
    // OSAP_Sequential_Receiver(const char* _name, size_t (*_onDataCallable)(uint8_t* data, size_t len, uint8_t* reply));
    // for void returners 
    // OSAP_Sequential_Receiver(const char* _name, void (*_onDataCallable)(uint8_t* data, size_t len, uint8_t* reply));

    // -------------------------------- Port-Facing API
    // we override the onPacket handler of the port class, 
    void onPacket(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort) override;

    // and provide an overrideable to our consumer, 
    virtual void onData(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort) = 0;

  // private:
  //     size_t (*onDataCallableWithReply)(uint8_t* data, size_t len, uint8_t* reply) = nullptr;
  //     void (*onDataCallableWithoutReply)(uint8_t* data, size_t len) = nullptr;

};

// .cpp 
OSAP_Sequential_Receiver::OSAP_Sequential_Receiver(
  const char* _name, 
  size_t (*_onDataCallable)(uint8_t* data, size_t len, uint8_t* reply)
  ) : VPort(OSAP_Runtime::getInstance(), "seqnc_rx", _name) 
{
  onDataCallableWithReply = _onDataCallable;
}

void OSAP_Sequential_Receiver::onPacket(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort){
  if(data[0] != TKEY_SEQUENTIAL_TX){
    OSAP_ERROR("rx'd oddball TKEY at sequence rx'er");
    return; 
  }

  uint8_t msgID = data[1];
  size_t replyLen = 0; 

  // call the attached function w/ an offset, 
  // note: this is from Runtime::_payload to VPort::_payload temporary... 
  if(onDataCallableWithReply != nullptr){
    replyLen = onDataCallableWithReply(data + 2, len - 2, _payload + 2);
  } else if (onDataCallableWithoutReply != nullptr){
    onDataCallableWithoutReply(data + 2, len - 2);
  }

  // stuff our info, 
  _payload[0] = TKEY_SEQUENTIAL_RX;
  _payload[1] = msgID; 

  // and ship that back out, 
  #warning memory swappage needs more consideration; do we have race cond?
  send(_payload, replyLen + 2, sourceRoute, sourcePort);
}

*/