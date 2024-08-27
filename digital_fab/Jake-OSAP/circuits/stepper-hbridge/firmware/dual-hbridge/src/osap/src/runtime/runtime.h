// runtime !

#ifndef RUNTIME_H_
#define RUNTIME_H_

#include <Arduino.h>
#include "../osap_config.h"
#include "../packets/routes.h"
#include "../utils/fp_clock_utils.h"

class NetResponder;
class VPacket;
class VPort;
class LinkGateway;

typedef struct TimeStats {
  uint8_t tier = 255;
  uint64_t lastRx = 0;
  // this should be nanoseconds, right ? 
  // maybe we need to redo ... some more ... 
  int64_t offset = 0;
} TimeStats;

class OSAP_Runtime {
  public:
    // con-structor, 
    OSAP_Runtime(const char* _typeName, const char* _name);
    OSAP_Runtime(const char* _typeName);

    // startup the OSAP instance and link layers 
    void begin(void);
    // operate the runtime 
    void loop(void);

    // ute-aids, 
    void attachDebugFunction(void (*_printFuncPtr)(String));
    // and debug-'ers 
    static void error(String msg);
    static void debug(String msg);

    // big-debuggers we compile guard... 
    #ifdef OSAP_CONFIG_INCLUDE_DEBUG_MSGS
    static String printRoute(Route* route);
    static String printPacket(VPacket* pck);
    #endif 

    // time service API 
    uint64_t getSystemMicroseconds(void);
    float getClockSkewAsFloat(void);

    // instance-getter, for singleton-ness, 
    static OSAP_Runtime* getInstance(void);

    // lists ! 
    VPort* ports[OSAP_CONFIG_MAX_PORTS];
    uint16_t portCount = 0;
    // TODO: links, not linkGateways ? 
    LinkGateway* links[OSAP_CONFIG_MAX_LGATEWAYS];
    uint16_t linkCount = 0;
    // BGateway* bgateways[OSAP_CONFIG_MAX_BGATEWAYS];
    uint16_t bgatewayCount = 0;

    uint32_t debug_totalPacketsTimedOut = 0;
    uint8_t debug_stackServiceHighWaterMark = 0;

    uint8_t currentPacketHold = 0;
    uint8_t maxPacketHold = 2;

    // these should be private, then have a set of values we can get sats for 
    fpint64_t clockSkew = fp_int64ToFixed64(1);
    // how many us per second of skew, per us of offset ? 
    fpint64_t clockSkewProportionalTerm = fp_float32ToFixed64(0.000001F);
    fpint64_t propTerm = fp_int64ToFixed64(0);

    fpint64_t propFilterAlpha = fp_float32ToFixed64(0.95F);
    fpint64_t propFilterOneMinusAlpha = fp_float32ToFixed64(0.05F);

    uint8_t ourTimeTier = 255;
    
    int64_t clockOffsetHardTrigger = 1000000;
    bool useHardOffsetJumps = true;
    // we can accumulate at some interval (microseconds)
    uint64_t timeCalcInterval = 100000;
    uint64_t underlyingStampPrevious = 0;
    uint64_t timeBaseAtLastCalculation = 0;
    // take note of hard resets, ignore returnals from prior op:
    // rendered in systems' own clock 
    uint64_t lastHardReset = 0;


  private:
    // only one among us 
    static OSAP_Runtime* instance;

    // discovery ute, 
    friend class NetResponder; 
    NetResponder* responder; 
    
    // stack (!) 
    VPacket* stack;
    size_t stackSize;

    // names for the module,
    // we allow 64-char typenames for modules 
    char typeName[OSAP_PROPERNAMES_MAX_CHAR];
    char moduleName[OSAP_PROPERNAMES_MAX_CHAR];

    // utility objs / buffers 
    static Route _route;
    static uint8_t _payload[OSAP_CONFIG_PACKET_MAX_SIZE];

    // graph traversals need to recognize loops, 
    // so we stash a stateful id of last-to-scope-check-us, 
    // so that traversers can connect dots... it's four random bytes 
    uint8_t previousTraverseID[4] = { 0, 0, 0, 0 };

    // time states and loop
    void timeLoop(void);
    void timeOnStampReturn(uint8_t link, uint8_t tier, uint64_t txTime, uint64_t stamp);

    // measurements from our neighbours: 
    // I suppose we could store this info in the link
    TimeStats perLinkTimeStats[OSAP_CONFIG_MAX_LGATEWAYS];

    uint64_t calculateSystemMicroseconds(bool interval);
    void setSystemMicroseconds(uint64_t _us);

    // we also do round-robin querying of our neighbours 
    uint8_t timeQueryRecipient = 0;
    uint64_t timeQueryLastTime = 0;
    uint64_t timeQueryInterval = 100000;

    // local ute for transport-query replies, 
    // this stuffs replies back into the same packet-allocation, 
    // so we don't need to re-allocate stack, etc, 
    void reply(VPacket* pck, uint8_t* data, size_t len);

    // and similar ute for us to send to neighbours... 
    void send(VPacket* pck, Route* route, uint8_t* data, size_t len);

    // local handler for system messages 
    void handleSystemMessage(VPacket* pck);

    // and those debug utes 
    static void (*printFuncPtr)(String);
};

#endif 