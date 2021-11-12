# SGS Documentation Template
> `This, is an example of a header README.md, the aim is to briefly describe with a few sentences what the repository does.`
> `This is heavily based on what Lee did for PK-WL before he left and it was very efficient for other devs to pick up from where he left`
> `This is an easy-to-implement Markdown version of documentation. This repo also demonstrates how to make documentation which can be compiled by using 'make doc' with the Elements builder. See the files in the 'doc' folder of this project for how to set up this documentation (using the same content, but in .rst format instead of .md). You can see how that looks by cloning this project within a LODEEN environment and running 'make doc' in the root folder. This will compile the files in the 'doc' folder into .html files in the build.../doc/sphinx folder. Open 'index.html' there with your browser of choice.`

This very simple repository aims to create a template for documentation (README & DocStrings) for Euclid-SGS Projects.

## Software identification
> `Software profile should be one of "develop", "release-candidate", "release"`

* Processing Element Name: PF-SHE
* Project Name: SHE_PPT
* Profile: develop
* Version: 8.11 (08/11/2021)

## Contributors
### Active Contributors
> `Here we add names of developers who need to be informed once a merge request (MR) or pull request (PR) is made`

* Bryan Gillis (b.gillis@roe.ac.uk)
* Malte Tewes (mtewes@astro.uni-bonn.de)
* Nicholas Cross (njc@roe.ac.uk)
* Giuseppe Condego (giuseppe.congedo@ed.ac.uk)
* Gordon Gibb (gordon.gibb@ed.ac.uk)

### Other Contributors
> `Add names of past or inactive contributors that do not need to be informed of MR or PR`

* Katie Eckhard ()

## Purpose
> `Describe here in more detail what are the goals of this repository as well as the expected outputs`

This repository contains general SHE functions, classes and product definitions. Some important examples are:

1. `SHE_frame_stack`,  a class that produces an instance of the image data, the background, flag, weight, and segmentation images and tools to extract postage stamps for object lists.  
2. the `.xml` product definition and `.fits` table definition code for all SHE data products and VIS, MER and other input data products.
3. Pipeline configuration code. 

## Relevant Documents
> `Boilerplate section which links any Euclid related documents that are relevant for the project`

