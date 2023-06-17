"""Hops default HTTP server swith rhinoinside example"""
import sys
import os
import rhinoinside

# load ghhops-server-py source from this directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import ghhops_server as hs


rhinoinside.load()
# System and Rhino can only be loaded after rhinoinside is initialized
import System  # noqa
import Rhino  # noqa

hops = hs.Hops(app=rhinoinside)

"""
██████╗ ██████╗ ██╗██████╗  ██████╗ ███████╗
██╔══██╗██╔══██╗██║██╔══██╗██╔════╝ ██╔════╝
██████╔╝██████╔╝██║██║  ██║██║  ███╗█████╗  
██╔══██╗██╔══██╗██║██║  ██║██║   ██║██╔══╝  
██████╔╝██║  ██║██║██████╔╝╚██████╔╝███████╗
╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝ ╚══════╝
                                            
██████╗  █████╗ ██████╗ ████████╗    ██╗██╗ 
██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝    ██║██║ 
██████╔╝███████║██████╔╝   ██║       ██║██║ 
██╔═══╝ ██╔══██║██╔══██╗   ██║       ██║██║ 
██║     ██║  ██║██║  ██║   ██║       ██║██║ 
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝╚═╝ 
""" 
import Rhino
import math
import scriptcontext
import rhinoscriptsyntax as rs

