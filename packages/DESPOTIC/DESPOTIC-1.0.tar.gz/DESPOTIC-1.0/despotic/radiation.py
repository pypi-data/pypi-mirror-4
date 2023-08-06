"""
This module defines the radiation class, which stores information
about the radiation field impinging on a cloud, including cosmic
rays.
"""

import numpy as np

# Define some global physical constants in cgs units
import scipy.constants as physcons
kB = physcons.k/physcons.erg
c = physcons.c/physcons.centi
mH = physcons.m_p/physcons.gram
h = physcons.h*1e7
sigma=physcons.sigma/physcons.erg*physcons.centi**2
a = 4*sigma/c

class radiation:
    """
    A class describing the radiation field affecting a cloud.

    Attributes
    ----------
    TCMB : float
        the temperature of the CMB, in K
    TradDust : float
        the temperature of the dust IR background field, in K
    ionRate : float
        the primary ionization rate due to cosmic rays and x-rays, in
        s^-1 H^-1
    chi : float
        strength of the ISRF, normalized to the solar neighborhood value

    Methods
    -------
    __init__ -- initializes
    ngamma -- returns the photon occupation number due to the CMB at a
        given frequency
    """

########################################################################
# Method to initialize
########################################################################
    def __init__(self):
        """
        This method initializes the value of the attributes to
        reasonable estimates of typical Milky Way values

        Parameters
        ----------
        None

        Returns
        -------
        Nothing
        """

        # Initialize to generic MW values
        self.TCMB = 2.73
        self.TradDust = 0.0
        self.ionRate = 2.0e-17
        self.chi = 1.0


########################################################################
# Method to return the photon occupation number at the CMB temperature
########################################################################
    def ngamma(self, Tnu):
        """
        Return the photon occupation number 1 / [exp(-h nu / k T_CMB) - 1].

        Parameters
        ----------
        Tnu : float or array of float
            frequency translated into K, i.e. frequency times h/kB

        Returns
        -------
        ngamma : float or array
            photon occupation number 1 /  [exp(-T_nu / T_CMB) - 1]
        """

        # Return value, written in such a way as to produce underflows
        # rather than overflows when Tnu >> TCMB
        expfac = np.exp(-Tnu/self.TCMB)
        return expfac / (1.0 - expfac)
