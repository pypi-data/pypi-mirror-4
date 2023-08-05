import math

def EffectiveAngle(E0,E,alpha,beta):
    """Calculates the effective collection angle
    
    Parameters
    ----------
    E0 : float
        electron beam energy in keV
    E : float
        energy loss in eV
    alpha : float
        convergence angle in mrad
    beta : float
        collection angle in mrad
        
    Returns
    -------
    float : effective collection angle in mrad
    
    Notes
    -----
    Code translated to Python from Egerton (second edition) page 420
    
    """	   
    E0 *= 1e3 # keV to eV
    if alpha == 0:
        return beta * 10**-3
    E0=10.**-3*E0 # In KeV
    E=float(E)
    alpha=float(alpha)
    beta=float(beta)
    TGT=E0*(1. + E0/1022.)/(1.+E0/511.)
    thetaE=E/TGT
    A2=alpha*alpha*1e-6
    B2=beta*beta*1e-6
    T2=thetaE*thetaE*1e-6
    eta1=math.sqrt((A2+B2+T2)**2-4.*A2*B2)-A2-B2-T2
    eta2=2.*B2*math.log(0.5/T2*(math.sqrt((A2+T2-B2)**2+4.*B2*T2)+A2+T2-B2))
    eta3=2.*A2*math.log(0.5/T2*(math.sqrt((B2+T2-A2)**2+4.*A2*T2)+B2+T2-A2))
#    ETA=(eta1+eta2+eta3)/A2/math.log(4./T2)
    F1=(eta1+eta2+eta3)/2/A2/math.log(1.+B2/T2)
    F2=F1
    if (alpha/beta)> 1 :
        F2=F1*A2/B2
    BSTAR=thetaE*math.sqrt(math.exp(F2*math.log(1.+B2/T2))-1.)
    return BSTAR # In mrad
