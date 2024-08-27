# ok, the python runtime, let's see... 
from typing import List, Optional
import asyncio 

# we have ... handles to link layers and to software objects, 
from .structure.links import LinkGateway, LinkImplementation
from .structure.ports import Port 

# some data structures
from .packets.routes import Route, route_from_packet 
from .packets.packets import Packet, packet_system_message 

# a helper 
from .discovery.netrunner import NetRunner
from .discovery.netresponder import NetResponder 

# and utes, keys, etc 
from .utils.keys import PacketKeys, SysMsgKeys, BuildTypeKeys, OSAPValues
from .utils.random_gen import random_five_alpha_character_gen
from .utils.serdes import deserialize_tight_utf8, deserialize_tight_u64, serialize_tight_utf8, serialize_tight_bool, serialize_tight_u8, serialize_tight_u64
from .utils.time_utils import get_microsecond_timestamp


class Runtime:
    def __init__(self, name: str = f"anon_{random_five_alpha_character_gen()}"):
        self.protocol_version = "0.7.1"
        self.type_name = "python_app"
        self.module_name = name
        self.module_version = "0.0.0"
        
        # we store some of our own packets, a-la ports, links 
        self.stack: List[Packet] = [] 
        self.stack_max_length = 8
        
        # we manage ports and links as well 
        self.ports: List[Optional[Port]] = [] 
        self.links: List[Optional[LinkGateway]] = [] 

        # stateful sweep artefact 
        self.previous_traverse_id: bytearray = bytearray([0, 0, 0, 0])

        # we have some timers... tbd 
        self.loop_timer = False # ? 
        # quicky on/off switch for time sync, for a debug task:
        self._answer_time_reqs = True 

        # at the 0th port, we have our internal DNS 
        self.local_dns = NetResponder(self) 

        # we have a helper class to ask questions of others
        self.netrunner = NetRunner(self) 


    def set_module_name(self, name: str):
        if len(name) >= OSAPValues.ProperNamesMaxChar:
            name = name[0:OSAPValues.ProperNamesMaxChar - 1]

        self.module_name = name 

    def port_factory(self, name: str, type_name: str = "bare")-> Port:
        # guard name uniqueness 
        for port in self.ports:
            if port == None:
                continue 
            if port.name == name:
                name += f"_{random_five_alpha_character_gen()}"
        
        # build the object, and stuff it in our list 
        prt = Port(self, len(self.ports), type_name, name)
        self.ports.append(prt)

        return prt 

    def link_factory(self, implementation: LinkImplementation):
        # guard name uniqueness 
        for link in self.links:
            if link == None:
                continue 
            if link.name == implementation.name:
                implementation.name += f"_{random_five_alpha_character_gen()}"

        # build and append it, in an open index if possible 
        lnk: LinkGateway
        lost = False

        for l in range(len(self.links)):
            if self.links[l] == None:
                lnk = LinkGateway(self, l, implementation)
                lost = True
                break

        if not lost:
           lnk = LinkGateway(self, len(self.links), implementation)
           self.links.append(lnk)

        return lnk
    
    async def await_stack_space(self):
        while True:
            if len(self.stack) < self.stack_max_length:
                return 
            else:
                await asyncio.sleep(0)

    def handle_packet(self, packet: Packet):
        ptr = packet.data[0]
        packet_key = packet.data[ptr] >> 6 
        # print('handle_packet key:', packet_key)

        def handle_dgrm():
            source_index = ((packet.data[ptr] & 0b00001111) << 6) | ((packet.data[ptr + 1] & 0b11111100) >> 2)
            destination_index = ((packet.data[ptr + 1] & 0b00000011) << 2) | packet.data[ptr + 2]
            port = self.ports[destination_index]
            if port is not None:
                # slice out the datagram, and record the route, 
                datagram = packet.data[ptr + 3:]
                route = route_from_packet(packet) 
                # reverse that route, and delete that packet object:
                packet.delete()
                route.reverse()
                # now we can hand it over to the recipient port, 
                port.on_data_callable(datagram, route, source_index)
            else:
                print(f"rx'd a packet for non-existent port {destination_index}, tossing it")
                packet.delete()

        def handle_lfwd():
            index = packet.data[ptr] & 0b00011111 
            link = self.links[index]
            if link is not None:
                if link.clear_to_send() and link.is_open():
                    link.send(packet.data)
                    packet.delete()
                # else:
                    # not clear, hold and wait, check next cycle: 
                    # self.request_loop_cycle()
            else:
                print(f"attempted to tx along non-existent link at index {index}")
                packet.delete()

        def handle_bfwd():
            packet.delete()
            print("deleted BFWD msg in queue, nonsense in this context")

        def handle_smsg():
            self.handle_system_msg(packet)

        def handle_default():
            print(f"unknown packet_key here {packet_key}")
            packet.delete() 

        packet_switch = {
            PacketKeys.DGRM.value: handle_dgrm,
            PacketKeys.LFWD.value: handle_lfwd,
            PacketKeys.BFWD.value: handle_bfwd,
            PacketKeys.SMSG.value: handle_smsg,
        }

        handler = packet_switch.get(packet_key, handle_default)
        handler() 
        # end handle_packet 

    def handle_system_msg(self, packet):
        ptr = packet.data[0] 
        packet_key = packet.data[ptr] & 0b00011111 

        def handle_time_stamp_req():
            if self._answer_time_reqs:
                res = bytearray(18)
                res[0] = 0 | PacketKeys.SMSG.value << 6 | SysMsgKeys.TIME_STAMP_RES.value
                # read-in and copy their stamp back:
                tx_stamp, _ = deserialize_tight_u64(packet.data, ptr + 1)
                # stamp, our stamp...
                serialize_tight_u64(tx_stamp, res, 1)
                serialize_tight_u64(get_microsecond_timestamp(), res, 9)
                # print(tx_stamp, get_microsecond_timestamp())
                # at the moment we are always 0 tier 
                serialize_tight_u8(0, res, 9 + 8)
                self.reply(packet, res)
            else: 
                packet.delete()

        def handle_time_stamp_res():
            # python not issuing stamp-request messages yet, 
            print("oddball / unfinished: got a res for time_stamp")
            print(packet.data) 
            packet.delete() 
                
        def handle_default():
            print(f"unknown smsg key: {packet_key}")
            packet.delete()
            return 
        
        smsg_switch = {
            SysMsgKeys.TIME_STAMP_REQ.value: handle_time_stamp_req,
            SysMsgKeys.TIME_STAMP_RES.value: handle_time_stamp_res,
        }

        # print('smsg_switch key: ', packet_key)
        handler = smsg_switch.get(packet_key, handle_default)
        handler() 
        # end handle_system_msg 

    def reply(self, packet: Packet, payload: bytearray):
        # get and reverse route (from->to) sender, 
        route = route_from_packet(packet) 
        route.reverse() 
        # de- and re-allocate a msg 
        packet.delete()
        self.stack.append(packet_system_message(self, route, payload))

    async def loop(self):
        # TODO would be adding graceful exit-clauses for each coroutine, 
        while True:
            # (0) would clear timers
            now = get_microsecond_timestamp()
            # print(f"now {now}") 

            # (1) collect packets from our own, and our ports' and links' stacks, 
            packets: List[Packet] = []
            packets.extend(self.stack)
            for port in self.ports:
                if port is not None:
                    packets.extend(port.get_packets_to_service())
            for link in self.links:
                if link is not None:
                    packets.extend(link.get_packets_to_service())

            # (2) sort those by service deadline, so that we service the neediest first 
            packets = sorted(packets, key = lambda packet: packet.service_deadline)

            # (3) service each in their sorted order,
            for packet in packets:
                # (3.1) if it's past the deadline, wipe it:
                if packet.service_deadline < now:
                    print(f"timing out a packet w/ key: {packet.data[packet.data[0]] >> 6} 1st index: {packet.data[packet.data[0] & 0b00011111]}")
                    packet.delete() 
                    continue 

                self.handle_packet(packet)

            # (4) sleep / redux 
            await asyncio.sleep(0) 

    async def run(self):
        # setup and then run loop
        # I'm trying to anticipate links popping-in and dropping off here, 
        def get_link_coroutines():
            routines = [] 
            for link in self.links:
                if link is not None:
                    routines.append(link.run())
            return routines 
        # we have tasks from all over, 
        tasks = [
            self.loop(),
            *(get_link_coroutines()),
        ]

        await asyncio.gather(*tasks)
