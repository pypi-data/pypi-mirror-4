import numpy as np
import matplotlib.pyplot as pl
import matplotlib.transforms as mtran

from utilities import between, Gaussian, stats, indexnear
from convolve import convolve_psf
from io import loadobj, saveobj
from interp import AkimaSpline

from absorb import readatom, find_tau

import os

class InteractiveCoFit(object):
    help_message = """
'a'        : add a new continuum point
'd'        : delete the nearest point
's'        : smooth the spectrum
'k'        : keep continuum
'q'        : quit without keeping continuum
"""
    def __init__(self, wa, fl, er, contpoints, nbin=8, fig=None):
        """ Initialise figure, plots and variables.

        Parameters
        ----------
        wa :   Wavelengths
        fl :   Fluxes
        er :   One sigma errors
        nbin : int (8)
            Number of pixels to bin arrays in wavelength. Default 8.
        contpoints : list of x,y tuple pairs (None)
            The points through which a cubic spline is passed,
            defining the continuum.
        redshift : float (None)
            Redshift used to plot reference emission lines.
        atmos : list of wavelength pairs (None)
            Regions of atmospheric absorption to plot.

        Notes
        -----
        Updates the following attributes:
        
         self.spec :  Dictionary of wa, fl, er.
         self.contpoints :  Points used to define the continuum.
         self.nbin :  The input nbin value.
         self.markers :  Dictionary of matplotlib plotting artists.
         self.connections :  Callback connections.
         self.fig :  The plotting figure instance.
        """
        #setup
        #print co
        self.WMIN_LYA = 1040
        self.WMAX_LYA = 1190

        self.spec = dict(wa=wa, fl=fl, er=er, co=co)
        self.nbin = nbin
        self.breaks = [wa[0], wa[-1]] # wavelengths of breaks in the continuum
        self.contpoints = list(contpoints)
        if os.path.lexists('./_knots.sav'):
            c = raw_input('temporary knots file exists, use these knots? (y) ')
            if c.lower() != 'n':
                self.contpoints = loadobj('./_knots.sav')

        self.markers = dict()
        self.art_fl = None
        if fig is None:
            self.fig = pl.figure()
        else:
            self.fig = fig
        # disable any existing key press callbacks
        cids = list(fig.canvas.callbacks.callbacks['key_press_event'])
        for cid in cids:
            fig.canvas.callbacks.disconnect(cid)

        self.connections = []
        self.continuum = None
        self.finished = False
        self.smoothby = None
        self.plotinit()
        self.update()
        self.modifypoints()
        pl.draw()

    def calc_tau(self):
        """ Include absorption from a transition (DLA). """
        lines = ([self.zabs, self.logN, self.b])
        return find_tau(self.wa, lines, atom)

    def plotinit(self):
        """ Set up the figure and do initial plots.

        Updates the following attributes:

          self.markers
        """
        wa,fl,er = [self.spec[k][0:-1:self.nbin] for k in 'wa fl er'.split()]
        # axis for spectrum & continuum
        a0 = self.fig.add_axes((0.05,0.1,0.9,0.6))
        a0.set_autoscale_on(0)
        # axis for residuals
        a1 = self.fig.add_axes((0.05,0.75,0.9,0.2),sharex=a0)
        a1.set_autoscale_on(0)
        a1.axhline(0,color='k',alpha=0.7, zorder=99)
        a1.axhline(1,color='k',alpha=0.7, zorder=99)
        a1.axhline(-1,color='k',alpha=0.7, zorder=99)
        a1.axhline(2,color='k',linestyle='dashed',zorder=99)
        a1.axhline(-2,color='k',linestyle='dashed',zorder=99)
        m0, = a1.plot([0],[0],'.r', ms=6, alpha=0.5)
        a1.set_ylim(-4, 4)
        a0.axhline(0, color='0.7')
        self.art_fl, = a0.plot(wa, fl, 'b', lw=0.5, linestyle='steps-mid')
        a0.plot(wa, er, lw=0.5, color='orange')
        m1, = a0.plot([0], [0], 'r', alpha=0.7)
        m2, = a0.plot([0], [0], 'o', mfc='None',mew=1, ms=8, mec='r', picker=5,
                      alpha=0.7)
        a0.set_xlim(min(wa), max(wa))
        good = (er > 0) & ~np.isnan(fl)
        ymin = -5 * np.median(er[good])
        ymax = 2 * sorted(fl[good])[int(good.sum()*0.95)]
        a0.set_ylim(ymin, ymax)
        a0.text(0.9,0.9, 'z=%.2f' % self.redshift, transform=a0.transAxes)

        # for histogram
        trans = mtran.blended_transform_factory(a1.transAxes, a1.transData)
        hist, = a1.plot([], [], color='k', transform=trans)
        x = np.linspace(-3,3)
        a1.plot(Gaussian(x,0,1,0.05), x, color='k', transform=trans, lw=0.5)

        self.fig.canvas.draw()
        self.markers.update(contpoints=m2, cont=m1, resid=m0, hist_left=hist)

    def update(self):
        """ Calculates the new continuum, residuals and updates the plots.


        Updates the following attributes:

          self.markers
          self.continuum
        """
        wa,fl,er = (self.spec[key] for key in 'wa fl er'.split())
        co = np.empty(len(wa))
        co.fill(np.nan)
        for b0,b1 in zip(self.breaks[:-1], self.breaks[1:]):
            cpts = [(x,y) for x,y in self.contpoints if b0 <= x <= b1]
            if len(cpts) == 0:
                continue 
            spline = AkimaSpline(*zip(*cpts))
            i,j = wa.searchsorted([b0,b1])
            co[i:j] = spline(wa[i:j])
        
        resid = (fl - co) / er
        # histogram
        bins = np.arange(0, 5+0.1, 0.2)
        w0,w1 = self.fig.axes[1].get_xlim()
        x,_ = np.histogram(resid[between(wa, w0, w1)],
                           bins=bins)
        b = np.repeat(bins, 2)
        X = np.concatenate([[0], np.repeat(x,2), [0]])
        Xmax = X.max()    
        X = 0.05 * X / Xmax
        self.markers['hist_left'].set_data(X, b)

        self.markers['contpoints'].set_data(zip(*self.contpoints))
        nbin = self.nbin
        self.markers['cont'].set_data(wa[::nbin], co[::nbin])
        self.markers['resid'].set_data(wa[::nbin], resid[::nbin])
        if self.smoothby is not None:
            sfl = convolve_psf(fl, self.smoothby)
            self.art_fl.set_data(wa, sfl)
        else:
            self.art_fl.set_data(wa, fl)
        self.continuum = co
        saveobj('_knots.sav', self.contpoints, overwrite=True)
        self.fig.canvas.draw()

    def on_keypress(self, event):
        """ Add or remove a continuum point.

        Updates:
        
         self.contpoints
        """
        if event.key == 'q':
            for item in self.connections:
                self.fig.canvas.mpl_disconnect(item)
            self.contpoints = None
            self.continuum = None
            self.finished = True
            return
        if event.key == 'k':
            for item in self.connections:
                self.fig.canvas.mpl_disconnect(item)
            self.finished = True
            return
        if event.inaxes != self.fig.axes[0]:  return
        
        if event.key == 'a':
            # add a point to contpoints
            x,y = event.xdata,event.ydata
            if x not in zip(*self.contpoints)[0]:
                self.contpoints.append((x,y))
                self.update()
        elif event.key == 'd':
            # remove a point from contpoints
            contx,conty = zip(*self.contpoints)
            sep = np.hypot(event.xdata - contx, event.ydata - conty)
            self.contpoints.remove(self.contpoints[sep.argmin()])
            self.update()
        elif event.key == 's':
            c = raw_input('New FWHM in pixels of Gaussian to convolve with? '
                          '(blank for no smoothing) ')
            if c == '':
                # restore spectrum
                self.smoothby = None
                self.update()
            else:
                try:
                    fwhm = float(c)
                except TypeError:
                    print 'FWHM must be a floating point number >= 1'
                if fwhm < 1:
                    self.smoothby = None
                else:
                    self.smoothby = fwhm
                self.update()
        elif event.key == '?':
            print self.help_message

    def on_button_release(self, event):
        self.update()

    def modifypoints(self):
        """ Add/remove continuum points."""
        print self.help_message
        id1 = self.fig.canvas.mpl_connect('key_press_event',self.on_keypress)
        id2 = self.fig.canvas.mpl_connect('button_release_event',self.on_button_release)
        self.connections.extend([id1, id2])
