from dataclasses import dataclass 
from typing import Union

@dataclass 
class GCodeLine:
    line_num: int
    x: float 
    y: float 
    z: float 
    e_delta: float 
    target_velocity: float 

class ArgsDict:
    def __init__(self, d):
        self.d = d

    def get_float(self, item):
        if item in self.d:
            return float(self.d[item])
        else:
            return None

    def __str__(self):
        return f"ArgsDict({self.d})"


class GCodeParser:
    def __init__(self, filename):
        with open(filename, "r") as f:
            self.content = f.read()

        self.i_line = 0
        self.lines = self.content.splitlines(keepends = False)

        self.position = [0.0, 0.0, 0.0]
        self.target_velocity = 0 
        self.e_last = 0 

    def set_current_position(self, position):
        self.position = position 

    def get_next_line(self) -> Union[GCodeLine, None]:
        for _ in range(len(self.lines) - self.i_line):
            line = self.lines[self.i_line]
            self.i_line += 1 

            if len(line) == 0 or line[0] == ";":
                continue

            items = line.split(" ")

            cmd = items[0]
            d = ArgsDict({x[0]: x[1:] for x in items[1:]})

            match cmd:
                case "G1":
                    motion_axes = [d.get_float("X"), d.get_float("Y"), d.get_float("Z")]
                    e = d.get_float("E")
                    f = d.get_float("F")
                    delta_e = 0 

                    for a, axis in enumerate(motion_axes):
                        if axis is not None:
                            self.position[a] = axis 

                    if f is not None:
                        self.target_velocity = f

                    if e is not None:
                        # extruding move
                        delta_e = e - self.e_last
                        self.e_last = e

                    return GCodeLine(
                        line_num = self.i_line - 1, 
                        x = self.position[0],
                        y = self.position[1],
                        z = self.position[2],
                        e_delta = delta_e, 
                        target_velocity = self.target_velocity 
                    )

                case "G92":
                    e = d.get_float("E")
                    if e is not None:
                        self.e_last = d.get_float("E")

                case _:
                    continue 

        # EOF: 
        return None 