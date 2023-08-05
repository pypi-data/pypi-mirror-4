# Discrete wavelet transform

import numpy as np

try:
    from scipy.ndimage import convolve1d
    _scipy_loaded = True
except :
    _scipy_loaded = False

def upsample(v):
    out = np.zeros(len(v)*2-1)
    out[::2] = v
    return out

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

def mirrorpd(k, L):
    if 0 <= k < L : return k
    else: return -(k)%L


# Redundant, modwt, a' trous
def dec_atrous(sig, lev, phi=np.array([1./16, 1./4, 3./8, 1./4, 1./16])):
    L = len(sig) 
    padlen = len(phi)
    assert L > padlen
    if _scipy_loaded:
        apprx = convolve1d(sig, phi, mode='mirror')
    else:
        indices = map(lambda i: mirrorpd(i, L),
                      range(-padlen, 0) + range(0,L) + range(L, L+padlen))
        padded_sig = sig[indices]
        apprx = np.convolve(padded_sig, phi, mode='same')[padlen:padlen+L]
    w = (sig - apprx) # wavelet coefs
    if lev <= 0: return sig
    elif lev == 1 or L < len(upsample(phi)): return [w, apprx]
    else: return [w] + dec_atrous(apprx, lev-1, upsample(phi))


# version with direct convolution (slow)
def dec_atrous1(v, lev, phi=np.array([1./16, 1./4, 3./8, 1./4, 1./16])):
    coefs = []
    cprev = v.copy()
    cnext = np.zeros(v.shape)
    L,lphi = len(v), len(phi)
    phirange = np.arange(lphi) - int(lphi/2)
    Ll = xrange(L)
    for j in xrange(lev):
        phiind = (2**j)*phirange
	cvals = [np.sum(phi*cprev[(l+phiind)%L]) for l in  Ll]
        coefs.append(cprev - cvals)
        cprev = np.array(cvals)
    return coefs + [cprev]
