#ifndef LINK_USB_CDC_COBS_H_
#define LINK_USB_CDC_COBS_H_

#include "../structure/links.h"
#include "../packets/packets.h"
#include "link_utils/cobs.h"

#define LINK_USB_BUFFER_SIZE 255

template <typename USBSerialImplementation> 
class OSAP_Gateway_USBCDC_COBS : public LinkGateway {
  public:
    OSAP_Gateway_USBCDC_COBS(USBSerialImplementation* _impl, const char* _name):
    LinkGateway(OSAP_Runtime::getInstance(), "usb_cdc_cobs", _name){
      impl = _impl; 
    }

    void begin(void) override {
      impl->begin(9600);
    }

    void loop(void) override {
      // rx while-available, 
      // NOTE: currently, we are waiting for app before rx'ing again, 
      // but we could at least buffer one extra... properly, we should have 
      // a buffer of some configured depth ....
      while(impl->available() && rxAwaitingLen == 0){
        rxBuffer[rxBufferWp ++] = impl->read();
        if(rxBufferWp >= LINK_USB_BUFFER_SIZE) rxBufferWp = 0;
        if(rxBuffer[rxBufferWp - 1] == 0){
          // nicely, we can decode COBS in place, 
          size_t len = cobsDecode(rxBuffer, 255, rxBuffer);
          // rm'ing the trailing zero, stuffing, 
          rxAwaitingLen = len - 1;
          memcpy(rxAwaiting, rxBuffer, rxAwaitingLen);
          // stat track 
          numRx ++;
          // every time we hit the zero, we reset these
          rxBufferLen = 0; 
          rxBufferWp = 0; 
        }
      } // end while-available rx 

      // tx while-available, 
      if(txBufferLen){
        noInterrupts();
        size_t fifoAvail = impl->availableForWrite();
        for(size_t i = 0; i < fifoAvail; i ++){
          impl->write(txBuffer[txBufferRp ++]);
          if(txBufferRp >= txBufferLen){
            // tx'ing is done, this all resets, 
            txBufferRp = 0;
            txBufferLen = 0;
            numTx ++;
            break;
          }
        }
        interrupts();
      }

      // relay to OSAP 
      if(claimPacketCheck(this) && rxAwaitingLen > 0){
        // claim a buffer, 
        VPacket* pck = claimPacketFromStack(this);
        // write into it and set length, 
        memcpy(pck->data, rxAwaiting, rxAwaitingLen);
        pck->len = rxAwaitingLen;
        // from links.cpp, apply pointer and time ops etc 
        ingestPacket(pck);
        // and clear it on our side, 
        rxAwaitingLen = 0;
      }
    }

    boolean clearToSend(void) override {
      return (txBufferLen == 0);
    }

    boolean isOpen(void) override {
      // a TODO 
      return true; 
    }

    void send(uint8_t* data, size_t len) override {
      if (!clearToSend()) return;
      txBufferLen = cobsEncode(data, len, txBuffer);
      txBuffer[txBufferLen] = 0;
      txBufferLen += 1;
      txBufferRp = 0;
    }

    // and some stats, 
    uint32_t numRx = 0;
    uint32_t numTx = 0; 

  private: 
    // "hardware" lol 
    USBSerialImplementation* impl; 
    // buffers, write/read-pointers, lengths 
    uint8_t rxAwaiting[LINK_USB_BUFFER_SIZE];
    uint8_t rxAwaitingLen = 0;
    // hot-and-incoming 
    uint8_t rxBuffer[LINK_USB_BUFFER_SIZE];
    uint8_t rxBufferWp = 0;
    uint8_t rxBufferLen = 0;
    // and tx, 
    uint8_t txBuffer[LINK_USB_BUFFER_SIZE];
    uint8_t txBufferRp = 0;
    uint8_t txBufferLen = 0;
};

#endif 