def create_cylinder_bridge(length, width, height, divisions, pillar_radius, beam_radius, road_thickness, railing_height, railing_thickness):
    # Calculate division length
    div_length = length / divisions
    
    # Initialize list for bridge components
    bridge = []
    
    # Create cylinders for the bridge
    for i in range(divisions):
        x = i * div_length
        base_point = Rhino.Geometry.Point3d(x, width/2, 0)
        
        # Create cylinder
        base_circle = Rhino.Geometry.Circle(base_point, pillar_radius)
        cylinder = Rhino.Geometry.Cylinder(base_circle, height)
        
        # Add cylinder to bridge
        bridge.append(cylinder.ToBrep(True, True))

        # If it's not the first or last division, create the beam between pillars
        if i > 0:
            start_point = Rhino.Geometry.Point3d(x - div_length, width/2, height)
            end_point = Rhino.Geometry.Point3d(x, width/2, height)
            line = Rhino.Geometry.Line(start_point, end_point)

            # Calculate midpoint of the line
            midpoint = Rhino.Geometry.Point3d((start_point.X + end_point.X) / 2, (start_point.Y + end_point.Y) / 2, (start_point.Z + end_point.Z) / 2)

            beam = Rhino.Geometry.Cylinder(Rhino.Geometry.Circle(midpoint, beam_radius), line.Length)
            
            # Add beam to bridge
            bridge.append(beam.ToBrep(True, True))
    
    # Create the road on the top of the pillars
    road_height = height + road_thickness
    road_base = Rhino.Geometry.Point3d(0, 0, height)
    road_points = [
        Rhino.Geometry.Point3d(road_base[0], road_base[1], road_base[2]),
        Rhino.Geometry.Point3d(road_base[0] + length, road_base[1], road_base[2]),
        Rhino.Geometry.Point3d(road_base[0] + length, road_base[1] + width, road_base[2]),
        Rhino.Geometry.Point3d(road_base[0], road_base[1] + width, road_base[2]),
        Rhino.Geometry.Point3d(road_base[0], road_base[1], road_base[2] + road_thickness),
        Rhino.Geometry.Point3d(road_base[0] + length, road_base[1], road_base[2] + road_thickness),
        Rhino.Geometry.Point3d(road_base[0] + length, road_base[1] + width, road_base[2] + road_thickness),
        Rhino.Geometry.Point3d(road_base[0], road_base[1] + width, road_base[2] + road_thickness),
    ]

    # Create road
    road = Rhino.Geometry.Brep.CreateFromBox(road_points)
    
    # Add road to bridge
    bridge.append(road)

    # Create railings
    railing_base_height = height + road_thickness
    railing_top_height = railing_base_height + railing_height

    # Left railing
    left_railing_start = Rhino.Geometry.Point3d(0, railing_thickness / 2, railing_base_height)
    left_railing_end = Rhino.Geometry.Point3d(length, railing_thickness / 2, railing_base_height)
    left_railing_line = Rhino.Geometry.Line(left_railing_start, left_railing_end)
    left_railing_midpoint = left_railing_line.PointAt(0.5)
    left_railing = Rhino.Geometry.Cylinder(Rhino.Geometry.Circle(left_railing_midpoint, railing_thickness / 2), railing_height)
    bridge.append(left_railing.ToBrep(True, True))
    
    # Right railing
    right_railing_start = Rhino.Geometry.Point3d(0, width - railing_thickness / 2, railing_base_height)
    right_railing_end = Rhino.Geometry.Point3d(length, width - railing_thickness / 2, railing_base_height)
    right_railing_line = Rhino.Geometry.Line(right_railing_start, right_railing_end)
    right_railing_midpoint = right_railing_line.PointAt(0.5)
    right_railing = Rhino.Geometry.Cylinder(Rhino.Geometry.Circle(right_railing_midpoint, railing_thickness / 2), railing_height)
    bridge.append(right_railing.ToBrep(True, True))

    # Define number of railing segments
    railing_segments = 10
    
    # Calculate the length of each segment
    segment_length = length / railing_segments
    
    # Create railings
    for i in range(railing_segments):
        x = i * segment_length
        
        # Left railing
        left_railing_start = Rhino.Geometry.Point3d(x, railing_thickness / 2, railing_base_height)
        left_railing_end = Rhino.Geometry.Point3d(x + segment_length, railing_thickness / 2, railing_base_height)
        left_railing_line = Rhino.Geometry.Line(left_railing_start, left_railing_end)
        left_railing_midpoint = left_railing_line.PointAt(0.5)
        left_railing = Rhino.Geometry.Cylinder(Rhino.Geometry.Circle(left_railing_midpoint, railing_thickness / 2), railing_height)
        bridge.append(left_railing.ToBrep(True, True))
        
        # Right railing
        right_railing_start = Rhino.Geometry.Point3d(x, width - railing_thickness / 2, railing_base_height)
        right_railing_end = Rhino.Geometry.Point3d(x + segment_length, width - railing_thickness / 2, railing_base_height)
        right_railing_line = Rhino.Geometry.Line(right_railing_start, right_railing_end)
        right_railing_midpoint = right_railing_line.PointAt(0.5)
        right_railing = Rhino.Geometry.Cylinder(Rhino.Geometry.Circle(right_railing_midpoint, railing_thickness / 2), railing_height)
        bridge.append(right_railing.ToBrep(True, True))

    import numpy as np
    
    # Create catenary arch cables
    for i in range(divisions - 1):
        x_start = i * div_length
        x_end = (i + 1) * div_length
    
        start_point = Rhino.Geometry.Point3d(x_start, width / 2, height + road_thickness)
        end_point = Rhino.Geometry.Point3d(x_end, width / 2, height + road_thickness)
    
        # Define the catenary scale (adjust this to get desired catenary shape)
        a = 5  # arbitrary value
    
        # Define number of points for each catenary
        num_points = 100
    
        # Create the points for the catenary curve
        x_values = np.linspace(x_start, x_end, num_points)
        y_values = a * np.cosh((x_values - (x_start + x_end) / 2) / a) - a + height + road_thickness
        catenary_points = [Rhino.Geometry.Point3d(x, width / 2, y) for x, y in zip(x_values, y_values)]
    
        # Create the catenary curve
        catenary_curve = Rhino.Geometry.Curve.CreateInterpolatedCurve(catenary_points, 3)
    
        # Add curve to bridge
        bridge.append(catenary_curve.ToNurbsCurve())

    # Return bridge components
    return bridge

# Create a cylinder bridge with railings
bridge = create_cylinder_bridge(length, width, height, divisions, pillar_radius, beam_radius, road_thickness, railing_height, railing_thickness)

# Output the bridge
a = bridge




if __name__ == "__main__":
    hops.start(debug=True)