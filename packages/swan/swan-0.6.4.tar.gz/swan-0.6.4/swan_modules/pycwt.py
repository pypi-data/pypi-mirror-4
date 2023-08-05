# Continuous wavelet transfrom via Fourier transform
# Collection of routines for wavelet transform via FFT algorithm


#-- Some naming and other conventions --
# use f instead of omega wherever rational/possible
# *_ft means Fourier transform

#-- Some references --
# [1] Mallat, S.  A wavelet tour of signal processing
# [2] Addison, Paul S. The illustrated wavelet transform handbook
# [3] Torrence and Compo. A practical guide to wavelet
#     analysis. Bulletin of American Meteorological Society. 1998, 79(1):61-78

import numpy as np
from numpy.fft import fft, ifft, fftfreq

_maxshape_ = 5e6

def memsafe_arr(shape, dtype):
    import tempfile as tmpf
    N = shape[0] * shape[1]
    if N < _maxshape_:
        return np.zeros(shape, dtype=dtype)
    else:
        print "Using memory-mapped arrays..."
        _tmpfile = tmpf.TemporaryFile('w+')
        return np.memmap(_tmpfile, dtype=dtype, shape=shape)
        
    

#try:
#    from scipy.special import gamma
#except:

pi = np.pi

try:
    from scipy.special import gamma
    class DOG:
        """Derivative of Gaussian, general form"""
        # Incomplete, as the general form of the mother wavelet
        # would require symbolic differentiation.
        # Should be enough for the CWT computation, though

        def __init__(self, m = 1.):
            self.order = m
            self.fc = (m+.5)**.5 / (2*pi)
            self.f0 = self.fc
    
        def psi_ft(self, f):
            c = 1j**self.order / np.sqrt(gamma(self.order + .5)) #normalization
            w = 2*pi*f
            return c * w**self.order * np.exp(-.5*w**2)
except:
    class DOG:
        def __init__(self,*args):
            print "Couldn't create DOG wavelet because scipy is unavailable"
            return None
        

class Mexican_hat:
    def __init__(self, sigma = 1.0):
        self.sigma = sigma
        self.fc = .5 * 2.5**.5 / pi
        self.f0 = self.fc
    def psi_ft(self, f):
        """Fourier transform of the Mexican hat wavelet"""
        c = np.sqrt(8./3.) * pi**.25 * self.sigma**2.5 
        wsq = (2. * pi * f)**2.
        return -c * wsq * np.exp(-.5 * wsq * self.sigma**2.)
    def psi(self, tau):
        """Mexian hat wavelet as described in [1]"""
        xsq = (tau / self.sigma)**2.
        c = 2 * pi**-.25 / np.sqrt(3 * self.sigma) # normalization constant from [1]
        out =  c * (1 - xsq) * np.exp(-.5 * xsq)
        out *= (tau < 6) * (tau > -6) # make it 'compact support'
        return out
    def cone(self, f):
        "e-folding time [Torrence&Compo]. For frequencies"
        return self.f0*2.0**0.5 / f
    def cone_s(self, s):
        "e-folding time [Torrence&Compo]. For scales"
        return 2.**0.5*s
    def set_f0(self, f0):
        pass

def heavyside(x):
    return 1.0*(x>0.0)

class Morlet:
    def __init__(self, f0 = 1.5):
        self.set_f0(f0)
    def psi(self, t):
        pi**0.25 * exp(-t**2 / 2.) * exp(2j*pi*self.f0*t) #[3]
    def psi_ft(self, f):
        """Fourier transform of the approximate Morlet wavelet
            f0 should be more than 0.8 for this function to be
            correct."""
        # [3]
        coef = (pi**-.25) * heavyside(f)
        return  coef * np.exp(-.5 * (2. * pi * (f - self.f0))**2.)
    def sigma_t_s(self,s):
        """
        Heisenberg box width for scales [Addison]
        s/sqrt(2)

        """
        return s/np.sqrt(2)

    def sigma_f_s(self, s):
        """
        Heisenberg box height for scales [Addison]
        s*sqrt(2)/4
        """
        return 1.0/(s*pi*np.sqrt(8.0))

    def sigma_f_f(self,f):
        """
        Heisenberg box height in frequencies
        s*sqrt(2)/4
        """
        return self.sigma_f_s(self.f0/f)

    def cone(self, f):
        "e-folding time [Addison]. For frequencies"
        return self.f0/(f*2.0**0.5)
    def cone_s(self, s):
        "e-folding time [Addison]. For scales"
        return self.sigma_t_s(s)
    def set_f0(self, f0):
        self.f0 = f0
        #self.fc = f0


