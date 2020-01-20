CMAKE_MINIMUM_REQUIRED(VERSION 2.8.5)

#---------------------------------------------------------------
# Load macros and functions for Elements-based projects
find_package(ElementsProject)
#---------------------------------------------------------------

# Declare project name and version

elements_project(SHE_PPT 1.3 USE Elements 5.8 ST_DataModelBindings 7.0.0 ST_DataModelTools 7.0.2)
