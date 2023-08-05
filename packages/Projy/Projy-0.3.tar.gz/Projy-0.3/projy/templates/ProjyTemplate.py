# -*- coding: utf-8 -*-
""" Main ProjyTemplate class. """

# system
import errno
import os
import sys
from string import Template
from os.path import join, dirname
# local
from projy.TerminalView import *



class ProjyTemplate:
    """ Base template class for a Projy project creation. """

    def __init__(self):
        self.project_name = None
        self.template_name = None
        self.substitutes_dict = {}
        self.term = TerminalView()


    def create(self, project_name, template_name, substitutions):
        """ Launch the project creation. """
        self.project_name = project_name
        self.template_name = template_name

        # create substitutions dictionary from user arguments
        # TODO: check what is given
        for subs in substitutions:
            current_sub = subs.split(',')
            current_key = current_sub[0].strip()
            current_val = current_sub[1].strip()
            self.substitutes_dict[current_key] = current_val

        self.term.print_info("Creating project '{0}' with template {1}"
            .format(self.term.text_in_color(project_name, TERM_PINK), template_name))

        self.make_directories()
        self.make_files()


    def make_directories(self):
        """ Create the directories of the template. """

        # get the directories from the template
        directories = []
        try:
            directories = self.directories()
        except AttributeError:
            self.term.print_info("No directory in the template.")

        working_dir = os.getcwd()
        # iteratively create the directories
        for directory in directories:
            dir_name = working_dir + '/' + directory
            if not os.path.isdir(dir_name):
                try:
                    os.makedirs(dir_name)
                except OSError, error:
                    if error.errno != errno.EEXIST:
                        raise
            else:
                self.term.print_error_and_exit("The directory {0} already exists."
                         .format(directory))

            self.term.print_info("Creating directory '{0}'"
                                 .format(self.term.text_in_color(directory, TERM_GREEN)))


    def make_files(self):
        """ Create the files of the template.  """

        # get the files from the template
        files = []
        try:
            files = self.files()
        except AttributeError:
            self.term.print_info("No file in the template. Weird, but why not?")

        # get the substitutes intersecting the template and the cli
        try:
            for key in self.substitutes().keys():
                if key not in self.substitutes_dict:
                    self.substitutes_dict[key] = self.substitutes()[key]

        except AttributeError:
            self.term.print_info("No substitute in the template.")

        working_dir = os.getcwd()
        # iteratively create the files
        for directory, name, template_file in files:
            if directory:
                filepath = working_dir + '/' + directory + '/' + name
                filename = directory + '/' + name
            else:
                filepath = working_dir + '/' + name
                filename = name

            # open the file to write into
            try:
                output = open(filepath, 'w')
            except IOError:
                self.term.print_error_and_exit("Can't create destination"\
                                                " file: {0}".format(filepath))

            # open the template to read from
            if template_file:
                input_file = join(dirname(__file__), template_file + '.txt')

                # write each line of input file into output file,
                # templatized with substitutes
                try:
                    with open(input_file, 'r') as line:
                        template_line = Template(line.read())
                        output.write(template_line.
                                safe_substitute(self.substitutes_dict))
                    output.close()
                except IOError:
                    self.term.print_error_and_exit("Can't create template file"\
                                                   ": {0}".format(input_file))
            else:
                output.close() # the file is empty, but still created

            self.term.print_info("Creating file '{0}'"
                             .format(self.term.text_in_color(filename, TERM_YELLOW)))
