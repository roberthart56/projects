import svgpathtools
import numpy as np

def move_path(path, x_offset, y_offset):
    """
    Translates a path by a given (x, y) vector.
    
    Args:
        path (svgpathtools.Path): The path to translate.
        x_offset (float): The distance to move along the x-axis.
        y_offset (float): The distance to move along the y-axis.
        
    Returns:
        svgpathtools.Path: The translated path.
    """
    moved_segments = []
    
    translation_vector = complex(x_offset, y_offset)
    
    for segment in path:
        moved_segment = segment.translated(translation_vector)
        moved_segments.append(moved_segment)
    
    return svgpathtools.Path(*moved_segments)

def move_all_paths(paths, x_offset, y_offset):
    """
    Translates all paths in an SVG by a given (x, y) vector.
    
    Args:
        paths (list of svgpathtools.Path): The list of paths to translate.
        x_offset (float): The distance to move along the x-axis.
        y_offset (float): The distance to move along the y-axis.
        
    Returns:
        list of svgpathtools.Path: The list of translated paths.
    """

    print(F"Moving all by {x_offset, y_offset}")

    moved_paths = []
    
    for path in paths:
        moved_path = move_path(path, x_offset, y_offset)
        moved_paths.append(moved_path)
    
    return moved_paths


def scale_path(path, scale_factor):
    scaled_segments = []
    
    for segment in path:
        segment = segment.scaled(scale_factor, scale_factor)
        scaled_segments.append(segment)

    return scaled_segments


def approximate_path_to_segments(path, precision=1.0):
    segments = []
    
    for segment in path:
        if isinstance(segment, svgpathtools.Line):
            # Directly append start and end points of the line
            segments.append([segment.start.real, segment.start.imag])
            segments.append([segment.end.real, segment.end.imag])
        
        elif isinstance(segment, svgpathtools.Arc):
            # Approximate arc with line segments
            arc_length = segment.length()
            num_segments = max(2, int(arc_length / precision))
            points = [segment.point(i / num_segments) for i in range(num_segments + 1)]
            segments.extend([point.real, point.imag] for point in points)
        
        else:
            # For any other segment type (CubicBezier, QuadraticBezier), approximate with line segments
            length = segment.length()
            num_segments = max(2, int(length / precision))
            points = [segment.point(i / num_segments) for i in range(num_segments + 1)]
            segments.extend([point.real, point.imag] for point in points)

    return segments


def scale_and_process_svg(svg_file, bounding_box, precision=1.0):
    paths, attributes = svgpathtools.svg2paths(svg_file)

    # Calculate current bounding box of the SVG
    x_min, x_max, y_min, y_max = svgpathtools.path.Path(*paths).bbox()
    print(F"File has: min, max x {x_min:.2f}, {x_max:.2f} ... min, max y {y_min:.2f} {y_max:.2f}")

    # let's move 'em all to 0, 0
    paths = move_all_paths(paths, -x_min, -y_min)

    # should be all 0,0 based ... 
    x_min, x_max, y_min, y_max = svgpathtools.path.Path(*paths).bbox()
    print(F"Now: min, max x {x_min:.2f}, {x_max:.2f} ... min, max y {y_min:.2f} {y_max:.2f}")

    # and then scale everything to pinch w/in the bounding box: 
    # Target bounding box
    target_width, target_height = bounding_box
    
    # Calculate scaling factor
    scale_factor = min(target_width / x_max, target_height / y_max)
    print(F"Scaling by {scale_factor:.3f}")

    all_segments = []
    
    # Scale and then segment each path
    for path in paths:
        scaled_path = scale_path(path, scale_factor)
        segments = approximate_path_to_segments(scaled_path, precision)
        all_segments.append(segments)

    return all_segments


if __name__ == "__main__":
    # Example usage
    svg_file = "test_files/shapes.svg"  # Replace with your SVG file path
    precision = 1.0  # 1mm precision
    points_lists = scale_and_process_svg(svg_file, (100, 100), precision)

    # Output the lists of points
    for i, points in enumerate(points_lists):
        print(f"Path {i}", points)
