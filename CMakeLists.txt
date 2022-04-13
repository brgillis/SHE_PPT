CMAKE_MINIMUM_REQUIRED(VERSION 2.8.5)

#---------------------------------------------------------------
# Load macros and functions for Elements-based projects
find_package(ElementsProject)
#---------------------------------------------------------------

# Declare project name and version

elements_project(SHE_PPT 9.1 USE ST_DataModel 9.0.0
                                 ST_DataModelTools 9.0.0
                                 EL_Utils 1.2.0)
