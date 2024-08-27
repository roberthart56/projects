from typing import cast, Tuple 
from osap.osap import OSAP 

class MAXLStepper:
    def __init__(self, osap: OSAP, device_name: str):
        self.device_name = device_name 
        self._set_current_scale_rpc = osap.rpc_caller(device_name, "setCurrentScale")
        self._get_limit_state_rpc = osap.rpc_caller(device_name, "getLimitState")
        self._set_final_scalar_rpc = osap.rpc_caller(device_name, "setFinalScalar")
        self._maxl_set_interval_rpc = osap.rpc_caller(device_name, "maxl_setInterval")
        self._maxl_add_control_point_rpc = osap.rpc_caller(device_name, "maxl_addControlPoint")
        self._maxl_get_error_message_rpc = osap.rpc_caller(device_name, "maxl_getErrorMessage")
        self._maxl_get_position_rpc = osap.rpc_caller(device_name, "maxl_getPosition")
        self.callers = [
            self._set_current_scale_rpc,
            self._get_limit_state_rpc,
            self._set_final_scalar_rpc,
            self._maxl_set_interval_rpc,
            self._maxl_add_control_point_rpc,
            self._maxl_get_error_message_rpc,
            self._maxl_get_position_rpc
        ]
        
    async def begin(self):
        for caller in self.callers:
            await caller.begin()
    
    async def set_current_scale(self, duty: float):
        await self._set_current_scale_rpc.call(duty)
        return
    
    async def get_limit_state(self)-> Tuple[int, bool] :
        time, state = await self._get_limit_state_rpc.call() #type: ignore
        return cast(int, time), cast(bool, state)
        
    
    async def set_final_scalar(self, scalar: float):
        await self._set_final_scalar_rpc.call(scalar)
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
        
    