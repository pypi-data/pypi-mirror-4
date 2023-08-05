Barak's Documentation
=====================
This package contains functions useful for scientific programming,
with a focus on astronomical research. The documentation details
everything that is available, but some example tasks that can be
handled are:

  * Calculate absorption profiles for various ions observed in
    astrophysical environments.
  * Fit a smooth continuum to a spectrum with many emission or
    absorption features.
  * Find the expected broad-band magnitudes given a spectral energy
    distribution.
  * Calculate cosmological distance measures for various cosmologies.

The package can be downloaded `here <https://github.com/nhmc/Barak>`_.

It requires `NumPy <http://numpy.scipy.org/>`_, `Matplotlib
<http://matplotlib.sourceforge.net/>`_, `SciPy
<http://www.scipy.org/>`_, `ATpy <http://atpy.github.com/>`_ and
`Astropy <http://www.astropy.org>`_.

To install, just copy the ``barak/`` directory to a location pointed
to by your PYTHONPATH variable.

To run the tests you need `py.test <http://pytest.org/latest/>`_
installed.  Then run::

   py.test barak 

from the ``barak/`` directory.

Feel free to email me if you have any questions: neilcrighton
.at. gmail .dot. com

.. raw:: html

 <a href="https://github.com/nhmc/Barak"><img style="position: absolute; top: 0; right: 0; border: 0;" src="https://s3.amazonaws.com/github/ribbons/forkme_right_orange_ff7600.png" alt="Fork me on GitHub"></a>

.. toctree::
   :maxdepth: 2

   index.rst

absorb
------

This module has routines for analysing the absorption profiles
from ions and molecules.

.. currentmodule:: barak.absorb

.. autosummary::
   :toctree: generated/

   T_to_b
   b_to_T
   calc_Wr
   calc_iontau
   calc_tau_peak
   calctau
   find_tau
   findtrans
   read_HITRAN
   readatom
   split_trans_name
   tau_LL

abundances
----------

Abundances and condensation temperatures.

This contains the following two datasets:

Asolar:
  An ordered dictionary of abundances from `Lodders 2003, ApJ, 591,
  1220 <http://adsabs.harvard.edu/abs/2003ApJ...591.1220L>`_. It
  contains a value A for each element `el`, where A is defined::

    A(el) = log10 n(el)/n(H) + 12

  `n(el)` is the number density of atoms of that element, and `n(H)`
  is the number density of hydrogen.

cond_temp:
  An array of condensation temperatures for each element from the same
  reference.  The condensation temperature is the temperature at which
  an element in a gaseous state attaches to dust grains.

  It contains the values `tc` and `tc50` for each element, where `tc`
  is the condensation temperature in K when condensation begins, and
  `tc50` is the temperature when 50% of the element is left in a
  gaseous state.

.. currentmodule:: barak.abundances

.. autosummary::
   :toctree: generated/

   calc_abund

constants
---------

