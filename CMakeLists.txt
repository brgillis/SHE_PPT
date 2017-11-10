CMAKE_MINIMUM_REQUIRED(VERSION 2.8.5)

#---------------------------------------------------------------
# Load macros and functions for Elements-based projects
find_package(ElementsProject)
#---------------------------------------------------------------

# Declare project name and version

# FIXME - Temporary workaround of bug in old versions of Elements. Have to
# use version 1.0 to avoid a spurious build error
elements_project(SHE_PPT 1.0 USE Elements 4.0 )
