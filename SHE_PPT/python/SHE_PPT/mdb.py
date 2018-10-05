""" @file full_mdb.py

    Created 15 Feb 2018

    Functions to get needed information from the MDB.
"""

# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

from MdbUtils.Mdb import Mdb as _Mdb

from SHE_PPT.file_io import find_file

_not_inited_exception = RuntimeError(
    "mdb module must be initialised with MDB xml object before use.")

full_mdb = {}


def init(mdb_files, path=None):
    """Initialises module by loading MDB data from file(s).

    Arguments
    ---------
    mdb_files: string or list of strings
        MDB filename(s)

    Return
    ------
    None

    """

    # Resolve the filename (or list of files) to find their qualified paths
    if isinstance(mdb_files, str):
        qualified_mdb_files = find_file(mdb_files, path)
    elif isinstance(mdb_files, list) or isinstance(object, tuple):
        qualified_mdb_files = []
        for mdb_file in mdb_files:
            qualified_mdb_file = find_file(mdb_file, path)
            qualified_mdb_files.append(qualified_mdb_file)

    # Get and store the data in a dictionary
    full_dict = _Mdb(qualified_mdb_files).get_all()
    full_mdb.clear()
    full_mdb.update(full_dict)

    return


def reset():
    """Resets the MDB dictionary.

    Arguments
    ---------
    None

    Return
    ------
    None
    """

    full_mdb.clear()


def get_mdb_value(key):
    """Gets an item's value from the MDB from its key (aka title).

    Arguments
    ---------
    key: str
        key for this item in the MDB

    Return
    ------
    value: (type dependent on key)

    """

    if len(full_mdb) == 0:
        raise _not_inited_exception

    return full_mdb[key]['Value']


def get_mdb_description(key):
    """Gets an item's description from the MDB from its key (aka title).

    Arguments
    ---------
    key: str
        key for this item in the MDB

    Return
    ------
    description: str

    """

    if len(full_mdb) == 0:
        raise _not_inited_exception

    return full_mdb[key]['Description']


def get_mdb_source(key):
    """Gets an item's source from the MDB from its key (aka title).

    Arguments
    ---------
    key: str
        key for this item in the MDB

    Return
    ------
    source: str

    """

    if len(full_mdb) == 0:
        raise _not_inited_exception

    return full_mdb[key]['Source']


def get_mdb_release(key):
    """Gets an item's release version from the MDB from its key (aka title).

    Arguments
    ---------
    key: str
        key for this item in the MDB

    Return
    ------
    release: str

    """

    if len(full_mdb) == 0:
        raise _not_inited_exception

    return full_mdb[key]['Release']


def get_mdb_expression(key):
    """Gets an item's expression from the MDB from its key (aka title).

    Arguments
    ---------
    key: str
        key for this item in the MDB

    Return
    ------
    expression: str

    """

    if len(full_mdb) == 0:
        raise _not_inited_exception

    return full_mdb[key]['Expression']


def get_mdb_unit(key):
    """Gets an item's unit from the MDB from its key (aka title).

    Arguments
    ---------
    key: str
        key for this item in the MDB

    Return
    ------
    unit: str

    """

    if len(full_mdb) == 0:
        raise _not_inited_exception

    return full_mdb[key]['unit']


# MDB keys stored as attributes of the mdb_keys object

