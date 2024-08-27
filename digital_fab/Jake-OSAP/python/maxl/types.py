# import numpy as np 
import numpy.typing as npt 

from dataclasses import dataclass 
from enum import Enum 
# from typing import List, Callable

# from modules.maxl_stepper import MAXLStepper

# valid intervals, in us, to run the system 
class MAXLInterpolationIntervals(Enum):
    # name, us, bits 
    INTERVAL_01024 = [1024,  10]
    INTERVAL_02048 = [2048,  11]
    INTERVAL_04096 = [4096,  12]
    INTERVAL_08192 = [8192,  13]
    INTERVAL_16384 = [16384, 14]
    INTERVAL_32768 = [32768, 15]
    INTERVAL_65536 = [65536, 16]    


@dataclass 
class MAXLControlPoint:
    position_cartesian: npt.NDArray
    position_actuator: npt.NDArray
    time: int 
    flags: int = 0 
    tx_time: int = 0     

@dataclass 
class MAXLStates:
    time_us: int 
    positions: npt.NDArray
    velocities: npt.NDArray
    accelerations: npt.NDArray
    jerks: npt.NDArray
