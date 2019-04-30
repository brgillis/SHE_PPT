CMAKE_MINIMUM_REQUIRED(VERSION 2.8.5)

#---------------------------------------------------------------
# Load macros and functions for Elements-based projects
find_package(ElementsProject)
#---------------------------------------------------------------

# Declare project name and version

elements_project(SHE_PPT 0.9 USE Elements 5.2.2 EuclidDmBindings 2.2.3 DMTools 2.2.3 MDBTools 2.2.3
                 CT_TestDataManager 1.0)
