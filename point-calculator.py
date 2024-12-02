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
from qgis.core import (
    QgsPointXY,
    QgsFeature,
    QgsGeometry,
    QgsVectorLayer,
    QgsProject
)
from qgis.gui import QgsMapToolEmitPoint

# Handle user input and pass coordinates to point calculator
class PointTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, callback_function):
        super().__init__(canvas)
        self.canvas = canvas
        self.callback_function = callback_function

    def canvasReleaseEvent(self, event):
        point = self.toMapCoordinates(event.pos())
        self.callback_function(point)

class Parcel:
    def __init__(self, canvas):
        self.canvas = canvas
        self.points = []  # Property corners as (northing, easting) tuples
        self.point_tool = PointTool(self.canvas, self.point_calculator)
        self.layer = None  # To store the plot layer

    def start_point_selection(self):  # Set up point selection tool
        self.canvas.setMapTool(self.point_tool)

    def point_calculator(self, point: QgsPointXY):
        print(f"Selected point: {point.x()}, {point.y()}")
        
        # Define initial coordinates from selected point
        begin_northing = point.y()
        begin_easting = point.x()
        self.points = [(begin_northing, begin_easting)]  # Reset points list

        # Open course schedule as plaintext .csv
        # Format: quadrant, degrees, minutes, seconds, distance
        with open("C:\\Users\\Arthur\\NewProject\\Deeds\\PA_Chester\\4405-735\\PA_Chester_4405-735_Courses.txt") as course_schedule:
            print(f"Northing Easting\t\tNorthing Easting")

            # Read course schedule and calculate line-by-line
            for number_of_courses, line in enumerate(course_schedule):
                current_course = line.strip().split(',')

                # Convert bearing to radians:
                # math.radians(deg + min / 60 + sec / 3600) = (deg + min / 60 + sec / 3600) * pi / 180
                bearing_radians = math.radians(
                    int(current_course[1]) + (int(current_course[2]) / 60) + (int(current_course[3]) / 3600)
                )

                # Calculate northing (y) of end point
                distance = float(current_course[4])
                if current_course[0] in ['1', '4']:  # NE or NW
                    end_northing = begin_northing + distance * math.cos(bearing_radians)
                elif current_course[0] in ['2', '3']:  # SE or SW
                    end_northing = begin_northing - distance * math.cos(bearing_radians)
                else:
                    raise ValueError("Northing: invalid quadrant")

                # Calculate easting (x) of end point
                if current_course[0] in ['1', '2']:  # NE or SE
                    end_easting = begin_easting + distance * math.sin(bearing_radians)
                elif current_course[0] in ['3', '4']:  # SW or NW
                    end_easting = begin_easting - distance * math.sin(bearing_radians)
                else:
                    raise ValueError("Easting: invalid quadrant")

                self.points.append((end_northing, end_easting))  # Append end point

                print(f"Course {number_of_courses + 1}:\t {begin_northing:.2f}\t{begin_easting:.2f}\t\t{end_northing:.2f}\t{end_easting:.2f}".rjust(6))

                # Update the beginning point for the next course
                begin_northing = end_northing
                begin_easting = end_easting

        print(f"All points processed: {self.points}")
        self.plot_parcel()

    def plot_parcel(self):
        # Create a new vector layer for the parcel
        if self.layer is None:
            self.layer = QgsVectorLayer("LineString?crs=EPSG:4326", "Parcel Boundary", "memory")
            QgsProject.instance().addMapLayer(self.layer)
        
        provider = self.layer.dataProvider()
        feature = QgsFeature()

        # Create a geometry from the points
        geometry = QgsGeometry.fromPolylineXY([QgsPointXY(pt[1], pt[0]) for pt in self.points])
        feature.setGeometry(geometry)

        # Add the feature to the layer
        provider.addFeature(feature)
        self.layer.triggerRepaint()

    def get_points(self):
        # This method can be used to retrieve all points for further processing or drawing on the map.
        return self.points

# Example usage:
canvas = iface.mapCanvas()
parcel_instance = Parcel(canvas)
parcel_instance.start_point_selection()
