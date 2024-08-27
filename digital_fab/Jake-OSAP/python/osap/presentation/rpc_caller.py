from ast import List
from dataclasses import dataclass
from typing import List, TYPE_CHECKING
from enum import Enum

from ..utils.serdes import deserialize_tight_utf8, deserialize_tight_u8, deserialize_tight_switch, serialize_tight_switch, typekey_to_name, typekey_to_pythonic_name, TypeLengths

from ..transport.sequential_tx import SequentialTransmitter

if TYPE_CHECKING:
    from ..osap import OSAP
    from ..packets.routes import Route


class RPCKeys(Enum):
    SIG_REQ = 1
    SIG_RES = 2
    FUNC_CALL = 3
    FUNC_RETURN = 4


@dataclass
class RPCVal:
    type_name: str
    type_name_pythonic: str 
    name: str

@dataclass
class FunctionSignature:
    name: str
    pythonic_name: str 
    return_types: List[RPCVal]
    args: List[RPCVal]


class RPCCaller:
    def __init__(self, osap: 'OSAP',
                 module_name: str, func_name: str,
                 implementer_module_route: 'Route', implementer_port: int):
        self.transmitter = SequentialTransmitter(osap.runtime, func_name, "rpc_caller")
        self.module_name = module_name 
        self.func_name = func_name
        self.implementer_module_route = implementer_module_route
        self.implementer_port = implementer_port
        self.signature: FunctionSignature | None = None

    async def begin(self, verbose = False):
        # we'll write a msg to ask for the goods,
        dg = bytearray(1)
        dg[0] = RPCKeys.SIG_REQ.value
        # print(f"sending dg for {self.port.name} ...")
        res = await self.transmitter.send(self.implementer_module_route, self.implementer_port, dg)
        if res is None:
            raise Exception(F"RPCCaller SIG_REQ to {self.func_name} returns None")
        # let's see what's up here,
        # print(f"got a res for {self.func_name}, it follows...")
        # print(res)
        # print(', '.join(str(b) for b in res))
        if res[0] != RPCKeys.SIG_RES.value:
            raise Exception("RPCCaller SIG_REQ returns with oddball key?")

        rptr = 1 

        # function name appears first, 
        function_name, increment = deserialize_tight_utf8(res, rptr)
        rptr += increment

        # then return count and types, 
        return_count, increment = deserialize_tight_u8(res, rptr)
        rptr += increment 
        return_types: List[RPCVal] = [] 
        for i in range(return_count):
            return_types.append(RPCVal(typekey_to_name(res[rptr]), typekey_to_pythonic_name(res[rptr]), ""))
            rptr += 1 

        # arg count and types, 
        arg_count, increment = deserialize_tight_u8(res, rptr)
        rptr += increment
        args: List[RPCVal] = []
        for i in range(arg_count):
            args.append(RPCVal(typekey_to_name(res[rptr]), typekey_to_pythonic_name(res[rptr]), ""))
            rptr += 1

        # return value names, 
        for i in range(return_count):
            return_types[i].name, increment = deserialize_tight_utf8(res, rptr)
            rptr += increment

        # argument names, 
        for i in range(arg_count):
            args[i].name, increment = deserialize_tight_utf8(res, rptr)
            rptr += increment 

        # lol ok, we have a siggy:
        self.signature = FunctionSignature(function_name, "", return_types, args)
        if verbose:
            print("RPC sig:", self.signature)


    def get_signature(self) -> FunctionSignature:
        if self.signature is None:
            raise Exception(f"No signature yet for this RPCCaller for '{self.func_name}' "
                            f"please use 'await caller.begin()' before using.")

        return self.signature

    async def call(self, *args):
        if self.signature is None:
            raise Exception(f"No signature yet for this RPCCaller for '{self.func_name}' "
                            f"please call 'await caller.begin()' before using.")
        
        # check we have the right args count:
        if len(args) != len(self.signature.args):
            raise Exception(f"While calling '{self.func_name}', you used {len(args)} "
                            f"args, but the signature specs {len(self.signature.args)}.")

        # check each given arg against our signature, 
        for i, arg in enumerate(self.signature.args):
            if arg.type_name == 'int' or arg.type_name == 'uint16' or arg.type_name == 'float':
                if isinstance(args[i], (int, float)):
                    continue 
                else:
                    raise Exception(f"A call to '{self.func_name}' has a bad argument at {i}: "
                                    f"call uses {type(args[i])}, function expects a {arg.type_name}.")
            if arg.type_name == 'string':
                if isinstance(args[i], str):
                    continue 
                else:
                    raise Exception(f"A call to '{self.func_name}' has a bad argument at {i}: "
                                    f"call uses {type(args[i])}, function expects a {arg.type_name}.")
            if arg.type_name == 'bool':
                if isinstance(args[i], bool):
                    continue 
                else:
                    raise Exception(f"A call to '{self.func_name}' has a bad argument at {i}: "
                                    f"call uses {type(args[i])}, function expects a {arg.type_name}.")

        # checks pass, call the functo: 
        # print("functo type checks pass, callin 'er")
        
        # call header 
        dg = bytearray(256)
        dg[0] = RPCKeys.FUNC_CALL.value 
        
        # ... and args all in-line, 
        wptr = 1
        for i, arg in enumerate(self.signature.args):
            wptr += serialize_tight_switch[arg.type_name](args[i], dg, wptr)
        dg = dg[:wptr]
        # print('the dg', dg)

        # send and await response, 
        res = await self.transmitter.send(self.implementer_module_route, self.implementer_port, dg)
        if res is None:
            raise Exception(f"RPCCaller FUNC_CALL to {self.func_name} is None...")

        if res[0] != RPCKeys.FUNC_RETURN.value:
           raise Exception(f"Implementer of '{self.func_name} has thrown an error...")

        # deserialize args and return em 
        if self.signature.return_types[0].type_name == 'void' or self.signature.return_types[0].type_name == 'none':
            return 

        if len(self.signature.return_types) == 1:
            val, _ = deserialize_tight_switch[self.signature.return_types[0].type_name](res, 1)
            return val 
        else:
            vals = [] 
            rptr = 1
            for ret in self.signature.return_types:
                val, increment = deserialize_tight_switch[ret.type_name](res, rptr)
                vals.append(val) 
                rptr += increment 

            return tuple(vals)