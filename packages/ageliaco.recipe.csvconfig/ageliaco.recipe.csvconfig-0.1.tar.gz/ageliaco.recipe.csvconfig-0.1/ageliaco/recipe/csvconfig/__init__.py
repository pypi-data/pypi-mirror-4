# -*- coding: utf-8 -*-
"""Recipe csvconfig"""
import re
import csv
import os.path
import zc.buildout.buildout
import pprint
from zc.buildout.buildout import Options
import ConfigParser
import logging
            
        



class Recipe(object):
    """zc.buildout recipe"""
    def read_csvconfig(self):
        aReader = csv.reader(open(self.csvfile))
        for index,row in enumerate(aReader):
            print ' : '.join(row)
            if index == 0: #first row holds the variable names
                for var in row:
                    self.vars.append(var)
                continue
            d = {}
            for i, var in enumerate(row):
                d[self.vars[i]] = var
            self.lines.append(d)

    def expandvar(self, word, line):
        """expand variables if found in vars according to dict 'line'
            returns word with var subsitution when possible
        """
        match = self.c_re.search(word)
        i = 0
        while match:
            var = match.group(1)
            to_replace = match.group(0)
            length = len(to_replace) + 1
            #import pdb; pdb.set_trace()
            if var in self.vars:
                word = word.replace(to_replace,line[var])
                length = len(line[var]) + 1
            i = match.pos + length
            match = self.c_re.search(word, i)
        return word

    def expandvars_on_section(self, config, buildout, section, newsection, line):
        """apply a list (line) of vars in section"""
        if not buildout.has_section(newsection):
            buildout.add_section(newsection)
        for option in config.options(section):
            #import pdb; pdb.set_trace()
            opt = config.get(section, option)
            newopt = self.expandvar(opt, line)
            buildout.set(newsection, option, newopt)
        return buildout
                

    def expandall_on_section(self, config, buildout, section):
        """apply all vars on a section"""
        # first expand section name if necessary
        match = self.c_re.search(section)
        if match:
            for line in self.lines:
                newsection = self.expandvar(section, line)
                #import pdb; pdb.set_trace()
                if newsection != section:
                    buildout = self.expandvars_on_section(config, buildout, 
                                                    section, newsection, line)
        else:
            if not buildout.has_section(section):
                buildout.add_section(section)
            for option in config.options(section):
                opt = config.get(section, option)
                match = self.c_re.search(opt)
                if match:
                    opts = []
                    #import pdb; pdb.set_trace()
                    for line in self.lines:
                        newopt = self.expandvar(opt, line)
                        if newopt!=opt and newopt not in opts:
                            opts.append(newopt)
                    buildout.set(section, option, ' '.join(opts))
                else:    
                    buildout.set(section, option, opt)
        return buildout 

    def apply_variables(self,template,target):
        """ apply variables in template and save it as new config file in target
        """
        
        config = ConfigParser.SafeConfigParser()
        newconfig = ConfigParser.SafeConfigParser()
        config.read(template)
        #import pdb; pdb.set_trace()
        # first read sections to find variables in vars
        # newconfig.sections = dict(config.sections)
        #import pdb; pdb.set_trace()
        for sect in config.sections():
            newconfig = self.expandall_on_section(config, newconfig, sect)
        #import pdb; pdb.set_trace()
        with open(target, 'wb') as configfile:
            newconfig.write(configfile)                            
                    

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.csvfile = self.options.pop('csvfile').strip()
        self.templates = self.options.pop('templates', name).strip().split()
        self.lines = []    
        self.vars = []
        self.c_re = re.compile(r'\$\{([^:|}]*)\}')
    
    #template name may come under the form "filepath:target" both being relative path from 
    #buildout-dir
    #if no ":" is found default target applied is buildout-dir with same filename as template
    # minus the ".in" extension
    def parse_template(self,template):
        if ':' in template:
            template, target = template.split(':')
            target = os.path.join(
                              self.buildout['buildout']['directory'],
                              target,
                              )

        else:
            target = template.split('/')[-1][0:-3]
        return template, target



    def install(self):
        """Installer"""
        # XXX Implement recipe functionality here

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        ret = []
        new_sections = []
        self.read_csvconfig()
        for template, target in (self.parse_template(template) for template in self.templates):
            self.apply_variables(template,target)
            logging.getLogger(self.name).info(
                'Creating config file : %s', target)
            ret.append(target)
        return tuple(ret)

    def update(self):
        """Updater"""
        pass
