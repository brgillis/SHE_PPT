CMAKE_MINIMUM_REQUIRED(VERSION 2.8.5)

#---------------------------------------------------------------
# Load macros and functions for Elements-based projects
find_package(ElementsProject)
#---------------------------------------------------------------

# Declare project name and version

elements_project(SHE_PPT 8.8.4 USE ST_DataModelBindings 8.0.5 ST_DataModelTools 8.0.5 EL_Utils 1.1.0)
