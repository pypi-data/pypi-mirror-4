# -*- coding: utf-8 -*-
"""Recipe csvconfig"""
import re
import csv
import os.path
import zc.buildout.buildout
import pprint
from zc.buildout.buildout import Options
import configparser
import logging
            
        



class Recipe(object):
    """zc.buildout recipe"""
    def read_csvconfig(self):
        aReader = csv.reader(open(self.csvfile))
        for index,row in enumerate(aReader):
            #print ' : '.join(row)
            if index == 0: #first row holds the variable names
                for var in row:
                    self.vars.append(var.strip())
                continue
            d = {}
            for i, var in enumerate(row):
                d[self.vars[i]] = var.strip()
            self.lines.append(d)

    def multikeydict(self,keys, lines):
        """generate a dict with 'keys' (list of variables names) as index key
        the value part of this dict is a list of dict that holds the values for
        the different columns"""
        newdict = {}

        for line in lines:
            newkey_value = []
            newkey = ''
            for key in keys:
                newkey_value.append(line[key])
            newkey_value.sort()
            newkey = ','.join(newkey_value)
            if newkey not in newdict.keys():
                newdict[newkey] = []
            newdict[newkey].append(line)
        return newdict
                
                
    def checkkey(self,word):
        """check either on the left part of an option or on a section if there is, or are
        keys => returns a list of keys or an empty list if nothing"""
        match = self.c_re.search(word)
        i = 0
        keylist = []
        while match:
            var = match.group(1)
            to_replace = match.group(0)
            length = len(to_replace) + 1
            #import pdb; pdb.set_trace()
            if var in self.vars:
                keylist.append(var)
            i = match.pos + length
            match = self.c_re.search(word, i)
        #print "checkkey : ", keylist
        return keylist
                

    def expandvar(self, word, line):
        """expand variables if found in vars according to dict 'line'
            returns word with var subsitution when possible
            rule is that if there's a variable in word and line as an empty result
            for this variable, then the returned word is set to ''
            the same is true if for all variable of a word line provides an empty result
        """
        match = self.c_re.search(word)
        i = 0
        nbmatch = 0
        empty = 0
        original = word[:]
        while True:
            if not match:
                break
            nbmatch += 1
            var = match.group(1)
            to_replace = match.group(0)
            length = len(to_replace) + 1
            #import pdb; pdb.set_trace()
            if var in self.vars:
                if line[var] == '':
                    empty += 1
                word = word.replace(to_replace,line[var])
                length = len(line[var]) + 1
            i = match.pos + length
            match = self.c_re.search(word, i)
        #print "expandvar : ", word, self.vars
        if nbmatch and nbmatch == empty:
            #import pdb; pdb.set_trace()
            return ''
        return word

                
    def expandsection(self,section,config,buildout,keylist,dictlist):
        """expand section with variables"""
        newsection = self.expandvar(section,dictlist[0])
        if not buildout.has_section(newsection):
            buildout.add_section(newsection)
        for option in config.options(section):
            #import pdb; pdb.set_trace()
            opt = config.get(section, option)
            match = self.c_re.search(option)
            if match: #option name contains a variable
                newkeys = self.checkkey(option)
                keydict = self.multikeydict(newkeys,dictlist)
                for key in keydict.keys():
                    buildout = self.expandoption(option,opt,newsection,buildout,keydict[key])
            else:#eventually right-part contains a variable
                buildout = self.expandoption(option,opt,newsection,buildout,dictlist)
        return buildout
        
    def expandoption(self,option,optionvalue,section,buildout,dictlist):
        """expand section with variables"""
        newoption = self.expandvar(option,dictlist[0])
        if not buildout.has_section(section):
            buildout.add_section(section)
        newopts = []
        for line in dictlist:
            #import pdb; pdb.set_trace()
            newopt = self.expandvar(optionvalue, line)
            if newopt not in newopts:
                newopts.append(newopt)
        newoptionvalue = '\n\t'.join(newopts)
        buildout.set(section, newoption, newoptionvalue)
        return buildout
        

    def expandall_on_section(self, config, buildout, section):
        """apply all vars on a section"""
        # first expand section name if necessary
        match = self.c_re.search(section)
        if match:
            newkeys = self.checkkey(section)
            keydict = self.multikeydict(newkeys,self.lines)
            for key in keydict.keys():
                buildout = self.expandsection(section,config,buildout,key,keydict[key])
        
        else:
            buildout = self.expandsection(section,config,buildout,self.vars,self.lines)
        return buildout 

    def apply_variables(self,template,target):
        """ apply variables in template and save it as new config file in target
        """
        
        config = configparser.ConfigParser(delimiters=('=', '+=', '-='))
        newconfig = configparser.ConfigParser(delimiters=('=', '+=', '-='))
        config.read(template)
        #import pdb; pdb.set_trace()
        # first read sections to find variables in vars
        # newconfig.sections = dict(config.sections)
        #import pdb; pdb.set_trace()
        for sect in config.sections():
            newconfig = self.expandall_on_section(config, newconfig, sect)
        #import pdb; pdb.set_trace()
        with open(target, 'wb+') as configfile:
            newconfig.write(configfile)                            
                    

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.csvfile = self.options.pop('csvfile').strip()
        self.templates = self.options.pop('templates', name).strip().split()
        self.lines = []    
        self.vars = []
        self.c_re = re.compile(r'\$\$\{([^:|}]*)\}')
    
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
        return template.strip(), target.strip()



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
        return self.install()