* [RSD](https://euclid.roe.ac.uk/attachments/download/54815)
* [SDD](https://euclid.roe.ac.uk/attachments/download/54782/EUCL-IFA-DDD-8-002.p
df)
* [VP/STS](https://euclid.roe.ac.uk/attachments/download/54785/EUCL-CEA-PL-8-001
_v1.44-Euclid-SGS-SHE-Validation_Plan_STS.pdf)
* [STP/STR](https://euclid.roe.ac.uk/attachments/download/54784/EUCL-IFA-TP-8-00
2_v1-0-0.pdf)

## Dependencies

### Internal Euclid Dependencies
> `Describe here any dependencies on Euclid projects managed by PF-SHE. Most direct dependencies should be at the top, with progressively more indirect dependencies toward the bottom, or alphabetically when otherwise equal.`
> ` Where possible, please add links to repositories or relevant gitlab codes`

N/A

### External Euclid Dependencies
> `Describe here any dependencies on Euclid projects managed outside PF-SHE. Most direct dependencies should be at the top, with progressively more indirect dependencies toward the bottom, or alphabetically when otherwise equal.`
> ` Where possible, please add links to repositories or relevant gitlab codes`

* [EL_Utils 1.1.0](https://gitlab.euclid-sgs.uk/EuclidLibs/EL_Utils)
* [ST_DataModelTools 8.0.5](https://gitlab.euclid-sgs.uk/ST-DM/ST_DataModelTools)
* [ST_DataModelBindings 8.0.5](https://gitlab.euclid-sgs.uk/ST-DM/ST_DataModelBindings)
* [ST_DataModel 8.0.5](https://gitlab.euclid-sgs.uk/ST-DM/ST_DataModel)
* [Elements 5.15](https://gitlab.euclid-sgs.uk/ST-TOOLS/Elements)
* etc

### Configuration
> `Describes the version of EDEN which this code runs on, and lists the versions of relevant packages in EDEN which are used by this project. In the case where one package depends on another (e.g. astropy depends on numpy), the dependant package should be listed first (astropy before numpy), or alphabetically when otherwise equal.`


**EDEN 2.1**
```
- astropy 3.2.1
- numpy 1.17.2
```

### Dependant Projects
> `Add here a list of all projects which depend on this project either directly or indirectly. These are the projects which will be at-risk of disruption due to changes in this project. Most direct dependants should be listed first (e.g. they call a function provided by this project), followed by more indirect dependants (e.g. they call a function provided by project B, which calls a function provided by this project), with dependants listed alphabetically when otherwise equal.`
> ` Where possible, please add links to repositories or relevant gitlab codes`

* [SHE_LensMC](https://gitlab.euclid-sgs.uk/PF-SHE/SHE_LensMC)
* [SHE_MomentsML](https://gitlab.euclid-sgs.uk/PF-SHE/SHE_MomentsML)
* [SHE_CTE](https://gitlab.euclid-sgs.uk/PF-SHE/SHE_CTE)
* [SHE_IAL_Pipelines](https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines)
* [SHE_MER]
* [SHE_PSFToolkit]
* etc

### Dependant Pipelines
> `Add here a list of all pipelines which use code from this project either directly or indirectly. These are the pipelines which will be at-risk of disruption due to changes in this project. Pipelines should be listed alphabetically.`
> ` Where possible, please add links to repositories or relevant gitlab codes`

* [SHE Analysis](https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines/-/blob/develop/SHE_Pipeline/auxdir/SHE_Shear_Analysis/PipScript_SHE_Shear_Analysis.py) 
* [Shear Calibration](https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines/-/blob/develop/SHE_Pipeline/auxdir/SHE_Shear_Calibration/PipScript_SHE_Shear_Calibration.py)
* [SHE Global Validation](https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines/-/blob/develop/SHE_Pipeline/auxdir/SHE_Global_Validation/PipDef_SHE_Global_Validation.xml)
* etc.

## Installation
> `Boilerplate section which explains how to install any Elements program. Only the repository location should be changed here for each project.`

All Euclid projects will be deployed via cvmfs. If this is installed and set up, this project will be pre-installed and no further work will be necessary. In case cvmfs isn't installed, or you wish to install an unreleased build or older build, you can do so through the following process:

```bash
cd ${HOME}/Work/Projects
git clone https://gitlab.euclid-sgs.uk/pf-she/she_myproject.git
cd she_myproject
git checkout <desired branch or tag>
make
make test
make install
```

## Main Programs Available
> `Describe here each executable Elements program provided by this project.`

* [`SHE_MyProject_GenCatPic`](#she_myproject_gencatpic): downloads the picture of a cat
* [`SHE_MyProject_ShowCatPic`](#she_myproject_showcatpic): shows the user the picture of a cat

## Running the software
> `for each of the codes described previously, the aim here is to describe each option, input, and output of the program as well as how to run it using Elements.`

### `SHE_MyProject_GenCatPic`
>`(Optional) a more careful description of what the program does`

>`Describe how one can call the program with Elements, include any necessary options with optional ones in [square brackets]. These arguments are to later be described in detail in the applicable arguments section below`

_**Running the Program on EDEN/LODEEN**_

To run the SHE_MyProject_GenCatPic processing element on Elements use the following command:
```bash
E-Run SHE_MyProject 0.1 SHE_MyProject_GenCatPic --workdir <dir> --psf_list <filename> --aux_data <filename> [--log-file <filename>] [--log-level <value>] [--pipeline_config <filename>] [--aux_data <filename>] [--cat_pic <filename>] [--use_dog] [--set_tie <value>]
```
with the following options:

**Common Elements Arguments**
>`This boilerplate section describes the standard arguments which are common to all Elements executables.`

|  **Argument**               | **Description**                                                       | **Required** | **Default** |
| :------------------------   | :-------------------------------------------------------------------- | :----------: | :----------:|
| --workdir `<path>`          | Name of the working directory, where input data is stored and output data will be created. | yes          | N/A         |
| --log-file `<filename>`     | Name of a filename to store logging data in, relative to the workdir. If not provided, logging data will only be output to the terminal. When run via the pipeline runner, this will be set to a file in the directory `<workdir>/logs/<task_name>/` with a name based off of the command used to call this executable, such as "E_Run_SHE_MyProject_0.1_SHE_MyProject_GenCatPic_retry_0.out" | no           | None        |
| --log-level `<filename>`    | Minimum severity level at which to print logging information. Valid values are DEBUG, INFO, WARNING, and ERROR. When run via the pipeline runner, this will be set based on the configuration of the pipeline server (normally INFO).  | no           | INFO        |


**Input Arguments**
>`Describe each of the input arguments which can be used when running the code, specifying the filenames of input data relative to the workdir.`

|  **Argument**               | **Description**                                                       | **Required** | **Default** |
| :------------------------   | :-------------------------------------------------------------------- | :----------: | :----------:|
| --psf_list `<filename>`     | `.json` listfile (Cardinality 1-4) listing data products for PSF `.fits` files. | yes    | N/A         |
| --pipeline_config `<filename>` | `.xml` data product or pointing to configuration file (described below), or .json listfile (Cardinality 0-1) either pointing to such a data product, or empty. | no          | None (equivalent to providing an empty listfile)         |
| --aux_data `<filename>`     | `.xml` data product describing the auxiliary information necessary for execution. | yes| N/A         |

**Output Arguments**
>`Describe each of the output arguments which can be used when running the code, specifying the desired filenames of output data relative to the workdir, which will be created by the program upon successful execution.`

|  **Argument**               | **Description**                                                       | **Required** | **Default** |
| :------------------------   | :-------------------------------------------------------------------- | :----------: | :----------:|
| --cat_pic `<filename>`      | Desired filename for `.xml` data product pointing to a `.png` image of the generated cat picture. | no          | cat_pic.xml |

**Options**
>`Describe any arguments which can be provided to the executable when run directly (not through the pipeline runner, which disallows such arguments).`

|  **Options**                | **Description**                                                       | **Required** | **Default** |
| :------------------------   | :-------------------------------------------------------------------- | :----------: | :----------:|
| --use_dog (`store true`)    | If set, will generate an image of a dog instead of a cat.             | no           | false       |
| --set_tie `<regular/bow>`   | If given, user should specify which tie to use: `regular` or `bow`. If not provided, neither a tie nor a bowtie will be added to the picture.    | no           | None    |

> `Any required files should be explicity explained in the Inputs section below`

_**Inputs**_
>`Describe in detail what inputs are necessary for running this processing element as well as where they are expected to come from`

_`psf_list`_:

**Description:** The filename of a `.json` listfile in the workdir, listing the filenames of 1-4 `.xml` data products of format dpdPsfModelImage. Each of these data products will point to a `.fits` file containing a binary data table containing necessary data on the ellipticity of a PSF for each star for each exposure. This data product and the format of the associated data table are described in detail in the Euclid DPDD at https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_psfmodelimage.html.

**Source:**  Generated by the [`SHE_PSFToolkit_model_psfs`](https://gitlab.euclid-sgs.uk/PF-SHE/SHE_PSFToolkit) executable, most expediently through running the [`SHE Analysis`](https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines) pipeline, which calls that program and passes the generated PSFs to an execution of this program. As this is an intermediate product, it is not stored in the EAS.

_`pipeline_config`_:


**Description:** One of the following:

1. The word "None" (without quotes), which signals that default values for all configuration parameters shall be used.
1. The filename of an empty `.json` listfile, which similarly indicates the use of all default values.
1. The filename of a `.txt` file in the workdir listing configuration parameters and values for executables in the current pipeline run. This shall have the one or more lines, each with the format "SHE_MyProject_config_parameter = config_value".
1. The filename of a `.xml` data product of format DpdSheAnalysisConfig, pointing to a text file as described above. The format of this data product is described in detail in the Euclid DPDD at https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_analysisconfig.html.
1. The filename of a `.json` listfile which contains the filename of a `.xml` data product as described above.

Any of the latter three options may be used for equivalent functionality.

The `.txt` pipeline configuration file may have any number of configuration arguments which apply to other executables, in addition to optionally any of the following which apply to this executable:


|  **Options**                | **Description**                                                       | **Default behaviour** |
| :------------------------   | :-------------------------------------------------------------------- | :----------:|
| SHE_MyProject_GenCatPic_use_dog `<True/False>` | If set to "True", will generate an image of a dog instead of a cat.   | Will generate a cat picture (equivalent to supplying "False" to this argument). |
| SHE_MyProject_GenCatPic_set_tie `<regular/bow>`  | Will add the selected tie (`regular` or `bow`) to the picture. | No tie will be added to the picture (equivalent to supplying "None" to this argument). |

If both these arguments are supplied in the pipeline configuration file and the equivalent command-line arguments are set, the command-line arguments will take precedence.

**Source:** One of the following:

1. May be generated manually, creating the `.txt` file with your text editor of choice.
1. Retrieved from the EAS, querying for a desired product of type DpdSheAnalysisConfig.
1. If run as part of a pipeline triggered by the [`SHE_Pipeline_Run`](https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines) helper script, may be created automatically by providing the argument `--config_args ...` to it (see documentation of that executable for further information).

_**Outputs**_
>`Describe in detail what output filenames are necessary for running this program, and what they should be expected to look like. The DPDD description of any data product should contain all information necessary to understand it. If anything is non-standard about the generated output, or you want to give some quick details, do so here.`

_`cat_pic`_:

**Description:** The desired filename of the data product for the output cat image. The data product will be an `.xml` file, so this filename should end with `.xml`.

**Details:**  The generated data product will be of type DpdSheCatImage, which is detailed in full on the DPDD at https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_catimage.html. This product provides the filename of a generated `.png` cat image in the attribute Data.DataContainer.FileName. This filename is generated to be fully-compliant with Euclid file naming standards. You can easily get this filename from the product with a command such as `grep \.png cat_pic.xml`.

_**Example**_
>`Describe here an example that any user can run out of the box to try the code and what is the expected output, if it can be reasonably run alone.`

The following example will generate picture of a cat with a bow tie in the `aux/CAT/pictures/` folder:
```bash
E-Run SHE_MyProject 0.1 SHE_MyProjectGenCatPic --workdir=AUX/SHE_MyProject/pictures/ --pipeline_config=AUX/SHE_MyProject/example_config.xml --psf_list=AUX/SHE_MyProject/example_psf.fits --use_tie=bow
```

>`Or, in the case that it is over-onerous to run an example (e.g. due to the reliance on intermediate data generated by a pipeline run which is not normally available outside of such a run), instead point to an example of running a pipeline which will call this executable.`

This program is designed to be run on intermediate data generated within an execution of the [`SHE Analysis`](https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines) pipeline. Please see the documentation of that pipeline for an example run. After that pipeline has been run once, this program can be re-run on the generated intermediate data. The command used for the execution of this program will be stored near the top of the log file for its original execution, which can be found in the folder "she_gen_cat_pic" within the workdir after execution.

### `SHE_MyProject_ShowCatPic`
> `Same structure as before: how to run the code on Elements, what are the options for the command line with descriptions and what each external file and a simple example for the user to run`

## Troubleshooting
> `If any problems are anticipated, add a section here for them to help users resolve them on their own before they need to appeal to a developer for help.`

### The cat in the generated picture appears to be wearing both a standard tie and a bowtie
> `For known problems which can occur if the user makes a common error, explain how it can be resolved.`

This is a known bug which occurs if the user requests `--use_tie=bowtie`. The correct argument is `--use_tie=bow`.

### A test failed when I ran "make test"

_**Ensure you have the most up-to-date version of the project and all its dependencies**_

It's possible the issue you're hitting is a bug that's already been fixed, or could be due to locally-installed versions of projects on the develop branch no longer being compatible with a newly-deployed version of another dependency on CODEEN. If you're running on the develop branch and have installed locally, pull the project, call `make purge`, and install again, and repeat for all dependencies you've installed locally. Try running `make test` again to see if it works.

_**Report the failing test to the developers**_

If the test still fails, please report it to the active developers listed above, ideally by creating a GitLab issue, or else by e-mailing them.

_**Try running the desired code**_

Tests can fail for many reasons, and a common reason is that the code is updated but not the test. This could lead to the test failing even if the code works properly. After you've reported the issue, you can try to run the desired code before the issue with the failing test has been fixed. There's a decent chance that the bug might only be in the test code, and the executable code will still function.

### An exception was raised, what do I do?
> `General instructions for how to figure out what to do when an exception is raised, which can be copied for all projects.`

_**Check for an issue with the input**_

First, look through the exception text to see if it indicates an issue with the input data. This will often be indicated by the final raised exception indicating an issue with reading a file, such as a SheFileReadError which states it cannot open a file. If this is the case, check if the file exists and is in the format that the code expects. If the file doesn't exist, then you've found the problem. Either a needed input file is missing, or one of the input files points to the incorrect filename. Determine which this is, and fix it from there.

If the file does exist but you still see an error reading from it, then the issue is most likely that the file is unreadable for some reason - perhaps the download was corrupt, perhaps manual editing left it improperly formatted, etc. Try to test if this is the case by reading it manually. For instance, if the program can't open a `FITS` file, try opening it with `astropy`, `ds9`, `topcat` etc. (whatever you're comfortable with) to see if you can read it external to the code.

Keep in mind that the code might try multiple methods to open a file. For instance, the pipeline_config input file can be supplied as either a raw text file, an `.xml` data product, or a `.json` listfile. The program will try all these options, and if all fail, the final exception text will only show the final type attempted. The full traceback, however, should show all attempts. So if it appears that the program tried to read a file as the wrong type, check through the traceback to see if it previously tried to read it as the expected type and failed.

_**Ensure you have the most up-to-date version of the project and all its dependencies**_

It's possible the issue you're hitting is a bug that's already been fixed, or could be due to locally-installed versions of projects on the develop branch no longer being compatible with a newly-deployed version of another dependency on CODEEN. If you're running on the develop branch and have installed locally, pull the project, call `make purge`, and install again, and repeat for all dependencies you've installed locally. Try running again to see if this works.

_**See if the exception, traceback, or log gives you any other clue to solve the problem**_

There are many reasons something might go wrong, and many have been anticipated in the code with an exception to indicate this. The exception text might tell you explicitly what the problem is - for instance, maybe two options you set aren't compatible together. If it wasn't an anticipated problem, the exception text probably won't obviously indicate the source of the problem, but you might be able to intuit it from the traceback. Look through the traceback at least a few steps back to see if anything jumps out at you as a potential problem that you can fix. Also check the logging of the program for any errors or warnings, and consider if those might be related to your problem.

_**Report the issue**_

If all else fails, raise an issue with the developers on GitLab. Be sure to include the following information:

1. Any details of input data you're using.
1. The command you called to trigger the program (or the pipeline which called the program)
1. The full log of the execution, from the start of the program to the ultimate failure. In the case of a failure during a pipeline run, you can attach the generated log file for this executable, which can be found in the `logs` directory within the work directory, and then in a subdirectory corresponding to this task.
1. Any steps you've taken to try to resolve this problem on your own.
