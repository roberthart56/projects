#ifndef LINK_UART_COBS_CRC16_H_
#define LINK_UART_COBS_CRC16_H_

#include "../structure/links.h"
#include "../packets/packets.h"
#include "link_utils/cobs.h"
#include "link_utils/crc16_ccitt.h"

#define LINK_UART_CC_BUFFER_SIZE 255

template <typename SerialImplementation> 
class OSAP_Gateway_UART_COBS_CRC16 : public LinkGateway {
  public:
    OSAP_Gateway_UART_COBS_CRC16(SerialImplementation* _impl, uint32_t _baudrate, const char* _name, uint32_t _pinYZTransciever, uint32_t _pinABTransciever):
    LinkGateway(OSAP_Runtime::getInstance(), "uart_cobs_crc", _name){
      impl = _impl; 
      baudrate = _baudrate;
      hasTrancievers = true;
      pinYZTransciever = _pinYZTransciever;
      pinABTransciever = _pinABTransciever;
    }

    OSAP_Gateway_UART_COBS_CRC16(SerialImplementation* _impl, uint32_t _baudrate, const char* _name):
    LinkGateway(OSAP_Runtime::getInstance(), "uart_cobs_crc", _name){
      impl = _impl; 
      baudrate = _baudrate;
      hasTrancievers = false;
    }

    void begin(void) override {
      if(hasTrancievers){
        pinMode(pinYZTransciever, OUTPUT);
        pinMode(pinABTransciever, OUTPUT);
        digitalWrite(pinYZTransciever, HIGH);
        digitalWrite(pinABTransciever, LOW);
      }
      impl->begin(baudrate);
      crc16_generate_table();
    }

    void loop(void) override {
      // rx while-available, 
      // NOTE: currently, we are waiting for app before rx'ing again, 
      // but we could at least buffer one extra... properly, we should have 
      // a buffer of some configured depth ....
      while(impl->available() && rxAwaitingLen == 0){
        rxBuffer[rxBufferWp ++] = impl->read();
        if(rxBufferWp >= LINK_UART_CC_BUFFER_SIZE) rxBufferWp = 0;
        if(rxBuffer[rxBufferWp - 1] == 0){
          // nicely, we can decode COBS in place, 
          size_t len = cobsDecode(rxBuffer, 255, rxBuffer);
          // rm'ing the trailing zero, 
          rxBufferLen = len - 1;
          // calculate the crc on the packet (less the crc itself), and compare to the crc reported: 
          uint16_t crc = crc16_ccitt(rxBuffer, rxBufferLen - 2);
          uint16_t tx_crc = ((uint16_t)(rxBuffer[rxBufferLen - 2]) << 8) | rxBuffer[rxBufferLen - 1];
          // pass / fail based on crc, 
          if(crc == tx_crc){
            numSuccessRx ++;
            // (removing the crc tail) 
            rxAwaitingLen = rxBufferLen - 2;
            memcpy(rxAwaiting, rxBuffer, rxAwaitingLen);
          } else {
            numFailedRx ++;
          }
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
      // calculate crc of the data in-place, 
      uint16_t crc = crc16_ccitt(data, len);
      // stick that in the tail: OK since we know OSAP has the packet locked out 
      data[len] = crc >> 8;
      data[len + 1] = crc & 255;
      txBufferLen = cobsEncode(data, len + 2, txBuffer);
      txBuffer[txBufferLen] = 0;
      txBufferLen += 1;
      txBufferRp = 0;
    }

    // and some stats, 
    uint32_t numSuccessRx = 0;
    uint32_t numFailedRx = 0; 
    uint32_t numTx = 0; 


  private: 
    // "hardware" lol 
    SerialImplementation* impl; 
    uint32_t baudrate; 
    // transcievers (if promoted to RS485...)
    bool hasTrancievers = false;
    uint32_t pinYZTransciever;
    uint32_t pinABTransciever; 
    // buffers, write/read-pointers, lengths 
    uint8_t rxAwaiting[LINK_UART_CC_BUFFER_SIZE];
    uint8_t rxAwaitingLen = 0;
    // hot-and-incoming 
    uint8_t rxBuffer[LINK_UART_CC_BUFFER_SIZE];
    uint8_t rxBufferWp = 0;
    uint8_t rxBufferLen = 0;
    // and tx, 
    uint8_t txBuffer[LINK_UART_CC_BUFFER_SIZE];
    uint8_t txBufferRp = 0;
    uint8_t txBufferLen = 0;
};

#endif 