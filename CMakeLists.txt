CMAKE_MINIMUM_REQUIRED(VERSION 2.8.5)

#---------------------------------------------------------------
# Load macros and functions for Elements-based projects
find_package(ElementsProject)
#---------------------------------------------------------------

# Declare project name and version

elements_project(SHE_PPT 8.7 USE Elements 5.10.0 ST_DataModelBindings 8.0.3 ST_DataModelTools 8.0.3)
