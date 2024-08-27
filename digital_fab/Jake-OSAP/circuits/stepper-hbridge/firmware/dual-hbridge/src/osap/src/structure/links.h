// links ! 

#ifndef LINKS_H_
#define LINKS_H_

#include "../runtime/runtime.h"
#include "../utils/keys.h"

class LinkGateway {
  public:
    // -------------------------------- Link-Implementers Author these Funcs
    // implement a .begin() to startup the link, 
    virtual void begin(void) = 0;

    // implement a function that is called once per runtime, 
    virtual void loop(void) = 0;

    // implement a function that reports whether/not 
    // the link is ready to send new data 
    virtual boolean clearToSend(void) = 0;

    // implement a function that reports whether/not 
    // the link is open... 
    virtual boolean isOpen(void) = 0;

    // implement a function that transmits this packet, 
    virtual void send(uint8_t* data, size_t len) = 0;

    // -------------------------------- Link-Implementers use these funcs 

    // having written off-the-line data into `pck` during loop, 
    // implementer calls this 
    void ingestPacket(VPacket* pck);

    // -------------------------------- Constructors

    LinkGateway(OSAP_Runtime* _runtime, const char* _typeName, const char* _name);

    // -------------------------------- Properties 

    char typeName[OSAP_TYPENAMES_MAX_CHAR];
    char name[OSAP_PROPERNAMES_MAX_CHAR];

    // -------------------------------- States 
    uint8_t currentPacketHold = 0;
    uint8_t maxPacketHold = 2;

    private:
      OSAP_Runtime* runtime;
      uint16_t index; 
};

#endif 