def next_pow2(x):
    return 2.**np.ceil(np.log2(x))

def pad_func(ppd):
    func = None
    if ppd == 'zpd':
        func = lambda x,a:  x*0.0
    elif ppd == 'cpd':
        func = lambda x,a:  x*a
    return func
    
def evenp(n):
    return not n%2

def cwt_a(signal, scales, sampling_scale = 1.0,
          wavelet=Mexican_hat(),
          ppd = 'zpd',
          verbose = False,):
    """ Continuous wavelet transform via fft. Scales version."""
    import sys
    siglen = len(signal)

    if hasattr(wavelet, 'cone_s'):
        needpad = wavelet.cone_s(np.max(scales))
    else:
        needpad = 1.2*np.max(scales)

    if siglen < 5e5: # only do expansion up to next ^2 for short signals
        ftlen = int(next_pow2(siglen + 2*needpad))
    else:
        if not evenp(siglen) :
            siglen -= 1
            signal = signal[:-1]
        ftlen = int(siglen + 2*needpad)

    padlen1 = int((ftlen - siglen)/2)
    padlen2 = evenp(siglen) and padlen1 or padlen1+1
    
    padded_signal = np.ones(ftlen)
    padfunc = pad_func(ppd)
    padded_signal[:padlen1] = padfunc(padded_signal[:padlen1],signal[0])
    padded_signal[-padlen2:] = padfunc(padded_signal[-padlen2:],signal[-1])
    padded_signal[padlen1:-padlen2] = signal

    signal_ft = fft(padded_signal)     # FFT of the signal
    del padded_signal
    ftfreqs = fftfreq(ftlen, sampling_scale)  # FFT frequencies

    psi_ft = wavelet.psi_ft
    coef = np.sqrt(2*pi/sampling_scale)

    ### version with map is slower :(
    #def _ls(s):
    #    return ifft(signal_ft*coef*(s**0.5)*np.conjugate(psi_ft(s*ftfreqs)))[padlen:-padlen]
    #xx = map(_ls, scales)
    #W = np.array(xx)

    ### matrix version
    scales = scales.reshape(-1,1)
    #s_x_ftf = np.dot(scales, ftfreqs.reshape(1,-1))
    #psi_ft_bar = np.conjugate(psi_ft(s_x_ftf))
    #psi_ft_bar *= coef*np.sqrt(scales)
    #W = ifft( psi_ft_bar * signal_ft.reshape(1,-1))[:,padlen1:-padlen2]
    #return W

    ## create the result matrix beforehand
    #W = np.zeros((len(scales), siglen), 'complex')
    W = memsafe_arr((len(scales), siglen), 'complex')
    ## Now fill in the matrix
    for n,s in enumerate(scales):
        if verbose :
            sys.stderr.write('\r Processing scale %04d of %04d'%(n+1,len(scales)))
        psi_ft_bar = np.conjugate(psi_ft(s * ftfreqs))
        psi_ft_bar *= coef*np.sqrt(s) # Normalization from [3]
        W[n,:] = ifft(signal_ft * psi_ft_bar)[padlen1:-padlen2]
    return W


def cwt_f(signal, freqs, Fs=1.5, wavelet = Morlet(), ppd = 'zpd', verbose=False):
    """Continuous wavelet transform -- frequencies version"""
    scales = wavelet.f0/freqs
    dt = 1./Fs
    return cwt_a(signal, scales, dt, wavelet, ppd, verbose=verbose)


