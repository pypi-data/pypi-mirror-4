from __future__ import division
import os
import math

import numpy as np
import scipy as sp
import scipy.interpolate

from hyperspy.defaults_parser import preferences
from hyperspy.misc.physical_constants import R, e, m0, a0, c
from hyperspy.misc.eels.base_gos import GOSBase
from hyperspy.misc.eels.elements import elements


class HartreeSlaterGOS(GOSBase):
    """Read Hartree-Slater Generalized Oscillator Strenght parametrized
    from files.
    
    Parameters
    ----------
    
    element_subshell : str
        For example, 'Ti_L3' for the GOS of the titanium L3 subshell
        
    Methods
    -------
    
    readgosfile()
        Read the GOS files of the element subshell from the location 
        defined in Preferences.
    get_qaxis_and_gos(ienergy, qmin, qmax)
        given the energy axis index and qmin and qmax values returns
        the qaxis and gos between qmin and qmax using linear 
        interpolation to include qmin and qmax in the range.
        
    
    Attributes
    ----------
    
    energy_axis : array
        The tabulated energy axis
    qaxis : array
        The tabulated qaxis
    energy_onset: float
        The energy onset for the given element subshell as obtained
        from iternal tables.
    
    """

    _name = 'Hartree-Slater'
    def __init__(self, element_subshell):
        """
        Parameters
        ----------
    
        element_subshell : str
            For example, 'Ti_L3' for the GOS of the titanium L3 subshell
            
        """
        # Check if the Peter Rez's Hartree Slater GOS distributed by 
        # Gatan are available. Otherwise exit
        if not os.path.isdir(preferences.EELS.eels_gos_files_path):
            raise IOError(
                "The parametrized Hartree-Slater GOS files could not "
                "found in %s ." % preferences.EELS.eels_gos_files_path +
                "Please define a valid location for the files "
                "in the preferences.")
        self.element, self.subshell = element_subshell.split('_')
        self.read_elements()
        self.readgosfile()

    def readgosfile(self): 
        print "\nHartree-Slater GOS"
        print "\tElement: ", self.element
        print "\tSubshell: ", self.subshell
        print "\tOnset Energy = ", self.onset_energy
        element = self.element
        subshell = self.subshell
        filename = os.path.join(
            preferences.EELS.eels_gos_files_path, 
            elements[element]['subshells'][subshell]['filename'])
            
        with open(filename) as f:
            GOS_list = f.read().replace('\r','').split()

        # Map the parameters
        material = GOS_list[0]
        info1_1 = float(GOS_list[2])
        info1_2 = float(GOS_list[3])
        info1_3 = float(GOS_list[4])
        ncol    = int(GOS_list[5])
        info2_1 = float(GOS_list[6])
        info2_2 = float(GOS_list[7])
        nrow    = int(GOS_list[8])
        self.gos_array = np.array(GOS_list[9:], dtype=np.float64)
        # The division by R is not in the equations, but it seems that
        # the the GOS was tabulated this way
        self.gos_array = self.gos_array.reshape(nrow, ncol) / R
        del GOS_list
        
        # Calculate the scale of the matrix
        self.rel_energy_axis = self.get_parametrized_energy_axis(
            info2_1, info2_2, nrow)
        self.qaxis = self.get_parametrized_qaxis(
            info1_1, info1_2, ncol)
        self.energy_axis = self.rel_energy_axis + self.onset_energy
                      
    def integrateq(self,energy_shift, angle,E0):
        qint = np.zeros((self.energy_axis.shape[0]))
        # Calculate the cross section at each energy position of the 
        # tabulated GOS
        gamma = 1 + E0 / 511.06
        T = 511060 * (1 - 1 / gamma**2) / 2
        for i in xrange(0,self.gos_array.shape[0]):
            E = self.energy_axis[i] + energy_shift
            # Calculate the limits of the q integral
            qa0sqmin = (E**2) / (4 * R * T) + (E**3) / (
                            8 * gamma ** 3 * R * T**2)
            p02 = T / (R * (1 - 2 * T / 511060))
            pp2 = p02 - E / R * (gamma - E / 1022120)
            qa0sqmax = qa0sqmin + 4 * np.sqrt(p02 * pp2) * \
                (math.sin(angle/2))**2
            qmin = math.sqrt(qa0sqmin) / a0
            qmax = math.sqrt(qa0sqmax) / a0
            # Perform the integration in a log grid
            qaxis, gos = self.get_qaxis_and_gos(i, qmin, qmax)
            logsqa0qaxis = np.log((a0 * qaxis)**2)
            qint[i] = sp.integrate.simps(gos, logsqa0qaxis)
        E = self.energy_axis + energy_shift
        # Energy differential cross section in (barn/eV/atom)
        qint *= (4.0 * np.pi * a0 ** 2.0 * R**2 / E / T *
                 self.subshell_factor) * 1e28
        self.qint = qint
        return sp.interpolate.interp1d(E, qint, kind=3)
            
                                               
