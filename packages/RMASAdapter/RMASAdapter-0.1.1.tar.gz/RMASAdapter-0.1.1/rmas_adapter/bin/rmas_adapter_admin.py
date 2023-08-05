#!/usr/bin/env python
'''
This is the script that you will use to create your new rmas_adapter skeleton.
It will use the adapter_template to create a new adapter, which provides you with
the runner script that allows you to start your adapter polling, and the settings file
where you specify the connection details to connect to the rmas bus, and which rmas events
you want to respond to.
'''



import argparse
import os

import codecs
import rmas_adapter


template_dir = os.path.join(rmas_adapter.__path__[0], 'conf', 'adapter_template') #the directory that has the adapter template

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('command', 
                        help='The command that you want to run, currently this is restricted to: create which will create a new adapter',
                        type=str)
    parser.add_argument('adapter_name' ,
                        help='The name of your new adapter',
                        type=str,)
    parser.add_argument('--target' , '-t',
                        help='The destination directory to build the adapter skeleton into, if not specified then the adapter will be generated in the current directory',
                        type=str,)
    
    args = parser.parse_args()
    
    #if the command is not "create" then throw an error
    
    if args.command != 'create':
        raise ValueError('This script only supports the create command at present')
    
    #if target is not specified then make the current directory the base directory
    if args.target:
        base_dir = os.path.join(args.target, args.adapter_name)
    else:
        base_dir = os.path.join(os.getcwd(), args.adapter_name)
        
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    

    
    #walk the template directory, and for each file:
    
    for root, dirs, files in os.walk(template_dir):
        
        for filename in files:
            if filename.endswith(('.pyo','.pyc', '.py.class')):
                #ignore compiled files
                continue
            
            template_path = os.path.join(root, filename)
            output_path = os.path.join(base_dir, filename )
            #read in the contents, and make it the contents of a template object
            #render the template and write to an identically named file in the basedirectory

            
            with codecs.open(template_path, 'r', 'utf-8') as template_file:
                contents = template_file.read()

            
            with codecs.open(output_path, 'w', 'utf-8') as output_file:
                output_file.write(str(contents))
    
    