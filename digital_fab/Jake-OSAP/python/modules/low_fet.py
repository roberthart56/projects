from typing import cast, Tuple 
from osap.osap import OSAP 

class LowFet:
    def __init__(self, osap: OSAP, device_name: str):
        self.device_name = device_name 
        self._set_gate_rpc = osap.rpc_caller(device_name, "setGate")
        self._pulse_gate_rpc = osap.rpc_caller(device_name, "pulseGate")
        self._maxl_set_interval_rpc = osap.rpc_caller(device_name, "maxl_setInterval")
        self._maxl_add_control_point_rpc = osap.rpc_caller(device_name, "maxl_addControlPoint")
        self._maxl_get_error_message_rpc = osap.rpc_caller(device_name, "maxl_getErrorMessage")
        self._maxl_get_position_rpc = osap.rpc_caller(device_name, "maxl_getPosition")
        self.callers = [
            self._set_gate_rpc,
            self._pulse_gate_rpc,
            self._maxl_set_interval_rpc,
            self._maxl_add_control_point_rpc,
            self._maxl_get_error_message_rpc,
            self._maxl_get_position_rpc
        ]
        
    async def begin(self):
        for caller in self.callers:
            await caller.begin()
    
    async def set_gate(self, duty: float):
        await self._set_gate_rpc.call(duty)
        return
    
    async def pulse_gate(self, duty: float, duration_ms: int):
        await self._pulse_gate_rpc.call(duty, duration_ms)
        return
    
    async def maxl_set_interval(self, intervalNumBits: int):
        await self._maxl_set_interval_rpc.call(intervalNumBits)
        return
    
    async def maxl_add_control_point(self, time: int, point: float, flags: int):
        await self._maxl_add_control_point_rpc.call(time, point, flags)
        return
    
    async def maxl_get_error_message(self) -> str:
        result = await self._maxl_get_error_message_rpc.call()
        return cast(str, result)
    
    async def maxl_get_position(self)-> Tuple[int, float] :
        time, position = await self._maxl_get_position_rpc.call() #type: ignore
        return cast(int, time), cast(float, position)
        
    