# ******NOTICE***************
# optimize.py module by Travis E. Oliphant
#
# You may copy and use this module as you see fit with no
# guarantee implied provided you keep this notice in all copies.
# *****END NOTICE************

# Minimization routines
"""This module contain the fmin minimisation algorithm (SIMPLEX) used by Masai

It is adapted from the optimize.py module by Travis E. Oliphant 
(`Scipy package <http://docs.scipy.org/doc/scipy-0.7.x/reference/generated/scipy.optimize.fmin.html>`_)

"""
__all__ = ['fmin']

import numpy
from numpy import atleast_1d, sqrt, asfarray

def is_array_scalar(x):
    """Test whether `x` is either a scalar or an array scalar.

    """
    return len(atleast_1d(x) == 1)

import __builtin__
pymin = __builtin__.min
pymax = __builtin__.max
__version__="0.7"
_epsilon = sqrt(numpy.finfo(float).eps)


def wrap_function(function, args):
    ncalls = [0]
    def function_wrapper(x):
        ncalls[0] += 1
        return function(x, *args)
    return ncalls, function_wrapper

def fmin(func, x0, args=(), xtol=1e-4, ftol=1e-4, maxiter=None, maxfun=None,
         full_output=0, disp=1, retall=0, callback=None):
    """
    Minimize a function using the downhill simplex algorithm.

    This algorithm only uses function values, not derivatives or second
    derivatives.

    Parameters
    ----------
    func : callable func(x,*args)
        The objective function to be minimized.
    x0 : ndarray
        Initial guess.
    args : tuple
        Extra arguments passed to func, i.e. ``f(x,*args)``.
    callback : callable
        Called after each iteration, as callback(xk), where xk is the
        current parameter vector.

    Returns
    -------
    xopt : ndarray
        Parameter that minimizes function.
    fopt : float
        Value of function at minimum: ``fopt = func(xopt)``.
    iter : int
        Number of iterations performed.
    funcalls : int
        Number of function calls made.
    warnflag : string
        Message of warning or completion
    allvecs : list
        Solution at each iteration.

    Other parameters
    ----------------
    xtol : float
        Relative error in xopt acceptable for convergence.
    ftol : number
        Relative error in func(xopt) acceptable for convergence.
    maxiter : int
        Maximum number of iterations to perform.
    maxfun : number
        Maximum number of function evaluations to make.
    full_output : bool
        Set to True if fopt and warnflag outputs are desired.
    disp : bool
        Set to True to print convergence messages.
    retall : bool
        Set to True to return list of solutions at each iteration.

    Notes
    -----
    Uses a Nelder-Mead simplex algorithm to find the minimum of function of
    one or more variables.

    References
    ----------
    Nelder, J.A. and Mead, R. (1965), "A simplex method for function
    minimization", The Computer Journal, 7, pp. 308-313
    Wright, M.H. (1996), "Direct Search Methods: Once Scorned, Now
    Respectable", in Numerical Analysis 1995, Proceedings of the
    1995 Dundee Biennial Conference in Numerical Analysis, D.F.
    Griffiths and G.A. Watson (Eds.), Addison Wesley Longman,
    Harlow, UK, pp. 191-208.

    """
    fcalls, func = wrap_function(func, args)
    x0 = asfarray(x0).flatten()
    N = len(x0)
    rank = len(x0.shape)
    if not -1 < rank < 2:
        raise ValueError("Initial guess must be a scalar or rank-1 sequence.")
    if maxiter is None:
        maxiter = N * 200
    if maxfun is None:
        maxfun = N * 200

    rho = 1; chi = 2; psi = 0.5; sigma = 0.5;
    one2np1 = range(1,N+1)

    if rank == 0:
        sim = numpy.zeros((N+1,), dtype=x0.dtype)
    else:
        sim = numpy.zeros((N+1,N), dtype=x0.dtype)
    fsim = numpy.zeros((N+1,), float)
    sim[0] = x0
    if retall:
        allvecs = [sim[0]]
    fsim[0] = func(x0)
    nonzdelt = 0.05
    zdelt = 0.00025
    for k in range(0,N):
        y = numpy.array(x0,copy=True)
        if y[k] != 0:
            y[k] = (1+nonzdelt)*y[k]
        else:
            y[k] = zdelt

        sim[k+1] = y
        f = func(y)
        fsim[k+1] = f

    ind = numpy.argsort(fsim)
    fsim = numpy.take(fsim,ind,0)
    # sort so sim[0,:] has the lowest function value
    sim = numpy.take(sim,ind,0)

    iterations = 1
    abort = False
    while (fcalls[0] < maxfun and iterations < maxiter and not abort):
        if (max(numpy.ravel(abs(sim[1:]-sim[0]))) <= xtol \
            and max(abs(fsim[0]-fsim[1:])) <= ftol):
            break

        xbar = numpy.add.reduce(sim[:-1],0) / N
        xr = (1+rho)*xbar - rho*sim[-1]
        fxr = func(xr)
        doshrink = 0

        if fxr < fsim[0]:
            xe = (1+rho*chi)*xbar - rho*chi*sim[-1]
            fxe = func(xe)

            if fxe < fxr:
                sim[-1] = xe
                fsim[-1] = fxe
            else:
                sim[-1] = xr
                fsim[-1] = fxr
        else: # fsim[0] <= fxr
            if fxr < fsim[-2]:
                sim[-1] = xr
                fsim[-1] = fxr
            else: # fxr >= fsim[-2]
                # Perform contraction
                if fxr < fsim[-1]:
                    xc = (1+psi*rho)*xbar - psi*rho*sim[-1]
                    fxc = func(xc)

                    if fxc <= fxr:
                        sim[-1] = xc
                        fsim[-1] = fxc
                    else:
                        doshrink=1
                else:
                    # Perform an inside contraction
                    xcc = (1-psi)*xbar + psi*sim[-1]
                    fxcc = func(xcc)

                    if fxcc < fsim[-1]:
                        sim[-1] = xcc
                        fsim[-1] = fxcc
                    else:
                        doshrink = 1

                if doshrink:
                    for j in one2np1:
                        sim[j] = sim[0] + sigma*(sim[j] - sim[0])
                        fsim[j] = func(sim[j])

        ind = numpy.argsort(fsim)
        sim = numpy.take(sim,ind,0)
        fsim = numpy.take(fsim,ind,0)

        if callback is not None:
            abort = callback(sim[0], args[0], fcalls[0], iterations, min(fsim))
        iterations += 1
        if retall:
            allvecs.append(sim[0])

    x = sim[0]
    fval = min(fsim)
    warnflag = ""
    
    if abort:
        warnflag = "Warning: User termination - optimization was not finished"

    elif fcalls[0] >= maxfun:
        warnflag = "Warning: Maximum number of function evaluations has "\
                  "been exceeded."
    elif iterations >= maxiter:
        warnflag = "Warning: Maximum number of iterations has been exceeded"
    else:
        warnflag = "Optimization terminated successfully.\n"
        warnflag +="The returned value satisfies the termination criteria " \
                  "(using tolerance = %s)\n"% str(xtol)
        warnflag +="         Current function value: %f\n" % fval
        warnflag +="         Iterations: %d\n" % iterations
        warnflag +="         Function evaluations: %d\n" % fcalls[0]


    if full_output:
        retlist = x, fval, iterations, fcalls[0], warnflag
        if retall:
            retlist += (allvecs,)
    else:
        retlist = x
        if retall:
            retlist = (x, allvecs)

    return retlist

if __name__ == "__main__":
    pass
