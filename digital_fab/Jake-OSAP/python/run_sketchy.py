import asyncio
import traceback 
import numpy as np 
import numpy.typing as npt 

from osap.bootstrap.auto_usb_serial.auto_usb_serial import AutoUSBPorts
from osap.osap import OSAP
from osap.utils.time_utils import get_microsecond_timestamp

from svg.svg_tools import scale_and_process_svg

from maxl.types import MAXLInterpolationIntervals 
from maxl.tools.gcode_parser import GCodeParser 

from modules.sketchy_machine_motion import SketchyMachineMotion

system_interpolation_interval = MAXLInterpolationIntervals.INTERVAL_16384
system_twin_to_real_ms = 200

machine_extents = [80, 150]
jog_rate = 100
draw_rate = 50
z_up = 0 
z_down = -0.75

async def main():
    try:
        machine = None 

        print("---------------------------------- get our files ...")
        segments = scale_and_process_svg("svg/test_files/rhino.svg", machine_extents, 0.25)
        print(F"SVG has {len(segments)} segments...")

        # raise Exception("bail")

        osap = OSAP("py-printer")
        loop = asyncio.get_event_loop()
        loop.create_task(osap.runtime.run())

        usbserial_links = AutoUSBPorts().ports
        for usbserial in usbserial_links:
            osap.link(usbserial)

        await asyncio.sleep(0.25)

        # parser load seems to take some # of ms, so we load it before networks become important 
        # ... clip 21500, seems like where the fuckups start... 
        # parser = GCodeParser("test_files/3DBenchy_Top.gcode")

        print("---------------------------------- collect system ...")

        system_map = await osap.netrunner.update_map()
        system_map.print()

        print("---------------------------------- wait for clocks to settle ...")
        await osap.netrunner.await_time_settle(print_updates=True)

        print("---------------------------------- machine setup ...")
        machine = SketchyMachineMotion(osap, system_interpolation_interval, system_twin_to_real_ms, extents = machine_extents)
        await machine.begin()

        print("---------------------------------- homing ...")
        await machine.home() 

        await machine.tour_extents() 

        for s, segment in enumerate(segments):
            # jog 2 above 1st pt 
            first_pt = segment[0] 
            xyz = [*first_pt, z_up]
            await machine.queue_planner.goto_via_queue(xyz, jog_rate)

            # draw seg 
            for pt in segment:
                xyz = [*pt, z_down]
                await machine.queue_planner.goto_via_queue(xyz, draw_rate)

            # lift at last pt 
            last_pt = segment[-1]
            xyz = [*last_pt, z_up]
            await machine.queue_planner.goto_via_queue(xyz, jog_rate)

        print("Flush...")
        await machine.queue_planner.flush_queue()

        await machine.queue_planner.goto_and_await([0,0,0], 100)

        print("---------------------------------- END of main()")


    except Exception as err:
        # should be able to get more info... 
        # https://stackoverflow.com/questions/3702675/catch-and-print-full-python-exception-traceback-without-halting-exiting-the-prog 
        print("ERROR:")
        print(err)
        print(traceback.format_exc())

    finally: 
        print("---------------------------------- Finally: attempting shutdown...")
        if machine is not None:
            await machine.shutdown() 
        print("----------------------------------  shutdown OK")


# async def run():
#     await asyncio.gather(osap.runtime.run(), main())

if __name__ == "__main__":
    asyncio.run(main())


# make maxl 
# maxl = MAXL(osap, MAXLConfig(
#     axes = ['X', 'Y', 'Z', 'E'],
#     # actuators = [None, None, None, None, None],
#     actuators = [motor_xy_left, motor_xy_right, None, None, None],
#     # actuators = [None, None, motor_z_front_left, motor_z_front_right, motor_z_back],
#     # actuators = [motor_xy_left, motor_xy_right, motor_z_front_left, motor_z_front_right, motor_z_back],
#     # actuator_currents = [0.3, 0.3, 0.5, 0.5, 0.5], 
#     actuator_currents = [0.0, 0.0, 0.5, 0.5, 0.5], 
#     transform_axes_2_actuators = transform_forwards,
#     transform_actuators_2_axes = transform_backwards,
#     interpolation_interval = MAXLInterpolationIntervals.INTERVAL_08192, 
#     twin_to_real_gap_ms = 100,
#     max_accels = [1000, 1000, 500],
#     max_vels = [100, 100, 50],
#     junction_deviation = 0.5,
#     e_max_mmps = 1 / cross_section_of_1p75_filament,
#     e_motor = motor_e, 
#     print_point_transmits = False  
# ))

