[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/nalivayev/florentine_abbot/blob/master/README.md)
[![ru](https://img.shields.io/badge/lang-ru-yellow.svg)](https://github.com/nalivayev/florentine_abbot/blob/master/README.ru.md)

A set of utilities designed to automate the scanning process using [VueScan](https://www.hamrick.com) by Ed Hamrick

Includes:

calculate_dpi.py - a utility to calculate the optimal scanning mode based on raw photo data

run_workflow.py - a utility that runs a simulated workflow for VueScan based on previously saved program settings

The settings use templates

Template format:

`{<n>[:l[:a[:p]]]}`

Where:

n - name of the value  
l - total length  
a - alignment  
p - placeholder character  

Template format example:

`{digitization_year:8:>:0}`

List of templates that can be used in *.ini files:

user_name - operating system user name  
digitization_year - year of digitization extracted from EXIF  
digitization_month - month of digitization extracted from EXIF  
digitization_day - day of digitization extracted from EXIF  
digitization_hour - hour of digitization extracted from EXIF  
digitization_minute - minute of digitization extracted from EXIF  
digitization_second - second of digitization extracted from EXIF
