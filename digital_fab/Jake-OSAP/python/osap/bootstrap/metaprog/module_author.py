from dataclasses import dataclass
from typing import List
import re 

from jinja2 import Template

from osap.osap import OSAP 
from osap.discovery.netrunner import MapRuntime 
from osap.presentation.rpc_caller import FunctionSignature


template_text = """
from typing import cast, Tuple 
from osap.osap import OSAP 

class {{ class_name }}:
    def __init__(self, osap: OSAP, device_name: str):
        self.device_name = device_name 
        {% for func in signatures %}self._{{ func.pythonic_name }}_rpc = osap.rpc_caller(device_name, "{{ func.name }}")
        {% endfor %}self.callers = [
            {% for func in signatures %}self._{{ func.pythonic_name }}_rpc{% if not loop.last %},
            {% endif %}{% endfor %}
        ]
        
    async def begin(self):
        for caller in self.callers:
            await caller.begin()
    {% for func in signatures %}
    async def {{ func.pythonic_name }}(self{% for arg in func.args %}, {{ arg.name }}: {{ arg.type_name_pythonic }}{% endfor %})
            {%- if func.return_types[0].type_name_pythonic == "None" -%}
            {%- elif func.return_types|length == 1 %} -> {{ func.return_types[0].type_name_pythonic }}
            {%- else -%} -> Tuple[{% for ret in func.return_types %}{{ ret.type_name_pythonic }}{{ ", " if not loop.last else "" }}{% endfor %}] {% endif %}:
        {% if func.return_types[0].type_name_pythonic == "None" -%}
        await self._{{ func.pythonic_name }}_rpc.call({% for arg in func.args %}{{ arg.name }}{% if not loop.last %}, {% endif %}{% endfor %})
        return
        {%- elif func.return_types|length == 1 -%}
        result = await self._{{ func.pythonic_name }}_rpc.call({% for arg in func.args %}{{ arg.name }}{% if not loop.last %}, {% endif %}{% endfor %})
        return cast({{ func.return_types[0].type_name_pythonic }}, result)
        {%- else -%}
        {% for ret in func.return_types -%}
            {% if ret.name == "" %}{{ ret.type_name_pythonic }}_{{ loop.index }}{% else %}{{ ret.name }}{% endif %}{{ ", " if not loop.last else "" }}
            {%- endfor %} = await self._{{ func.pythonic_name }}_rpc.call({% for arg in func.args %}{{ arg.name }}{% if not loop.last %}, {% endif %}{% endfor %}) #type: ignore
        return {% for ret in func.return_types %}cast({{ ret.type_name_pythonic }}, {% if ret.name == "" %}{{ ret.type_name_pythonic }}_{{ loop.index }}{% else %}{{ ret.name }}{% endif %}){{ ", " if not loop.last else "" }}{% endfor %}
        {% endif %}
    {% endfor %}
            
""".strip()

old_temp = """
        {%- elif func.return_types|length > 1 -%} -> Tuple[{% for ret in func.return_types %}{{ ret.type_name_pythonic }}{{ ", " if not loop.last else "" }}{% endfor %}] 
        {%- else %} -> {{ func.return_types[0].type_name_pythonic }}{% endif %}:
        {% if func.return_types[0].type_name_pythonic == "None" %}{% else %}result = {% endif %}await self._{{ func.pythonic_name }}_rpc.call({% for arg in func.args %}{{ arg.name }}{% if not loop.last %}, {% endif %}{% endfor %}){% if func.return_types[0] == "None" %}{% else %}
        return cast({{ func.return_types[0] }}, result){% endif %}
"""

def to_camel_case(name):
    # Function to capitalize words unless they contain uppercase letters
    def capitalize_if_needed(word):
        if word.islower():
            return word.capitalize()
        return word

    # Split the string by non-alphanumeric characters and handle cases with acronyms
    words = re.split(r'[^a-zA-Z0-9]', name)
    
    # Apply the capitalization function to each word
    camel_case_name = ''.join(capitalize_if_needed(word) for word in words if word)
    
    return camel_case_name

def to_snake_case(name):
    # Replace dashes with underscores
    name = name.replace('-', '_')
    # Handle the acronym at the start by not splitting if it is followed directly by lowercase
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    # Insert underscores before capital letters, but only after the first full word (including acronym)
    name = re.sub(r'(?<!^)(?<![A-Z])(?=[A-Z])', '_', name)
    # Replace any instance of double underscores with a single underscore
    name = name.replace('__', '_')
    # Convert the whole string to lowercase
    return name.lower()


@dataclass
class MetaModuleInstance:
    file_name: str 
    class_name: str 
    code: str 
    instance_name: str 
    instance_py_name: str 


async def write_module_boilerplate(osap: OSAP, device: MapRuntime):
    # dynamically build RPCCallers for each device, 
    signatures: List[FunctionSignature] = [] 

    for port in device.ports:
        if port.type_name != "rpc_implementer":
            continue 
        caller = osap.rpc_caller(device.module_name, port.name)
        await caller.begin() 
        signatures.append(caller.get_signature())

    # we have a kind of fuckup where 'string' is not the type-hint appropriate 'str' ... 
    # TODO: ... be more consistent with type name conventions and conversions ? 
    for signature in signatures:
        # for ret in signature.return_types:
        #     if ret.type_name == 'string':
        #         ret.type_name = 'str'
        #     if ret.type_name == 'void' or ret.type_name == 'none':
        #         ret.type_name = 'None'
        # for arg in signature.args:
        #     if arg.type_name == 'string':
        #         arg.type_name = 'str'
        #     if arg.type_name == 'void' or arg.type_name == 'none':
        #         # this is actually a case where we don't have proper type-serialization for the function ! 
        #         arg.type_name = 'None'
        # we also want to camel-case the python functions, 
        signature.pythonic_name = to_snake_case(signature.name)
        print('reprint', signature)

    class_name = to_camel_case(device.module_type)
    file_name = to_snake_case(device.module_type)
    py_name = to_snake_case(device.module_name)

    print("set...")
    template = Template(template_text)
    code_str = template.render(class_name=class_name, signatures=signatures)

    print("code...")
    print(code_str)

    return MetaModuleInstance(file_name, class_name, code_str, device.module_name, py_name)