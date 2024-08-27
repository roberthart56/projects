from multiprocessing import Value
from ..packets.routes import Route
from ..packets.packets import packet_system_message
from ..utils.keys import BuildTypeKeys, PacketKeys, NetRunnerKeys, NetRunnerKeys, OSAPValues, key_to_string
from ..transport.sequential_tx import SequentialTransmitter
from ..utils.serdes import serialize_tight_u64, serialize_tight_f32, serialize_tight_utf8, serialize_tight_bool, deserialize_tight_utf8, deserialize_tight_bool, deserialize_tight_u64, serialize_tight_u64
from ..utils.time_utils import get_microsecond_timestamp 

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..runtime import Runtime


@dataclass
class RTInfoResponse:
    route: Route
    previous_traverse_id: bytes
    protocol_build: str
    protocol_version: str
    instruction_of_arrival: bytes
    link_count: int
    bus_count: int
    port_count: int


@dataclass
class ModuleInfoResponse:
    version: str
    type_name: str
    name: str


@dataclass
class LinkGatewayInfoResponse:
    type_name: str
    name: str
    is_open: bool


@dataclass
class PortInfoResponse:
    type_name: str
    name: str


@dataclass 
class TimeConfigResponse:
    underlying_time: int 
    system_time: int 
    skew: float 
    rtt: int


# TODO much of these are repetetive and could be tightened up, i.e.
# async def await_stack_space_and_request(runtime: Any, resolver: Any, packet_data: bytearray) -> bytearray:
#     await runtime.await_stack_space()
#     request_id = resolver.write_new()
#     runtime.stack.append(packet_system_message(runtime, packet_data))
#     runtime.request_loop_cycle()
#     return await resolver.request(request_id)
# then functions just become
# datagram = ...
# res = await_stack_space_and_request()
# deserialize...

# TODO also - to have delivery guarantees at the transport layer, 
# which would be proper, we should / could use the SequentialIDResolver class ? 
# ... and need to test that over lossy links! 

# 'tis always zero 
responder_port_num = 0 

