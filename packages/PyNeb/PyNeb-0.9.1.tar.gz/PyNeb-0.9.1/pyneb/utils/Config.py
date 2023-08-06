import os
import numpy as np
from misc import execution_path
from logging import my_logging

class _Config(object):
    """
    This is the place where to put stuff that any module may need, a kind of COMMON.
    An instantiation is done in the main __init__ file using the "config" name.

    """
    def __init__(self):
        """
        Defining some variables that will be known from everywhere:
        - INSTALLED: a dictionary to hold Boolean values for the libraries that PyNeb may need
            e.g. 'plt' for matplotlib.pyplot, 'scipy' for scipy.interpolate
        
        - Datafile: a dictionary holding the HI atom, that can be used intensively in Atom.getIonicAbundance
        
        - pypic_path: the default value for pypic_path parameter of getEmisGridDict()
            First try with $HOME/.pypics, check if it exists, if it is not writable, go to next try, 
            if it does not exists, try to create it, if fails, go to next step. Thus try with /tmp/pypics,
            do the same: test if it exists and is writable, create it if absent. If fails, set to None and
            getEmisGridDict() will need to have a value for pypic_path.
        
        No Parameter for the instantiation.
        """
        self.log_ = my_logging()
        self.calling = '_Config'
        
        self.INSTALLED ={}
        try:
            import matplotlib.pyplot as plt
            self.INSTALLED['plt'] = True
        except:
            self.INSTALLED['plt'] = False
            self.log_.message('matplotlib not available', calling = self.calling)
        try:
            from scipy import interpolate
            self.INSTALLED['scipy'] = True
        except:
            self.INSTALLED['scipy'] = False
            self.log_.message('scipy not available', calling = self.calling)
            
        self.DataFiles = {}
    
        self._initPypicPath()
        
    def _initPypicPath(self):
        """
        Defining the pypic_path variable
        """
        self.pypic_path = None
        if 'HOME' in os.environ:
            home = os.environ['HOME']
            self.pypic_path = '{0}/.pypics/'.format(home)
            if os.path.exists(self.pypic_path):
                if not os.access(self.pypic_path, os.W_OK):
                    self.log_.message('Directory {0} not writable'.format(self.pypic_path),
                                      calling = self.calling)
                    self.pypic_path = None
            else:
                try:
                    os.makedirs(self.pypic_path)
                    self.log_.message('Directory {0} created'.format(self.pypic_path),
                                      calling = self.calling)
                except:
                    self.pypic_path = None
        if self.pypic_path is None:
            self.pypic_path = '/tmp/pypics/'
            if os.path.exists(self.pypic_path):
                if not os.access(self.pypic_path, os.W_OK):
                    self.log_.message('Directory {0} not writable'.format(self.pypic_path),
                                      calling = self.calling)                                   
                    self.pypic_path = None 
            else:
                try:
                    os.makedirs(self.pypic_path)
                    self.log_.message('Directory {0} created'.format(self.pypic_path),
                                      calling = self.calling)
                except:
                    self.pypic_path = None
        self.log_.message('pypic_path set to {0}'.format(self.pypic_path),
                                      calling = self.calling)
        