Useful physical and mathematical values. Physical constants in
Gaussian cgs units when not indicated otherwise. From 2010 CODATA
recommended values where available (see
http://physics.nist.gov/cuu/Constants/index.html).

>>> import constants as c
>>> from math import sqrt 
>>> Planck_length = sqrt(c.hbar * c.G / c.c**3)    # cm 
>>> Planck_mass = sqrt(c.hbar * c.c / c.G)         # g
>>> Planck_time = sqrt(c.hbar * c.G / c.c**5)      # s

Constants defined:

 ======== ===================== =============== ===============================
 c         2.99792458e10        cm/s            speed of light
 G         6.67384e-8           cm^3/g/s^2      gravitational constant
 hplanck   6.6260775e-27        erg s           Planck's constant
 hbar      1.054571726e-27      erg s           1/(4*pi) * Planck's constant
 kboltz    1.3806488e-16        erg/K           Boltzmann constant
 mp        1.67261777e-24       g               proton mass
 me        9.10938291e-28       g               electron mass
 eV        1.602176565e-12      ergs            electron volt
 e         4.80320451e-10       esu             magnitude of charge on electron
 sigma     5.670373e-5          erg/s/cm^2/K^4  Stefan-Boltzmann constant
 Ryd       2.179872171e-11      ergs            Rydberg: energy needed to
                                                dissociate H atom from
                                                ground state
 Jy        1e-23                ergs/s/cm^2/Hz  Jansky
 sigmaT    6.652458734e-25      cm^2            Thomson cross section
 Mmoon     7.348e25             g               Moon mass
 Rmoon     1.7374e8             cm              Moon radius
 Mearth    5.9742e27            g               Earth mass
 Rearth    6.3781e8             cm              Earth radius
 Msun      1.989e33             g               Solar mass
 Lsun      3.90e33              erg/s           Solar luminosity
 Rsun      6.96e10              cm              Solar radius
 au        1.496e13             cm              Distance from Earth to Sun
 ly        9.4607304725808e16   cm              light year
 pc        3.08567802e18        cm              parsec
 kpc       3.08567802e21        cm              kiloparsec
 Mpc       3.08567802e24        cm              megaparsec
 yr        3.155815e7           s               year
 Gyr       3.155815e16          s               gigayear
 mu        0.62                 unitless        mean molecular weight of
                                                astrophysical gas
 mile      160934.              cm              mile
 a0        hbar**2 / me / e**2  cm              Bohr radius
 alpha     e**2 / (hbar*c)      unitless        Fine structure constant
 Ryd_Ang   h * c * 1.0e8 / Ryd  Angstroms       Rydberg in Angstroms
 c_kms     2.99792458e5         km/s            speed of light
          
 sqrt_ln2  0.832554611158       sqrt(ln(2))
 pi       

 wlya      1215.6701            Angstroms       Wavelength of HI Lya transition
 wlyb      1025.72              Angstroms       Wavelength of HI Lyb transition
  
 Ar                                             dictionary of atomic weights
 ======== ===================== =============== ===============================

.. currentmodule:: barak.constants

.. autosummary::
   :toctree: generated/


cont
----



.. currentmodule:: barak.cont

.. autosummary::
   :toctree: generated/

   InteractiveCoFit
   InteractiveCoFit.calc_tau
   InteractiveCoFit.modifypoints
   InteractiveCoFit.on_button_release
   InteractiveCoFit.on_keypress
   InteractiveCoFit.plotinit
   InteractiveCoFit.update

convolve
--------

Functions related to convolution.

.. currentmodule:: barak.convolve

.. autosummary::
   :toctree: generated/

   convolve_psf
   convolve_window

coord
-----

Astronomical coordinate functions.

.. currentmodule:: barak.coord

.. autosummary::
   :toctree: generated/

   ang_sep
   check_ra_dec
   dec2s
   dec_dec2s
   dec_s2dec
   distsq
   distsq_to_radians
   indmatch
   match
   ra_dec2s
   ra_s2dec
   radec_to_xyz
   radians_to_distsq
   s2dec
   unique_radec

extinction
----------

Tools for calculating dust attenuation.

**How dust attentuation is expressed in this module**

If :math:`I_\lambda` is the observed attenuated intensity of an
object, and :math:`I_{\lambda,0}` is the unattenuated intensity
modulated by an optical depth :math:`\tau_\lambda` due to dust
particles, then:

.. math::

  I_\lambda = I_{\lambda,0}\ e^{-\tau_\lambda}

Generally the attenuation is given in magnitude in a band or at a
wavelegnth. For example, A(V) refers to the extinction in magnitudes
in the V band, and

.. math::

  E(B - V) \equiv A(B) - A(V)

is the difference in extinction between the B and V
bands. Empirically, dust attenuation is found to have a similar
functional form in different parts of the Milky Way's ISM that can be
parametrised with a normalisation A(V) and slope E(B - V). Another
commonly used quantity is

.. math::

  R(V) \equiv A(V) / E(B - V)

Analytic approximations for dust attenuation curves are often
calculated as a function of R(V), and then normalised by A(V) or, more
commonly, E(B - V). The attenuation for all the public functions in
this module is returned as :math:`\tau(\lambda)`. This is related to
:math:`A(\lambda)` in the following way:

.. math::

  \tau(\lambda) = A(\lambda) / (2.5 \log_{10}(e))

**References**

- 'Astrophysics of Dust in Cold Clouds' by B.T. Draine:
  http://arxiv.org/abs/astro-ph/0304488
- 'Interstellar Dust Grains' by B.T. Draine:
  http://arxiv.org/abs/astro-ph/0304489

Note that much of the code in this module is adapted from Erik
Tollerud's `Astropysics <https://github.com/eteq/astropysics>`_, which
has an Apache licence.

.. currentmodule:: barak.extinction

.. autosummary::
   :toctree: generated/

   LMC_Gordon03
   MW_Cardelli89
   SMC_Gordon03
   starburst_Calzetti00

fitcont
-------

Functions and Classes used to fit an estimate of an unabsorbed
continuum to a QSO spectrum.

.. currentmodule:: barak.fitcont

.. autosummary::
   :toctree: generated/

   InteractiveCoFit
   InteractiveCoFit.modifypoints
   InteractiveCoFit.on_button_release
   InteractiveCoFit.on_keypress
   InteractiveCoFit.plotinit
   InteractiveCoFit.update
   fitqsocont
   spline_continuum

interp
------

Interpolation-related functions and classes.

.. currentmodule:: barak.interp

.. autosummary::
   :toctree: generated/

   AkimaSpline
   CubicSpline
   CubicSpline.set_d2
   fit_spline
   interp_Akima
   interp_spline
   splice
   trilinear_interp

io
--

Functions to read and write text, fits and pickle files.

.. currentmodule:: barak.io

.. autosummary::
   :toctree: generated/

   loadobj
   parse_config
   readsex
   readtabfits
   readtxt
   saveobj
   sex_to_DS9reg
   write_DS9reg
   writetabfits
   writetable
   writetxt

phot
----

Photometry-based tools.

.. currentmodule:: barak.phot

.. autosummary::
   :toctree: generated/

   UBVRI_to_ugriz

plot
----

Plotting routines.

.. currentmodule:: barak.plot

.. autosummary::
   :toctree: generated/

   arrplot
   axvfill
   axvlines
   default_marker_size
   dhist
   distplot
   draw_arrows
   errplot
   histo
   puttext
   shade_to_line
   shade_to_line_vert

pyvpfit
-------

Contains a class, VpfitModel, useful for parsing f26 and fort.13
files, and writing out fort.13 files.

.. currentmodule:: barak.pyvpfit

.. autosummary::
   :toctree: generated/

   VpfitModel
   VpfitModel.copy
   VpfitModel.writef13
   VpfitModel.writef26
   calc_Ntot
   calc_v90
   make_autovpin_input
   make_rdgen_input
   parse_entry
   parse_lines
   parse_regions
   readf13
   readf26
   sumlines

sed
---

Perform calculations on Spectral Energy Distributions (SEDs).

Based on the SED module in astLib by Matt Hilton, with some routines
copied from there (LGPL): http://astlib.sourceforge.net

- VEGA: The SED of Vega, used for calculation of magnitudes on the Vega system.
- AB: Flat spectrum SED, used for calculation of magnitudes on the AB system.
- SUN: The SED of the Sun.

.. currentmodule:: barak.sed

.. autosummary::
   :toctree: generated/

   Passband
   Passband.plot
   SED
   SED.apply_extinction
   SED.calc_colour
   SED.calc_flux
   SED.calc_mag
   SED.copy
   SED.integrate
   SED.normalise_to_mag
   SED.plot
   SED.redshift_to
   Jy2Mag
   flux2mag
   get_SEDs
   get_bands
   get_extinction
   mag2Jy
   mag2flux

spec
----

Contains an object to describe a spectrum, and various
spectrum-related functions.

.. currentmodule:: barak.spec

.. autosummary::
   :toctree: generated/

   Spectrum
   Spectrum.multiply
   Spectrum.plot
   Spectrum.rebin
   Spectrum.rebin_simple
   Spectrum.stats
   Spectrum.write
   air2vac_Ciddor
   air2vac_Morton
   combine
   convolve_constant_dv
   cr_reject
   cr_reject2
   find_cont
   find_err
   find_wa_edges
   getwave
   make_constant_dv_wa_scale
   make_wa_scale
   pca_qso_cont
   plot
   plotatmos
   plotlines
   qso_template
   qso_template_uv
   read
   rebin
   rebin_simple
   scale_overlap
   scalemult
   vac2air_Ciddor
   vac2air_Morton
   writesp

stats
-----

Statistics-related functions.

.. currentmodule:: barak.stats

.. autosummary::
   :toctree: generated/

   binomial_confidence_interval
   binomial_min_max_limits
   blackbody_lam
   blackbody_nu
   poisson_confidence_interval
   poisson_min_max_limits

utilities
---------

Various general-use functions.

.. currentmodule:: barak.utilities

.. autosummary::
   :toctree: generated/

   Bunch
   adict
   adict.copy
   Gaussian
   addnoise
   autocorr
   between
   calc_Mstar_b
   combinations
   find_edges_true_regions
   get_data_path
   indexnear
   indgroupby
   indices_from_grid
   meshgrid_nd
   nan2num
   permutations
   poisson_noise
   stats
   wmean

voigt
-----

A fast implementation of the Voigt function.

.. currentmodule:: barak.voigt

.. autosummary::
   :toctree: generated/

   voigt
   voigt_slow
   voigt_wofz

Command line scripts
--------------------
====================== ==============================================================================================================================================
       ../scripts/cphd read a set of valid FITS key=value pairs from a text file and copy them to the the given fits file, with suffix _newhd added.                 
../scripts/extract_wcs Print the world coordinate system (wcs) information from a fits image header to a text file.                                                  
       ../scripts/fhdr Print the whole header or selected cards for a list of FITS files.                                                                            
      ../scripts/finfo Print a short summary for one or more FITS files.                                                                                             
../scripts/overwritehd read a set of valid FITS key=value pairs from a text file and use them to make a new header for the given fits file, with suffix _newhd added.
    ../scripts/qso_jhk Plot the spectrum of a QSO in the IR overlayed with atmospheric absorption and sky background emission.                                       
  ../scripts/run_nproc Run a shell command on a list of files using multiple processors.                                                                             
 ../scripts/sex2DS9reg Make a ds9 region file from a SExtractor catalogue.                                                                                           
====================== ==============================================================================================================================================


.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
