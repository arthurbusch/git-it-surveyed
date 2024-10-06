# Point Calculator
# This script calculates beginning and end points for all the courses described in a deed.
# The deed .pdf can be scanned using an OCR such as Tesseract and then tabulated.
# Copyright (C) 2024  Arthur Busch

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import math
from qgis.PyQt.QtCore import QObject
from qgis.core import QgsPointXY, QgsFeature, QgsGeometry
from qgis.gui import QgsMapToolEmitPoint

class PointTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, callback_function):
        super().__init__(canvas)
        self.canvas = iface.mapCanvas()    # Get the map canvas
        self.callback_function = callback_function

    # This method is triggered when the user clicks on the map
    def canvasReleaseEvent(self, event):
        point = self.toMapCoordinates(event.pos())  # Get the map coordinates from the event
        self.callback_function(point)  # Call the function to handle the selected point

# Main function to handle point selection
def point_calculator(point: QgsPointXY):
    print(f"Selected point: {point.x()}, {point.y()}")  # Print selected point

    # Open course schedule as plaintext .csv
    # Format: quadrant, degrees, minutes, seconds, distance
    # Replace {filepath} with your file path
    course_schedule = open("{filepath}", "r")

    # Declare variables
    begin_northing = point.x()  # Initial northing (y)
    begin_easting = point.y()   # Initial easting (x)
    points = []                 # Will contain the coordinates calculated herein
    grantors = ["James M. Kirsch", "Florence E. Kirsch"]
    grantees = ["Richard D. Busch", "Gail W. Craven"]

    print(f"""Beginning and Ending Points for the Courses and Distances Described in
Chester County, Pennsylvania\tDeed Book 4405\tPage 735\n
Grantors: {", ".join (str(grantor) for grantor in grantors)}
Grantees: {", ".join (str(grantee) for grantee in grantees)}\n
\t       Northing Easting\t\tNorthing Easting""")

    # Read course schedule and calculate line-by-line
    for number_of_courses, line in enumerate(course_schedule):
        current_course = line.split(',')
    
        current_course.append(begin_northing)   # Append initial coordinates
        current_course.append(begin_easting)    # to course being processed
    
        # Convert bearing to radians:
        # math.radians(deg + min / 60 + sec / 3600) = (deg + min / 60 + sec / 3600) * pi / 180
        bearing_radians = math.radians(int(current_course[1]) + (int(current_course[2]) / 60) + (int(current_course[3]) / 3600))
            
        # Calculate northing (y) of end point
        # Northeast or northwest (positive delta_y): y = y_0 + d cos (bearing)
        # Southeast or southwest (negative delta_y): y = y_0 - d cos (bearing)
        if current_course[0] == '1' or current_course[0] == '4':    # If NE or NW
            end_northing = begin_northing + (float(current_course[4]) * math.cos(bearing_radians))
        elif current_course[0] == '2' or current_course[0] == '3':  # If SE or SW
            end_northing = begin_northing - (float(current_course[4]) * math.cos(bearing_radians))
        else:
            print("Cannot calculate northing")

        # Calculate easting (x) of end point
        # Northeast or southeast (positive delta_x): x = x_0 + d sin (bearing)
        # Southwest or southwest (negative delta_x): x = x_0 - d sin (bearing)
        if current_course[0] == '1' or current_course[0] == '2':
        end_easting = begin_easting + (float(current_course[4]) * math.sin(bearing_radians))
        elif current_course[0] == '3' or current_course[0] == '4':
            end_easting = begin_easting - (float(current_course[4]) * math.sin(bearing_radians))
        else:
            print("Cannot calculate easting")
       
        points.append(begin_northing)   # Append initial coordinates
        points.append(begin_easting)    # to points list
            
        current_course.append(end_northing) # Append calculated coordinates
        current_course.append(end_easting)  # to course being processed
    
        print(f"Course {number_of_courses + 1}:\t {begin_northing:.2f}\t{begin_easting:.2f}\t\t{end_northing:.2f}\t{end_easting:.2f}".rjust(6))
            
        begin_northing = end_northing   # Set beginning point from which
        begin_easting = end_easting     # next course is measured
            
    points.append(end_northing) # Append calculated coordinates
    points.append(end_easting)  # to points list

point_tool = PointTool(canvas, point_calculator)
canvas.setMapTool(point_tool)   # User prompt to select point
