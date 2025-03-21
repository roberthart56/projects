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

from modules.vvelocity_motion import VVelocityMachineMotion

system_interpolation_interval = MAXLInterpolationIntervals.INTERVAL_16384
system_twin_to_real_ms = 200

machine_extents = [260, 180]
# rates are: 100 for clean drawings, 500 for speed, 1500 for ludicrous 
draw_rate = 1000
jog_rate = draw_rate
z_up = 0
z_down = 1

async def main():
    try:
        machine = None 

        print("---------------------------------- get our files ...")
        segments = scale_and_process_svg("svg/test_files/dragon_curved.svg", machine_extents, 0.1)
        print(F"SVG has {len(segments)} segments...")

        # raise Exception("bail")

        osap = OSAP("py-printer")
        loop = asyncio.get_event_loop()
        loop.create_task(osap.runtime.run())

        usbserial_links = AutoUSBPorts().ports
        for usbserial in usbserial_links:
            osap.link(usbserial)

        await asyncio.sleep(0.25)

        print("---------------------------------- collect system ...")
        system_map = await osap.netrunner.update_map()
        system_map.print()

        print("---------------------------------- wait for clocks to settle ...")
        await osap.netrunner.await_time_settle(print_updates=True)

        print("---------------------------------- machine setup ...")
        machine = VVelocityMachineMotion(osap, system_interpolation_interval, system_twin_to_real_ms, extents = machine_extents)
        await machine.begin()

        await asyncio.sleep(1)

        # tour_rate = 100000
        # tour_span = 100
        # tour_count = 20 

        # for _ in range(tour_count):
        #    await machine.queue_planner.goto_via_queue([0,0,0], tour_rate)
        #    await machine.queue_planner.goto_via_queue([tour_span,0,0], tour_rate)
        #    await machine.queue_planner.goto_via_queue([tour_span,tour_span,0], tour_rate)
        #    await machine.queue_planner.goto_via_queue([0,tour_span,0], tour_rate)

        # await machine.queue_planner.goto_and_await([0,0,0], tour_rate)

        # raise Exception("bail")

        # await machine.queue_planner.flush_queue()

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

        # await machine.queue_planner.goto_and_await([0,0,0], 100)

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

