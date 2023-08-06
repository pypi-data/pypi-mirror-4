#!/usr/bin/env python

'''
Created on Aug 20, 2009

@author: jonathanfriedman

Write a shell script that submits a scipt that uses the survey package to the queue.
The resulting script can be submitted to the queue using the qsub command, e.g.:

   qsub -cwd run_survey_script.sh

----------
Important:
----------
To be able to import the survey module, your python script must start with:

   import sys
   sys.path.append('/home/yonatanf/alm_lib') 


Typically this will be followed by imported survey and SurveyMatrix:

   import survey
   from survey.SurveyMatrix import SurveyMatrix as SM
'''


def write_script(python_script, shell_script=None, args=None, modules=[]):
    '''
    write an SGE script that runs a python command with command line arguments.
    Inputs:
        shell_script  - name of resulting script file to be submitted to the queue.
        python_script - name of python script to run
        args          - list of command line input arguments for python
        modules       - list of modules to be loaded in SGE env., 
                        in addition to the modules required for survey. 
    '''
    import subprocess

    f_out = open(shell_script,'w')
    f_out.write('#!/bin/tcsh\n\n') #set the shell
        
    #add modules
    for mod in modules:
        f_out.write('module add '+mod+'\n')
        f_out.write('\n')
    
    #set env variables
    f_out.write('setenv R_LIBS_USER /home/yonatanf/R/x86_64-unknown-linux-gnu-library/2.12\n')
            
    #python comman
    line = python_script
    if args:
        args_string = map(lambda x: str(x),args)
        line+=' '+' '.join(args_string)
    f_out.write(line)
    f_out.write('\n')
    f_out.close()

    cmd='chmod a+x ' + shell_script   
    subprocess.call(cmd,shell=True)

     
if __name__ == '__main__':
    ## parse input arguments
    from optparse import OptionParser
    kwargs = {}
    usage  = ('Write a shell script for submitting python scripts that use the survey2 package to the queue.\n'
              'The resulting script can be submitted to the queue using the qsub command, e.g.:\n'
              '\n'
              '    qsub -cwd run_survey_script.sh'
              )
    
    parser = OptionParser(usage)
    parser.add_option("-s", "--shell_script", dest="shell_script", type = 'str', default=None,
                      help="name of resulting script file to be submitted to the queue.")
    parser.add_option("-m", "--modules", dest="modules_file", default=None,
                      help="file listing modules to be loaded in SGE env.\
                       in addition to the modules required for survey.\
                       Each module should be listed in a new line")

    (options, args) = parser.parse_args()
    python_script   = args[0]
    
    
    # get extra module names from file
    modules_file = options.modules_file
    if modules_file is not None:
        f = open(modules_file,'r')
        lines = f.reaflines()
        f.close()
        modules = [line.strip() for line in lines]
    else:
        modules = []
    
    # set name of shell file     
    shell_script = options.shell_script
    if shell_script is None:
        shell_script = python_script.split('.')[0] +'.sh'
            
    write_script(python_script, shell_script, modules=modules, args=args[1:])    
   
    
    
