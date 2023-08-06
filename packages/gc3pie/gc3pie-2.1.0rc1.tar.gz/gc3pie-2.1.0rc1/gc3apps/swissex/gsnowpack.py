#! /usr/bin/env python
#
#   gsnowpack.py -- Front-end script for running 'snowpack' on data gathered
#   from GSN stations. Generate plots and return the corresponding plot images.
#
#   Copyright (C) 2011, 2012 GC3, University of Zurich
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
gsnowpack is a driver script that allows to run 'snowpack' on a series of input
data gathered from publicly available GSN stations. Data correspond to an
arbitrary number of GSN stations (first prototype used 2 stations).
The script is meant to be invoked every 30' and analyse updated data from the 
same stations.
For each station, gsnowpack launches a single job whose task is to run snowpack
with a gsn configuration that allows to fetch fresh data from a given station
( 1 station per job ); analyse such data and generate the plot image.
Each snowpack analysis should take no more than few seconds with the default
configuration.
Plot images are then retrieved to the client side (optionally data could be also
uploaded on an ftp or http server that would make data available for upload
to the central GSN repository).
Plot images are organized with the following schema:
<output_folder>/<station_name>/.

Input parameters consists of:
:param str filename: path to a .sno file that correspond to the selected
station.

Options parameters:
:param str GSN ini file: use an alternative GSN ini file

:param str destination URI: upload data to an accessible URI

"""

__version__ = '2.1.0rc1 version (SVN $Revision$)'
# summary of user-visible changes
__changelog__ = """
  2013-04-09:
  * Added postprocessing of result data

  2013-03-22:
  * Initial version
"""
__author__ = 'Sergio Maffioletti <sergio.maffioletti@gc3.uzh.ch>'
__docformat__ = 'reStructuredText'

# run script, but allow GC3Pie persistence module to access classes defined here;
# for details, see: http://code.google.com/p/gc3pie/issues/detail?id=95
if __name__ == "__main__":
    import gsnowpack
    gsnowpack.GsnowpackScript().run()

import os
import sys
import time
import tempfile

import posix
import shutil

import gc3libs
from gc3libs import Application, Run, Task
from gc3libs.cmdline import SessionBasedScript, executable_file
import gc3libs.utils
from gc3libs.quantity import Memory, kB, MB, GB, Duration, hours, minutes, seconds
from gc3libs.workflow import RetryableTask


## custom application class
class GsnowpackApplication(Application):
    """
    Custom class to wrap the execution of snowpack and the plotting of the
    result data.
    """
    application_name = 'gsnowpack'

    def __init__(self, sno_files, gsn_ini=None, **extra_args):

        self.station_name = extra_args['station_name']
        self.time_stamp = extra_args['time_stamp']

        # sno_file_name = basename(sno_files[0])


        command = """#!/bin/bash
echo [`date`] Start

# XXX: debug
echo ------- /DEBUG --------
env
echo ------- /DEBUG --------


# Verify consistency of data
GSN_INI='io_gsn.ini'
# SNO_NAME=`basename $SNO_FILE .sno`
SNO_NAME="%s"
SNO_FILE="./output/${SNO_NAME}.sno"


echo -n "Checking GSN ini file [$GSN_INI]... "
if [ ! -e $GSN_INI ]; then
   echo "[failed]"
   exit 1
else
   echo "[ok]"
fi

echo -n "Checking .sno file [$SNO_FILE]... "
if [ ! -e $SNO_FILE ]; then
   echo "[failed]"
   exit 1
else
   echo "[ok]"
fi

# Create filesystem layout
mkdir output
mkdir img

export LD_LIBRARY_PATH=/usr/local/lib/:$LD_LIBRARY_PATH

# run snowpack
echo "Running snowpack... "
CMD=`snowpack -c $GSN_INI -e NOW -s $SNO_NAME -m operational 2>&1`

if [ $? -ne 0 ]; then
   echo "Failed running snowpack"
   exit 1
fi

echo "Checking results"
if [ ! -e output/${SNO_NAME}.pro ]; then
   echo "Output file output/${SNO_NAME}.pro not produced"
   exit 1
fi

echo "Plotting results"
# Do the plotting part
# image files will be places in `img` folder

# Creating output folder
# Execute: create_matrix.sh <file.pro> <output_folder>/

