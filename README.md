# git-it-surveyed
A collection of Python scripts for boundary surveying applications.

* point-calculator.py:
  This script calculates coordinates of property corners from a deed.
  Bearings and distances are read from a plaintext .csv in the format quadrant, degrees, minutes, seconds, distance.
  
* PA_Chester_4405-735_Courses.txt:
  Companion file for point-calculator.py. Note: the parcel does not come close to closing.
  Make sure to change {filepath} of the course_schedule object to point to this file!