class MDBKeys(object):

    def __init__(self):

        # Environmental constants

        self.VelocityOfLightConstantVacuum = "Environment.Constant.VelocityOfLightConstantVacuum"
        self.AstronomicalUnit2Meter = "Environment.Constant.AstronomicalUnit2Meter"
        self.Day2Second = "Environment.Constant.Day2Second"
        self.Degree2Radian = "Environment.Constant.Degree2Radian"

        # SpaceSegment.PLM

        self.TelescopeVISFoVCentreXscNominal = "TelescopeVISFoVCentreXscNominal"
        self.TelescopeVISFoVCentreYscNominal = "TelescopeVISFoVCentreYscNominal"
        self.TelescopeVISFOVXsc = "TelescopeVISFOVXsc"
        self.TelescopeVISFOVYsc = "TelescopeVISFOVYsc"
        self.TelescopeVISLocalFocalLengthCentre = "TelescopeVISLocalFocalLengthCentre"
        self.TelescopeVISParaxialFocalRatio = "TelescopeVISParaxialFocalRatio"
        self.TelescopeVISPlatescale = "TelescopeVISPlatescale"
        self.TelescopeVISPSFEllipticity = "TelescopeVISPSFEllipticity"
        self.TelescopeVISPSFEllipticityStability = "TelescopeVISPSFEllipticityStability"
        self.TelescopeVISPSFFWHM = "TelescopeVISPSFFWHM"
        self.TelescopeVISPSFLambdaParameterAlpha = "TelescopeVISPSFLambdaParameterAlpha"
        self.TelescopeVISPSFR2 = "TelescopeVISPSFR2"
        self.TelescopeVISPSFR2Stability = "TelescopeVISPSFR2Stability"

        #   SpaceSegment.SVM

        self.DitherStepAngularError = "DitherStepAngularError"
        self.DitherStepAngularMinimum = "DitherStepAngularMinimum"
        self.MaxField2FieldOverlap = "MaxField2FieldOverlap"
        self.MinField2FieldOverlap = "MinField2FieldOverlap"
        self.NominalScienceObservationSequenceDuration = "MinField2FieldOverlap"

        # SpaceSegment.Instrument.VIS

        self.ShutterClosingDuration = "ShutterClosingDuration"
        self.ShutterOpeningDuration = "ShutterOpeningDuration"
        self.VISADCDynamics = "VISADCDynamics"
        self.CUUniformityMapNormalised = "CUUniformityMapNormalised"
        self.VISAveragePixelSizemicron = "VISAveragePixelSizemicron"
        self.VISCCDChargeInjection = "VISCCDChargeInjection"
        self.VISCCDColumn = "VISCCDColumn"
        self.VISCCDDefectsColumnEOL = "VISCCDDefectsColumnEOL"
        self.VISCCDDefectsTotalSpotsEOL = "VISCCDDefectsTotalSpotsEOL"
        self.VISCCDDefectsTrapsEOL = "VISCCDDefectsTrapsEOL"
        self.VISCCDDefectsWhiteSpotsBOL = "VISCCDDefectsWhiteSpotsBOL"
        self.VISCCDDefectsWhiteSpotsEOL = "VISCCDDefectsWhiteSpotsEOL"
        self.VISCCDGapLongDimensionNominalImage = "VISCCDGapLongDimensionNominalImage"
        self.VISCCDGapShortDimensionNominalImage = "VISCCDGapShortDimensionNominalImage"
        self.VISCCDNumber = "VISCCDNumber"
        self.VISCCDQuadrantList = "VISCCDQuadrantList"
        self.VISCCDRow = "VISCCDRow"
        self.VISDarkCurrent = "VISDarkCurrent"
        self.VISDataCompression = "VISDataCompression"
        self.VISDetectorActivePixelLongDimensionFormat = "VISDetectorActivePixelLongDimensionFormat"
        self.VISDetectorActivePixelShortDimensionFormat = "VISDetectorActivePixelShortDimensionFormat"
        self.VISDetectorOverscanx = "VISDetectorOverscanx"
        self.VISDetectorPixelLongDimensionFormat = "VISDetectorPixelLongDimensionFormat"
        self.VISDetectorPrescanx = "VISDetectorPrescanx"
        self.VISExposureTime = "VISExposureTime"
        self.VISExposureTimeKnowledgeError = "VISExposureTimeKnowledgeError"
        self.VISFocalPlaneAssemblyLongDimensionMaxImage = "VISFocalPlaneAssemblyLongDimensionMaxImage"
        self.VISFocalPlaneAssemblyShortDimensionMaxImage = "VISFocalPlaneAssemblyShortDimensionMaxImage"
        self.VISGain = "VISGain"
        self.VISReadoutNoise = "VISReadoutNoise"
        self.VISDistortionMaps = "VISDistortionMaps"
        self.CTIParallelAcsMode = "CTIParallelAcsMode"
        self.CTIParallelClockingMode = "CTIParallelClockingMode"
        self.CTIParallelExpress = "CTIParallelExpress"
        self.CTIParallelNIterations = "CTIParallelNIterations"
        self.CTIParallelNLevels = "CTIParallelNLevels"
        self.CTIParallelNSpecies = "CTIParallelNSpecies"
        self.CTIParallelReadOutOffset = "CTIParallelReadOutOffset"
        self.CTIParallelTrapDensity = "CTIParallelTrapDensity"
        self.CTIParallelTrapLifeTime = "CTIParallelTrapLifeTime"
        self.CTIParallelWellDepth = "CTIParallelWellDepth"
        self.CTIParallelWellFillPower = "CTIParallelWellFillPower"
        self.CTIParallelWellNotchDepth = "CTIParallelWellNotchDepth"
        self.CTISerialAcsMode = "CTISerialAcsMode"
        self.CTISerialClockingMode = "CTISerialClockingMode"
        self.CTISerialExpress = "CTISerialExpress"
        self.CTISerialNIterations = "CTISerialNIterations"
        self.CTISerialNLevels = "CTISerialNLevels"
        self.CTISerialNSpecies = "CTISerialNSpecies"
        self.CTISerialReadOutOffset = "CTISerialReadOutOffset"
        self.CTISerialTrapDensity = "CTISerialTrapDensity"
        self.CTISerialTrapLifeTime = "CTISerialTrapLifeTime"
        self.CTISerialWellDepth = "CTISerialWellDepth"
        self.CTISerialWellFillPower = "CTISerialWellFillPower"
        self.CTISerialWellNotchDepth = "CTISerialWellNotchDepth"
        self.FWHMInt0 = "FWHMInt0"
        self.FWHMxaInt1x = "FWHMxaInt1x"
        self.FWHMxalambda1x = "FWHMxalambda1x"
        self.FWHMxbInt1x = "FWHMxbInt1x"
        self.FWHMxblambda1x = "FWHMxblambda1x"
        self.FWHMyaInt1y = "FWHMyaInt1y"
        self.FWHMyalambda1y = "FWHMyalambda1y"
        self.FWHMybInt1y = "FWHMybInt1y"
        self.FWHMyblambda1y = "FWHMyblambda1y"
        self.GhostModel = "GhostModel"
        self.GhostModelPositionMatrixA = "GhostModelPositionMatrixA"
        self.GhostModelPositionMatrixB = "GhostModelPositionMatrixB"
        self.GhostModelShiftX = "GhostModelShiftX"
        self.GhostModelShiftY = "GhostModelShiftY"
        self.GhostModelStarBrightness = "GhostModelStarBrightness"
        self.MeanDetectorQuantumEfficiencyCBENominalEOL = "MeanDetectorQuantumEfficiencyCBENominalEOL"
        self.NL_P1 = "NL_P1"
        self.NL_P2 = "NL_P2"
        self.NL_P3 = "NL_P3"
        self.NLFWC = "NLFWC"
        self.CCDFullWellCapacityEOL = "CCDFullWellCapacityEOL"
        self.DistortionModel = "DistortionModel"
        self.VISOpticsAOCSPixelDetectorPSF = "VISOpticsAOCSPixelDetectorPSF"
        self.PRNU = "PRNU"


mdb_keys = MDBKeys()