class NetRunnerAtomics:
    def __init__(self, runtime: 'Runtime'):
        self.runtime = runtime
        self.transmitter = SequentialTransmitter(runtime, "netrunner", "netrunner")
    
    async def get_rtinfo(self, route: Route, traverse_id: bytearray) -> RTInfoResponse:
        # write a datagram, 
        dg = bytearray(6)
        dg[0] = PacketKeys.SMSG.value << 6 | NetRunnerKeys.RTINFO_REQ.value
        dg[1:] = traverse_id
        # send it, awaiting response 
        res = await self.transmitter.send(route, responder_port_num, dg)
        if res is None:
            raise Exception("received None after rtinfo_req...")

        return RTInfoResponse(
            route=route,
            previous_traverse_id=res[1:5],
            protocol_build=key_to_string(res[5], BuildTypeKeys),
            protocol_version=f"{res[6]}.{res[7]}.{res[8]}",
            instruction_of_arrival=res[9:11],
            link_count=res[11] & 0b00011111,
            bus_count=0,
            port_count=((res[12] & 0b00000011) << 8) | res[13],
        )

    async def get_module_info(self, route: Route) -> ModuleInfoResponse:
        dg = bytearray([PacketKeys.SMSG.value << 6 | NetRunnerKeys.MTYPEGET_REQ.value])
        res = await self.transmitter.send(route, responder_port_num, dg)
        if res is None:
            raise Exception("received None after mtypeget_req...")

        version = f"{res[1]}.{res[2]}.{res[3]}"
        type_name, _ = deserialize_tight_utf8(res, 4)
        # second transaction for the name
        dg = bytearray([PacketKeys.SMSG.value << 6 | NetRunnerKeys.MNAMEGET_REQ.value])
        res = await self.transmitter.send(route, responder_port_num, dg)
        if res is None:
            raise Exception("received None after mnameget_req...")

        name, _ = deserialize_tight_utf8(res, 1)
        return ModuleInfoResponse(
            version=version,
            type_name=type_name,
            name=name
        )

    async def set_module_name(self, route: Route, name: str) -> None:
        if len(name) > OSAPValues.ProperNamesMaxChar:
            raise ValueError(f"OSAP has max propername length of "\
                             f"{OSAPValues.ProperNamesMaxChar} chars, "\
                             f"your request for {name} is {len(name)} chars")
        # serialize
        dg = bytearray(2 + len(name))
        dg[0] = PacketKeys.SMSG.value << 6 | NetRunnerKeys.MNAMESET_REQ.value
        serialize_tight_utf8(name, dg, 1)
        # send await
        res = await self.transmitter.send(route, responder_port_num, dg)
        if res is None:
            raise Exception("received None after mnameset_req")
        # deserialize, throw errs
        success, _ = deserialize_tight_bool(res, 1)
        if not success:
            raise ValueError(f"Your call to change a module's name to {name} "\
                             f"failed; either something went wrong or the module "\
                             f"doesn't support nonvolatile storage.")
        
    async def get_link_info(self, route: Route, index: int) -> LinkGatewayInfoResponse:
        if index >= OSAPValues.MaxLinkCount:
            raise ValueError(f"OSAP has max links of {OSAPValues.MaxLinkCount},"\
                             f"you requested info on num {index}")
        dg = bytearray([PacketKeys.SMSG.value << 6 | NetRunnerKeys.LINKINFO_REQ.value, index])
        res = await self.transmitter.send(route, responder_port_num, dg)
        if res is None:
            raise Exception("received None after linkinfo_req")
        # state is stashed here,
        is_open = True if (res[1] & 0b01100000) >> 5 else False
        # we need to wipe those before passing to deserialization: res[2] is len of type_name str
        res[1] = res[1] & 0b00011111
        if res[1] == 0:
            print("the null link...")
            return LinkGatewayInfoResponse(type_name="", name="", is_open=False)
        else:
            type_name, increment = deserialize_tight_utf8(res, 1)
            name, _ = deserialize_tight_utf8(res, 1 + increment)
            return LinkGatewayInfoResponse(type_name=type_name, name=name, is_open=is_open)

    async def get_port_info(self, route: Route, index: int) -> PortInfoResponse:
        if index >= OSAPValues.MaxPortCount:
            raise ValueError(f"OSAP has max ports of "\
                             f"{OSAPValues.MaxPortCount}, "\
                             f"you requested info on num {index}")
        dg = bytearray([PacketKeys.SMSG.value << 6 | NetRunnerKeys.PORTINFO_REQ.value, index >> 8, index & 0xFF ])
        res = await self.transmitter.send(route, responder_port_num, dg)
        if res is None:
            raise Exception("received None after portinfo_req")
        type_name, increment = deserialize_tight_utf8(res, 1)
        name, _ = deserialize_tight_utf8(res, 1 + increment)
        return PortInfoResponse(type_name=type_name, name=name)

    async def get_time_config(self, route: Route) -> TimeConfigResponse:
        dg = bytearray([PacketKeys.SMSG.value << 6 | NetRunnerKeys.TIME_CONFIG_GET_REQ.value])
        start_time = get_microsecond_timestamp() 
        res = await self.transmitter.send(route, responder_port_num, dg)
        rtt = get_microsecond_timestamp() - start_time 
        if res is None:
            raise Exception("received None after timeconfig_get_req")
        # so, this should actually have... underlying, system, skew, 
        # and then stats: jump (bool), filter, and p-term 
        underlying_time, _ = deserialize_tight_u64(res, 1)
        system_time, _ = deserialize_tight_u64(res, 9) 
        # skew is in fixed-point, base 22... let's test:
        skew_fp, _ = deserialize_tight_u64(res, 17)
        skew = float(skew_fp) / float(1 << 22)
        # dec_part = skew_fp & 0b1111111111111111111111         
        # whole_part = skew_fp >> 22 
        return TimeConfigResponse(
            underlying_time=underlying_time,
            system_time=system_time,
            skew=skew, 
            rtt=rtt 
        )

    async def set_time_config(self, route: Route, base_us: int, skew: float, filter_alpha: float, p_term: float, jumps: bool) -> None:
        if (skew < 0.8 or skew > 1.2) and skew != 0:
            raise ValueError(f"skew setting of {skew} is OOB")

        if filter_alpha > 1 or filter_alpha < 0.8:
            raise ValueError(f"filter_alpha of {filter_alpha} is OOB")
        
        if p_term < (1 / 2**22):
            raise ValueError(f"p_term of {p_term} is smaller than smallest resolveable by fxp22: {1 / 2**22}")

        dg = bytearray(22)
        dg[0] = PacketKeys.SMSG.value << 6 | NetRunnerKeys.TIME_CONFIG_SET_REQ.value

        # uint64_t setBaseUpdate = deserializeTight<uint64_t>(pck->data, &rptr);
        # float setSkew = deserializeTight<float>(pck->data, &rptr);
        # float setFilterAlpha = deserializeTight<float>(pck->data, &rptr);
        # float setPTerm = deserializeTight<float>(pck->data, &rptr);
        # bool setUseJumps = deserializeTight<bool>(pck->data, &rptr);

        serialize_tight_u64(base_us, dg, 1)
        serialize_tight_f32(skew, dg, 9)
        serialize_tight_f32(filter_alpha, dg, 13)
        serialize_tight_f32(p_term, dg, 17)
        serialize_tight_bool(jumps, dg, 21)
        # and this should actually be able to set... jump (bool), filter, and p-term
        # and we need to figure how to govern min/max p- and filter terms 
        res = await self.transmitter.send(route, responder_port_num, dg)
        # ... does this return anything ? 
        return 

