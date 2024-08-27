from typing import List 
from jinja2 import Template

from osap.bootstrap.metaprog.module_author import MetaModuleInstance 

template_text = """
import asyncio 
from osap.bootstrap.auto_usb_serial.auto_usb_serial import AutoUSBPorts 
from osap.osap import OSAP 

{% for instance in instance_set %}from modules.{{ instance.file_name }} import {{ instance.class_name }}
{% endfor %}

osap = OSAP("auto_modules_main")

ports = AutoUSBPorts().ports 
for port in ports:
    osap.link(port) 

async def main():
    # collect an image of the system 
    system_map = await osap.netrunner.update_map() 
    system_map.print() 


    # instantiate each of our modules, 
    {% for instance in instances %}{{ instance.instance_py_name }} = {{ instance.class_name }}(osap, "{{ instance.instance_name }}")
    {% endfor %}
    
    # and set each up, 
    {% for instance in instances %}await {{ instance.instance_py_name }}.begin()
    {% endfor %}

async def run():
    await asyncio.gather(osap.runtime.run(), main())

asyncio.run(run())

""".strip() 

def write_main_boilerplate(instances: List[MetaModuleInstance]):
    template = Template(template_text)

    class_name_set = [] 
    instance_set = [] 
    for instance in instances:
        if instance.class_name in class_name_set:
            continue 
        class_name_set.append(instance.class_name)
        instance_set.append(instance) 

    return template.render(instances=instances, instance_set=instance_set) 