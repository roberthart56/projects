// auto-rpc-rollup port 

#ifndef PORT_RPC_H_
#define PORT_RPC_H_

#include "../transport/sequential_receiver.h"
#include "../utils/serdes.h"
#include "./port_rpc_helpers.h"
#include <tuple>

#define PRPC_KEY_SIGREQ 1
#define PRPC_KEY_SIGRES 2
#define PRPC_KEY_FUNCCALL 3
#define PRPC_KEY_FUNCRETURN 4

// see osap.h for macro definition BUILD_RPC()

// see ./port_rpc_helpers.h for much of the wizardry required, 
// ------------------------------------ the actual class 
template <typename Func>
class OSAP_Port_RPC;

template <typename Ret, typename... Args>
class OSAP_Port_RPC<Ret(*)(Args...)> : public OSAP_Sequential_Receiver {
  public:
    // to diff void-returners, 
    using ResultType = typename ReturnType<Ret>::Type;

    // -------------------------------- Constructors 
    // base constructor 
    OSAP_Port_RPC(
      Ret(*funcPtr)(Args...), const char* functionName, const char* argNames, const char* retNames
    ) : OSAP_Sequential_Receiver("rpc_implementer", functionName)
    {
      // stash names and the functo 
      _funcPtr = funcPtr;
      strncpy(_functionName, functionName, PRPC_FUNCNAME_MAX_CHAR);
      // count args using ... pattern; this is odd to me:
      // I think that the sizeof(Args) has no effect *but* causes the thing to increment, 
      // ((_numArgs ++, sizeof(Args)), ...);
      _numArgs = sizeof...(Args);
      // count return values as well (if returning tuples !) 
      if constexpr(is_tuple<Ret>::value){
        _numRets = std::tuple_size<Ret>::value;
      } else {
        // if we have just one value, 
        _numRets = 1;
      }
      // and then read-while-copying, and throw some error if we don't have 
      // the right count of args... 
      argSplitter(argNames, _argNames);
      argSplitter(retNames, _retNames);
    }
    // deferring constructor for whence we have args only, 
    OSAP_Port_RPC(
      Ret(*funcPtr)(Args...), const char* functionName, const char* argNames
    ) : OSAP_Port_RPC(funcPtr, functionName, argNames, "") {}
    // deferring constructor for whence we have no args or return names 
    OSAP_Port_RPC(
      Ret(*funcPtr)(Args...), const char* functionName
    ) : OSAP_Port_RPC(funcPtr, functionName, "", "") {}
  
    // -------------------------------- OSAP-Facing API
    // override the packet handler, 
    size_t onData(uint8_t* data, size_t len, Route* sourceRoute, uint16_t sourcePort, uint8_t* reply) override {
      switch(data[0]){
        case PRPC_KEY_SIGREQ:
          {
            // write response key and msg id 
            size_t wptr = 0;
            reply[wptr ++] = PRPC_KEY_SIGRES;

            // write the function name 
            serializeTight<char*>(_functionName, reply, &wptr);

            // write return-values count, and type: 
            if constexpr(is_tuple<Ret>::value){
              // serialize using recursive rollup, 
              reply[wptr ++] = _numRets;
              // TODO: should be writeTupleSignatures 
              writeTupleKeys(resultStorage.result, reply, &wptr);
            } else {
              // if we have just one value, 
              reply[wptr ++] = _numRets;
              reply[wptr ++] = getTypeKey<Ret>();
            }

            // write args count, type and names 
            reply[wptr ++] = _numArgs;
            // add a type key to the payload for each arg in Args...
            // this is a "fold expression" ... which is not available until c++17 
            // instead, we could use recursive template expansions 
            (..., (reply[wptr++] = getTypeKey<Args>())); 

            // write in return names, 
            for(uint8_t a = 0; a < _numRets; a ++){
              serializeTight<char*>(_retNames[a], reply, &wptr);
            }

            // finally arg names, 
            for(uint8_t a = 0; a < _numArgs; a ++){
              serializeTight<char*>(_argNames[a], reply, &wptr);
            }

            // we are done, ship it back: 
            return wptr; 
          }
        case PRPC_KEY_FUNCCALL:
          {
            // response key and msg id 
            size_t wptr = 0;
            reply[wptr ++] = PRPC_KEY_FUNCRETURN;
            // we'll be reading starting at [1] in the packet (after the key) 
            size_t rptr = 1;
            // we have four cases to deal with: void-void, void-args, ret-void, ret-args, 
            // another note on the compiler availability: `constexpr` is only available since c++17, 
            // so it might be that we need to specialize templates for each case void-void...ret-args etc 
            if constexpr (sizeof...(Args) == 0){
              if constexpr (std::is_same<Ret, void>::value){
                // we are void-void, 
                _funcPtr();
              } else {
                // ret-void, 
                resultStorage.result = _funcPtr();
              }
            } else {
              // each of the following conditions has args, so deserialize those:
              argStorage.tuple = deserializeArgs<Args...>(data, &rptr);
              if constexpr (std::is_same<Ret, void>::value) {
                // this is void-args, we use 'apply' but there is no storage of the return type
                // note that std::apply is only available since c++17, so this would also require 
                // rework, although (since tuples are available since c++14), it should be possible 
                // again using recursive template expansion... 
                std::apply(_funcPtr, argStorage.tuple);
              } else {
                // this is ret-args, we use 'apply' and stash the result, 
                resultStorage.result = std::apply(_funcPtr, argStorage.tuple);
              }               
            }
            // in both cases where we have some result, we serialize:
            if constexpr (!(std::is_same<Ret, void>::value)){
              // if we have a return tuple... 
              if constexpr(is_tuple<Ret>::value){
                // serialize using recursive rollup, 
                // OSAP_DEBUG("hello tuple serdes");
                serializeTuple(resultStorage.result, reply, &wptr);
              } else {
                // if we have just one value, 
                serializeTight<Ret>(resultStorage.result, reply, &wptr);
              }
            }
            // currently void returners simply donot serialize anything on the way up,  
            // so that'd be it, we can sendy:
            return wptr;
          }
        default:
          OSAP_Runtime::error("bad onPacket key \nto PRPC");
          return 0;
      }
    }

  private: 
    // the pointer, etc... 
    Ret(*_funcPtr)(Args...) = nullptr;
    uint8_t _numArgs = 0;
    uint8_t _numRets = 0; 
    char _functionName[PRPC_FUNCNAME_MAX_CHAR];
    char _argNames[PRPC_MAX_ARGS][PRPC_ARGNAME_MAX_CHAR];
    char _retNames[PRPC_MAX_ARGS][PRPC_ARGNAME_MAX_CHAR]; // 33.0 21.4 
    // we allocate storage for the function results and args here to avoid stack overflow, 
    // and these both use template helpers that simply store nothing when no args or no return type is present 
    ResultStorage<Ret, std::is_same<Ret, void>::value> resultStorage;
    ArgStorage<Args...> argStorage;
};


#endif 
