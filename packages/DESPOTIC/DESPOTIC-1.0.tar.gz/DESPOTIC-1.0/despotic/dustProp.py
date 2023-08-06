"""
This module defines the dustProp class, which carries information
about the properties of the dust in a cloud.
"""

class dustProp:
    """
    A class describing the properties of dust grains.

    Attributes
    ----------
    sigma10 : float
        dust opacity to thermal radiation at 10 K, in cm^2 H^-1
    sigmaPE : float
        dust opacity averaged over 8 - 13.6 eV, the range that
        dominates grain photoelectric heatin
    sigmaISRF : float
        dust opacity averaged the range that dominates grain starlight
        heating
    Zd : float
        dust abundance normalized to solar neighborhood value
    beta : float
        dust spectral index in the mm, sigma ~ nu^beta
    alphaGD : grain-gas coupling coefficient

    Methods
    ------
    None
    """

    # Initialize to generic MW values
    sigma10 = 2.0e-25
    sigmaPE = 1.0e-21
    sigmaISRF = 3.0e-22
    Zd = 1.0
    beta = 2.0
    alphaGd = 3.2e-34

