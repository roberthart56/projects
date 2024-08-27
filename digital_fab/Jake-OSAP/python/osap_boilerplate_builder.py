import asyncio

from typing import List 
from pathlib import Path 

from osap.osap import OSAP
from osap.bootstrap.auto_usb_serial.auto_usb_serial import AutoUSBPorts
from osap.bootstrap.metaprog.module_author import MetaModuleInstance, write_module_boilerplate
from osap.bootstrap.metaprog.main_author import write_main_boilerplate

osap = OSAP("py_system_grepper")

ports = AutoUSBPorts().ports
for port in ports:
    osap.link(port)


async def main():
    # collect devices, 
    system_map = await osap.netrunner.update_map()
    system_map.print()

    # setup dirs, 
    Path("boilerplate").mkdir(exist_ok=True)
    Path("boilerplate/modules").mkdir(exist_ok=True)

    instances: List[MetaModuleInstance] = [] 
    for runtime in system_map.runtimes:
        if runtime.protocol_build == "Python":
            continue 
        instance = await write_module_boilerplate(osap, runtime) 
        instances.append(instance)

    # now write them to file... 
    files_written = [] 
    for instance in instances:
        if instance.file_name in files_written:
            continue
        print(f"writing {instance.file_name}")
        with open(f"boilerplate/modules/{instance.file_name}.py", 'w') as file:
            file.write(instance.code)
            files_written.append(instance.file_name)

    # then we would want to write a main.py, 
    main_code = write_main_boilerplate(instances)
    print("writing main")
    with open(f"boilerplate/main.py", 'w') as file:
        file.write(main_code)

    print("... done")


async def run():
    await asyncio.gather(osap.runtime.run(), main())

asyncio.run(run())
