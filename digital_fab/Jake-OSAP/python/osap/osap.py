from .runtime import Runtime
from .discovery.netrunner import NetRunner
from .presentation.rpc_caller import RPCCaller
from .utils.time_utils import get_microsecond_timestamp

class OSAP:
    def __init__(self, name: str):
        self.runtime: Runtime = Runtime(name)
        self.netrunner: NetRunner = self.runtime.netrunner
        self.port = self.runtime.port_factory
        self.link = self.runtime.link_factory

    def rpc_caller(self, module_name: str, func_name: str) -> RPCCaller:
        # we need to do some route lookup for this...
        implementer_module = None
        for rt in self.netrunner.map.runtimes:
            if rt.module_name == module_name:
                implementer_module = rt
                break

        if implementer_module is None:
            raise AttributeError(f"RPC couldn't find a module named "\
                                 f"'{module_name}' in this map, "\
                                 f"so I can't spin up an RPC Caller"\
                                 f" for '{func_name}'")

        for index, port in enumerate(implementer_module.ports):
            if port.type_name == "rpc_implementer" and port.name == func_name:
                # print(f"RPC found a '{func_name}' within '{module_name}'")
                return RPCCaller(self, module_name, func_name, implementer_module.route, index)

        raise AttributeError(f"RPC couldn't find an implementer of a "\
                             f"function named '{func_name}' within this "\
                             f"module '{module_name}'.")

    # current situation assumes py is global time boss :| 
    def get_system_microseconds(self):
        return get_microsecond_timestamp()
    
    def answer_time_reqs(self, state: bool):
        self.runtime._answer_time_reqs = state 