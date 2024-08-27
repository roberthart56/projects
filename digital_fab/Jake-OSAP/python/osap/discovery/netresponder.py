from typing import List, TYPE_CHECKING

from ..packets.routes import Route 
from ..transport.sequential_rx import SequentialReceiver
from ..utils.serdes import serialize_tight_utf8, deserialize_tight_utf8, serialize_tight_bool
from ..utils.keys import NetRunnerKeys, BuildTypeKeys, PacketKeys

if TYPE_CHECKING:
    from ..runtime import Runtime

class NetResponder:
    def __init__(self, runtime: 'Runtime'):
        self.receiver = SequentialReceiver(runtime, "netresponder", "netresponder")
        self.receiver.attach_on_data(self.on_data)
        self.runtime = runtime 
 
    def on_data(self, data: bytearray, source_route: Route, source_port: int):

        def handle_rtinfo_req():
            res = bytearray(14) 
            res[0] = 0 | PacketKeys.SMSG.value << 6 | NetRunnerKeys.RTINFO_RES.value
            # swap traverse ID's 
            res[1:5] = self.runtime.previous_traverse_id 
            self.runtime.previous_traverse_id = data[1:5]
            # build lang and version 
            res[5] = BuildTypeKeys.Python.value
            version_split = [int(num) for num in self.runtime.protocol_version.split(".")] 
            res[6:9] = version_split
            # entry-point,
            if(len(source_route.encoded_path) == 0):
                # was self, use nonsense 
                res[9:11] = [PacketKeys.SMSG.value << 6, 0]
            elif source_route.encoded_path[0] >> 6 == PacketKeys.LFWD.value:
                # report link of entry, 
                res[9:11] = source_route.encoded_path[0:2]
            else:
                raise Exception(f"found a nonsensical rtinforeq w/ mystery rx-path {source_route.encoded_path[0] >> 6},"\
                                f" {source_route.encoded_path[0] & 0b00011111}")

            res[11] = 0b00011111 & len(self.runtime.links)
            res[12] = (len(self.runtime.ports) >> 8) & 0b00000011
            res[13] = len(self.runtime.ports) & 255
            # print(f"handle_rtinfo_req() reporting ports: {len(self.ports)}, links: {len(self.links)}")
            return res 

        def handle_mtypeget_req():
            res = bytearray(6 + len(self.runtime.type_name)) 
            # stuffing our return keys and the msg id, 
            res[0] = 0 | PacketKeys.SMSG.value << 6 | NetRunnerKeys.MTYPEGET_RES.value
            # B2,3,4 are device version nums 
            version_split = [int(num) for num in self.runtime.module_version.split(".")] 
            res[1:4] = version_split
            # and the typeName, 
            serialize_tight_utf8(self.runtime.type_name, res, 4)
            return res
        
        def handle_mnameget_req():
            res = bytearray(3 + len(self.runtime.module_name))
            res[0] = 0 | PacketKeys.SMSG.value << 6 | NetRunnerKeys.MNAMEGET_RES.value
            serialize_tight_utf8(self.runtime.module_name, res, 1) 
            return res
        
        def handle_mnameset_req():
            new_name, _ = deserialize_tight_utf8(data, 2)
            self.runtime.module_name = new_name 
            res = bytearray(2)
            res[0] = 0 | PacketKeys.SMSG.value << 6 | NetRunnerKeys.MNAMESET_RES.value
            serialize_tight_bool(True, res, 1)
            return res 

        def handle_linkinfo_req():
            index = 0b00011111 & data[1]
            link = self.runtime.links[index] if index < len(self.runtime.links) else None 
            if link is not None:
                res = bytearray(3 + len(link.type_name) + len(link.name))
                res[0] = 0 | PacketKeys.SMSG.value << 6 | NetRunnerKeys.LINKINFO_RES.value
                wptr = 1
                wptr += serialize_tight_utf8(link.type_name, res, wptr)
                wptr += serialize_tight_utf8(link.name, res, wptr)
                # amending with the link's state: zero of false, so no-op, 
                if link.is_open():
                    res[1] |= 1 << 5
                return res 
            else:
                res = bytearray(2)
                res[0] = 0 | PacketKeys.SMSG.value << 6 | NetRunnerKeys.LINKINFO_RES.value
                res[1] = 0
                return res 
        
        def handle_businfo_req():
            raise Exception('req for bus-link info in py...')
        
        def handle_portinfo_req():
            index = ((data[1] & 0b00000011) << 8) | data[2]
            port = self.runtime.ports[index] if index < len(self.runtime.ports) else None
            if port is not None:
                res = bytearray(3 + len(port.type_name) + len(port.name))
                res[0] = 0 | PacketKeys.SMSG.value << 6 | NetRunnerKeys.PORTINFO_RES.value
                wptr = 1
                wptr += serialize_tight_utf8(port.type_name, res, wptr)
                wptr += serialize_tight_utf8(port.name, res, wptr)
                return res 
            else:
                res = bytearray(2)
                res[0] = 0 | PacketKeys.SMSG.value << 6 | NetRunnerKeys.PORTINFO_RES.value
                res[1] = 0
                return res 
        
        def handle_default():
            print(f"unknown smsg key: {data[0]}")
            return 

        netrunner_switch = {
            NetRunnerKeys.RTINFO_REQ.value: handle_rtinfo_req,
            NetRunnerKeys.MTYPEGET_REQ.value: handle_mtypeget_req,
            NetRunnerKeys.MNAMEGET_REQ.value: handle_mnameget_req,
            NetRunnerKeys.MNAMESET_REQ.value: handle_mnameset_req,
            NetRunnerKeys.LINKINFO_REQ.value: handle_linkinfo_req,
            NetRunnerKeys.BUSINFO_REQ.value: handle_businfo_req,
            NetRunnerKeys.PORTINFO_REQ.value: handle_portinfo_req,
            # no-one is asking time-config vals *of python* at the moment 
            # NetRunnerKeys.TIME_CONFIG_GET_REQ.value: ,
            # NetRunnerKeys.TIME_CONFIG_SET_REQ.value: 
        }

        # print('smsg_switch key: ', packet_key)
        handler = netrunner_switch.get(data[0], handle_default)
        return handler()

        # end of netresponder on_data 