def eds(x, f0=1.5):
    "Energy density surface [2,3]"
    ## Update, simulations with MK (as in [3]) suggest that I
    ## shouldn't divide by f0 to obtain correct normalisation,
    ## e.g. 1 s.d. is mean for white noise signal
    #return abs(x)**2/f0
    return abs(x)**2

def real(x, *args):
    return x.real

def cwt_phase(x, *args):
    return np.arctan2(x.imag, x.real)


def xwt_f(sig1, sig2, freqs, Fs=1.0, wavelet=Morlet()):
    "Cross-wavelet coeficients for 2 signals"
    cwtf = lambda x: cwt_f(x, freqs, Fs, wavelet)
    return xwt(cwtf(sig1),cwtf(sig2))

def absxwt_f(sig1, sig2, freqs, Fs=1.0, wavelet=Morlet()):
    "Cross-wavelet power for 2 signals"
    return abs(xwt_f(sig1,sig2, freqs, Fs, wavelet))/wavelet.f0**0.5

def absxwt_a(sig1, sig2, scales, dt=1.0, wavelet=Morlet()):
    "Cross-wavelet power for 2 signals"
    Fs = 1./dt
    freqs = wavelet.f0/scales
    return abs(xwt_f(sig1,sig2, freqs, Fs, wavelet))/wavelet.f0**0.5


def xwt(wcoefs1,wcoefs2):
    "Cross wavelet transform for 2 sets of coefficients"
    return wcoefs1*wcoefs2.conjugate()

def absxwt(wcoefs1,wcoefs2, f0=1.5):
    "Cross-wavelet power for 2 sets of coefficients"
    ## Why do I divide by f_0^2 here?
    return  abs(xwt(wcoefs1,wcoefs2))/f0**0.5

def wtc_a(sig1, sig2, scales, dt=1.0, wavelet=Morlet()):
    cwta = lambda x: cwt_a(x, scales, dt, wavelet)
    return coherence_a(cwta(sig1), cwta(sig2), scales, dt, wavelet)


def wtc_f(sig1, sig2, freqs, Fs=1.0, wavelet=Morlet()):
    cwtf = lambda x: cwt_f(x, freqs, Fs, wavelet)
    return coherence_f(cwtf(sig1), cwtf(sig2), freqs, Fs, wavelet.f0)

def coherence_a(x,y,scales,dt,f0=1.5):
    # almost not useful 
    #scor =np.ones(x.shape[1])[:,np.newaxis] * scales
    #scor = np.transpose(scor)
    sx = wsmooth_a(abs(x)**2,scales,dt)
    sy= wsmooth_a(abs(y)**2,scales,dt)
    sxy = wsmooth_a((x*y.conjugate()), scales, dt)
    return abs(sxy)**2/(sx.real*sy.real)

def coherence_f(x,y,freqs, Fs=1.0, f0=1.5):
    return coherence_a(x,y,f0/freqs, 1.0/Fs, f0)

def cphase(x,y):
    #hard to interprete :(
    d = xwt(x,y)
    return np.arctan2(d.imag, d.real)



def wsmooth_a(coefs, scales, dt = 1.0, wavelet=Morlet()):
    "Smoothing of wavelet coefs. Scales version"
    #G = lambda omega,s: np.exp(-0.5 * s**2.0 *omega**2.0) # Literature
    G = lambda omega,s: np.exp(-0.25 * s**2.0 *omega**2.0) 

    W = np.zeros(coefs.shape, 'complex')
    fftom = 2*pi*fftfreq(coefs.shape[1], dt) 

    for n,s in enumerate(scales):
        W[n,:] = ifft(fft(coefs[n,:]) * G(fftom, s/dt))

    # TODO: scale smoothing
    return W


import time 
def speed_test(sig_len, nscales = 512, N = 100, ppd='zpd',wavelet=Morlet()):
    tick = time.clock()
    s = np.random.randn(sig_len)
    scales = np.linspace(0.5, sig_len/4.0, nscales)
    for j in xrange(N):
        eds = cwt_a(s, scales, sampling_scale = 1.0, ppd = ppd,
                    wavelet=wavelet)
    tock =  time.clock() - tick
    print tock
    return tock
