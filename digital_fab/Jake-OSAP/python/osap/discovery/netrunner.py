import asyncio 
from dataclasses import dataclass
from typing import List, TYPE_CHECKING
from osap.packets.routes import Route, route_build
from ..utils.keys import PacketKeys
from ..utils.time_utils import get_millisecond_timestamp, get_microsecond_timestamp
from ..utils.random_gen import random_four_byte_write_new, random_four_byte_check_match
from .netrunner_atomics import LinkGatewayInfoResponse, NetRunnerAtomics, PortInfoResponse, RTInfoResponse

if TYPE_CHECKING:
    from ..runtime import Runtime
    # from ..packets.routes import Route


@dataclass
class MapRuntime:
    route: Route
    module_type: str
    module_name: str
    module_version: str
    protocol_build: str
    protocol_version: str
    ports: List[PortInfoResponse]
    links: List[LinkGatewayInfoResponse]


@dataclass
class TempLink:
    source_route: Route
    source_index: int
    dest_route: Route
    dest_index: int


@dataclass
class SystemLink:
    source_runtime_index: int
    source_link_index: int
    dest_runtime_index: int
    dest_link_index: int


class SystemMap:
    def __init__(self, runtimes: List[MapRuntime], links: List[SystemLink]):
        self.runtimes = runtimes
        self.links = links

    def print(self, verbose = False):
        for rt in self.runtimes:
            print(f"RT: build: '{rt.protocol_build}' type: '{rt.module_type}' name: '{rt.module_name}' "\
                  f"at OSAP {rt.protocol_version}")
            if verbose:
                for l, link in enumerate(rt.links):
                    print(f"\t link {l}: type: '{link.type_name}'\t open: {link.is_open}")
                for p, port in enumerate(rt.ports):
                    print(f"\t port {p}: type: '{port.type_name}'\t name: '{port.name}'")


