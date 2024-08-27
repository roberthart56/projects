#ifndef NET_RESPONDER_H_
#define NET_RESPONDER_H_ 

#include "../transport/sequential_receiver.h"

class NetResponder : public OSAP_Sequential_Receiver {
  public:
    NetResponder(void);
    size_t onData(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort, uint8_t* reply) override;

  private:
    OSAP_Runtime* rt;
};

#endif 