echo "Running: create_matrix.sh output/${SNO_NAME}.pro img/"
create_plots.sh output/${SNO_NAME}.pro img/

# XXX: check this
# listing produces images
if [ `ls img/*.png | wc -l` -eq 0 ]; then
   # there are not .png files in the output folder
   echo "No images produced."
   exit 1
fi

# Cleanup unnecessary files
echo "Cleaning up image folder... "
rm img/*.dat
rm img/*.dat.gnu

echo "[`date`] End"
""" % (self.station_name)

        outputs = [('./img/','images/'),('./output/','output/')]

        # setup input references
        # inputs = [(sno_file,os.path.join('./output',os.path.basename(sno_file)))]

        inputs = []

        for _file in sno_files:
            inputs.append((_file,os.path.join('./output',os.path.basename(_file))))

        if gsn_ini:
            inputs.append((gsn_ini,'io_gsn.ini'))

        try:
            # create script file
            f_handle = tempfile.NamedTemporaryFile(prefix='gc3pie-gc_gps', suffix=extra_args['jobname'], delete=False)
            self.execution_script_filename = f_handle.name

            f_handle.file.write(command)
            f_handle.file.close()
            os.chmod(f_handle.name,0777)
        except Exception, ex:
            gc3libs.log.debug("Error creating execution script." +
                              "Error type: %s." % type(ex) +
                              "Message: %s"  %ex.message)
            raise

        inputs.append((self.execution_script_filename,'gsnowpack.sh'))

        Application.__init__(
            self,
            arguments = ['./gsnowpack.sh'],
            inputs = inputs,
            outputs = outputs,
            stdout = 'gsnowpack.log',
            join=True,
            **extra_args)

    def get_images(self):
        """
        Return a list of image files
        """
        return [os.path.join(self.output_dir,'images',img) for img in os.listdir(os.path.join(self.output_dir,'images')) if img.endswith('.png')]
        

    def get_snofiles(self):
        """
        Return a list of updated .sno files
        with corresponding .pro .map .haz
        """
        return [os.path.join(self.output_dir,'output',station_file) for station_file in os.listdir(os.path.join(self.output_dir,'output')) if station_file.startswith(self.station_name)]

class GsnowpackScript(SessionBasedScript):
    """
Scan the specified INPUT directories recursively for .sno files
and submit a job for each one found; job progress is
monitored and, when a job is done, its output files are retrieved back
into the simulation directory itself.

The ``gsnowpack`` command keeps a record of jobs (submitted, executed
and pending) in a session file (set name with the ``-s`` option); at
each invocation of the command, the status of all recorded jobs is
updated, output from finished jobs is collected, and a summary table
of all known jobs is printed.  New jobs are added to the session if
new input files are added to the command line.

Options can specify a maximum number of jobs that should be in
'SUBMITTED' or 'RUNNING' state; ``gsnowpack`` will delay submission of
newly-created jobs so that this limit is never exceeded.

    """

    def __init__(self):
        SessionBasedScript.__init__(
            self,
            version = __version__, # module version == script version
            # only display stats for the top-level policy objects
            # (which correspond to the processed files) omit counting
            # actual applications because their number varies over
            # time as checkpointing and re-submission takes place.
            stats_only_for = GsnowpackApplication,
            ) 

    def setup_options(self):
        self.add_param("-g", "--gsn", metavar="PATH",
                       dest="gsn_ini", default=None,
                       help="Path to an alternative gsn_ini file.")

        self.add_param("-p", "--publish", metavar="PATH",
                       dest="www", default=None,
                       help="Location of http server's DocRoot." + 
                       " Results (plots) will be copied and organised there")

    def setup_args(self):

        self.add_param('sno_files_location', type=str,
                       help="Path to the folder containing the .sno files")

        
    def process_args(self):
        from time import localtime, strftime
        # set timestamp
        self.time_stamp = strftime("%Y-%m-%d-%H%M", localtime())

        SessionBasedScript.process_args(self)

    def new_tasks(self, extra):
        """
        Read content of 'command_file'
        For each command line, generate a new GcgpsTask
        """

        tasks = []

        ## collect input directories/files
        def contain_sno_files(paths):
            for path in paths:
                if path.endswith('.sno'):
                    return True
            return False

        inputfiles = []

        self.sno_files_list = {}
            
        if not os.path.isdir(self.params.sno_files_location):
            gc3libs.log.error("Argument '%s' is not a directory path." % self.params.sno_files_location)
        else:
            input_list = []

            # recursively scan for input files
            for dirpath, dirnames, filenames in os.walk(self.params.sno_files_location):
                for file in filenames:
                    if file.endswith('.sno'):

                        extra_args = extra.copy()

                        extra_args['station_name'] = os.path.basename(file).split('.sno')[0]
                        self.sno_files_list[extra_args['station_name']] = dirpath

                        input_list = []
                        input_list.append(os.path.join(dirpath,file))

                        # within 'dirpath' search for all files with
                        # 'station_name' as prefix
                        # they will be all inputs
                        for _file in os.listdir(dirpath):
                            if _file.startswith(extra_args['station_name']):
                                input_list.append(os.path.join(dirpath,_file))
                            

                        extra_args['time_stamp'] = self.time_stamp

                        jobname = 'snopack-%s-%s' % (extra_args['station_name'],extra_args['time_stamp'])

                        extra_args['jobname'] = jobname
                        extra_args['output_dir'] = extra_args['output_dir'].replace(
                            'NAME',
                            os.path.join(extra_args['station_name'],extra_args['time_stamp']))

                        self.log.info("Creating new Task: '%s'" % jobname)
                        
                        tasks.append(GsnowpackApplication(
                                input_list,
                                gsn_ini = self.params.gsn_ini,
                                **extra_args))

        return tasks

    def after_main_loop(self):
        """
        After completion of the SessionBasedScript
        publish the result images to www_location.
        """
        import glob

        if self.params.www:

            # create folder
            if not os.path.exists(self.params.www):
                os.makedirs(self.params.www)
            

            # Loop trhough the list of own tasks
            # extract 'output_dir'
            # get images from output_dir/img

            for task in self.session:
                if isinstance(task,GsnowpackApplication) and task.execution.returncode == 0:
                    station_folder = os.path.join(self.params.www,task.station_name)
                    time_stamp = task.time_stamp

                    
                    # XXX: Aggressive approach
                    # first clean the existing folder
                    # then copy fresh data
                    shutil.rmtree(station_folder)

                    if not os.path.exists(station_folder):
                        try:
                            os.makedirs(station_folder)
                        except OSError, osx:
                            gc3libs.log.error("Failed while creating www folder '%s'" +
                                              "Error: %s" % (station_folder, str(osx)))
                            continue


                    for image in task.get_images():
                        # image needs to be renamed with the following schema
                        # [station_name]-[attribute-displayed]-[timestamp]
                        # timestamp format: YYYYMMDD-hhmm
                        
                        try:
                            img_attribute_displayed = os.path.basename(image).split('.')[0]
                        except Exception, ex:
                            # XXX: teoretically all the above statements are safe and should not trigger
                            # any Error
                            # but to be safe...
                            # in case we fail, use default
                            gc3libs.log.error("Exception while setting image attribute" +
                                              "Error type: '%s', message: '%s'" % (type(ex),str(ex)))
                            img_attribute_displayed = ""

                        image_name = "%s-%s-%s.png" % (task.station_name,img_attribute_displayed,time_stamp)

                        shutil.copy(image,os.path.join(station_folder,image_name))

                    # Update timestamp file
                    time_stamp_file = os.path.join(station_folder,'.time_stamp')
                    try:
                        fh = open(time_stamp_file,'wb')
                        fh.seek(0)
                        fh.write(time_stamp)
                        fh.close()
                    except OSError, osx:
                        gc3libs.log.error("Failed while updating timestamp file " +
                                          "'%s'. Error '%s'" % (time_stamp_file, str(osx)))

                    # Update original .sno files with computed one
                    # remove .sno files from output_dir
                    if task.station_name in self.sno_files_list.keys():
                        gc3libs.log.info('Updating sno files for station %s' % task.station_name)
                        for snofile in task.get_snofiles():
                            # replace .sno files with new ones
                            try:
                                shutil.move(snofile,self.sno_files_list[task.station_name])
                            except Exception, ex:
                                gc3libs.log.error("Failed while updating .sno files %s" +
                                                  "Error type '%s', message '%s'" % (snofile, type(ex), str(ex)))
                                continue


                                
                   


                    
                    