class NetRunner:
    def __init__(self, runtime: 'Runtime'):
        self.runtime = runtime
        self.atomics = NetRunnerAtomics(runtime)
        self.update_is_running = False
        self.map_completion_time = 0
        self.map = SystemMap([], [])

    async def update_map(self, print_updates = False):
        # if we're already map-updating, bail,
        if self.update_is_running:
            raise Exception('overlapped calling of osap.netrunner.update_map()')
        self.update_is_running = True
        # gobaby
        try:
            print("UPDATE_MAP STARTUP -----------------------------------------")
            # else start timers and trace ids, get going,
            sweep_start_time = get_millisecond_timestamp()
            traverse_id = random_four_byte_write_new()
            runtimes: List[MapRuntime] = []
            temp_links: List[TempLink] = []
            # edge poker ...

            async def recursor(rt_info: RTInfoResponse) -> None:
                try:
                    # get module name info
                    module_info = await self.atomics.get_module_info(rt_info.route)
                    # infill link and port info, await expand...
                    # print(f"with {rt_info.port_count} ports apparent")
                    ports = [await self.atomics.get_port_info(rt_info.route, p) for p in range(rt_info.port_count)]
                    # print(f"with {rt_info.link_count} links apparent")
                    links = [await self.atomics.get_link_info(rt_info.route, l) for l in range(rt_info.link_count)]
                    # stash that,
                    rt_map = MapRuntime(
                        route=rt_info.route,
                        module_type=module_info.type_name,
                        module_name=module_info.name,
                        module_version=module_info.version,
                        protocol_build=rt_info.protocol_build,
                        protocol_version=rt_info.protocol_version,
                        ports=ports,
                        links=links
                    )
                    runtimes.append(rt_map)
                    # now poke along routes,
                    for l, link in enumerate(rt_map.links):
                        if link.is_open:
                            search_route = route_build(rt_map.route).link(l).end()
                            if print_updates:
                                print(f"About to search along a new route:")
                                search_route.print()
                            try:
                                next_rt_info = await self.atomics.get_rtinfo(search_route, traverse_id)
                            except TimeoutError as err:
                                if print_updates:
                                    print(F"... next_rt unavailable, bailing on link {l}")
                                continue  

                            if random_four_byte_check_match(next_rt_info.previous_traverse_id, traverse_id):
                                if print_updates:
                                    print(F"... avoided a re-up to\n{next_rt_info.route.print(return_string=True)}\n----")
                                continue
                            if next_rt_info.instruction_of_arrival[0] >> 6 != PacketKeys.LFWD.value:
                                # print(next_rt_info.route, next_rt_info.instruction_of_arrival)
                                raise Exception("Entry via link, but entry-instruction is not reporting linkf...")
                            else:
                                entry_index = next_rt_info.instruction_of_arrival[0] & 0b00011111
                                temp_links.append(TempLink(
                                    source_route=rt_info.route,
                                    source_index=l,
                                    dest_route=next_rt_info.route,
                                    dest_index=entry_index
                                ))
                                await recursor(next_rt_info)

                except Exception as err:
                    raise err

            # the kickoff,
            own_rt_info = await self.atomics.get_rtinfo(route_build().end(), traverse_id)
            # print('our own rt_info', own_rt_info)
            await recursor(own_rt_info)

            # ... a while later, we do representation cleanup:
            print("UPDATE_MAP recursor cycle completed... fixing link indices...")
            links: List[SystemLink] = []
            for temp_link in temp_links:
                source_runtime_index = -1
                dest_runtime_index = -1
                for i, rt in enumerate(runtimes):
                    if rt.route == temp_link.source_route:
                        source_runtime_index = i
                        break
                for i, rt in enumerate(runtimes):
                    if rt.route == temp_link.dest_route:
                        dest_runtime_index = i
                        break
                if source_runtime_index == -1 or dest_runtime_index == -1:
                    raise Exception(f"Failed to find runtime-indices for link hookup after a graph search (?) {source_runtime_index} ... {dest_runtime_index}")

                links.append(SystemLink(
                    source_runtime_index=source_runtime_index,
                    source_link_index=temp_link.source_index,
                    dest_runtime_index=dest_runtime_index,
                    dest_link_index=temp_link.dest_index,
                ))
                #     [
                #     [source_runtime_index, temp_link.source_index],
                #     [dest_runtime_index, temp_link.dest_index]
                # ])

            print(f"UPDATE_MAP ----------------------- done after {round((get_millisecond_timestamp() - sweep_start_time), 3)}ms")
            self.map = SystemMap(runtimes, links)
            self.map_completion_time = get_millisecond_timestamp()
            self.update_is_running = False 
            return self.map

        except Exception as err:
            print(f"UPDATE_MAP sweep fails after {(get_millisecond_timestamp() - sweep_start_time)}ms")
            raise err

        finally:
            self.map_discovery_is_running = False
    
        # end update_map

    # properly, this would add a metric for clock stability as well... 
    async def await_time_settle(self, print_updates = False, await_spread_epsilon_us = 1000):
        try:
            skew_alpha = 0.95   # fw default is 0.95 
            p_gain = 0.000001   # fw default is 0.000001, minimum gain is 0.0000003

            if self.map_completion_time == 0 or len(self.map.runtimes) == 1:
                return 

            # initialize settings for each device... 
            for d, device in enumerate(self.map.runtimes):
                if device.protocol_build == 'Python':
                    continue 
                
                # basically get everyone on-time and with 1.0 skew to start even keeled, 
                now = get_microsecond_timestamp()
                await self.atomics.set_time_config(device.route, now, 1.0, skew_alpha, p_gain, True)

            ok_cycle_count = 0 
            ok_cycle_pass = 3 

            # now run a loop where we poll each, get a grouping... and post it ? 
            while True:
                clock_errors = []
                rtts = []
                for d, device in enumerate(self.map.runtimes):
                    if device.protocol_build == 'Python':
                        continue 

                    our_time = get_microsecond_timestamp()
                    time_stats = await self.atomics.get_time_config(device.route)
                    device_time = time_stats.system_time - time_stats.rtt / 2 
                    clock_errors.append(our_time - device_time)
                    rtts.append(time_stats.rtt)
                    await asyncio.sleep(0.05)

                print(F"ERRS: {[int(err) for err in clock_errors]}, \tRTT: {[int(rtt) for rtt in rtts]}")

                if all(abs(err) < await_spread_epsilon_us for err in clock_errors):
                    ok_cycle_count += 1 
                else:
                    ok_cycle_count = 0 

                if ok_cycle_count >= ok_cycle_pass:
                    print("CLOCKS OK...")
                    return 
                else:
                    await asyncio.sleep(0.25) 
        except Exception as err:
            print(err)
            return 