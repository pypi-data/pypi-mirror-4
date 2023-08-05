

import logging
import numpy
from numpy import *
import numpy.random
import objective
import innersolve

def sgd(f, x0, ndata, gtol=1e-5, maxiter=100, callback=None, props={}): 
    logger = logging.getLogger("phf.sgd")
    initialStep = props.get("SGDInitialStep", 0.01)
    SGDType = props.get("SGDType", 'SGD')
    stepScale = props.get("SGDStepScale", 0.5)
    averageSGD = props.get("averageSGD", False)

    n = len(x0)
    f = objective.Objective(f, ndata, n, props)
    
    x = copy(x0)
    xacum = zeros(n)
    accumed = 0

    gtot = zeros(n)
    gn = 0
    ggs = {}
    
    iteration = 0

    logger.info("SGD Training on %d points, %d dimensions", ndata, n)

    while iteration < maxiter:
        loss = 0.0
        
        for j in range(f.parts):
            (li, gi) = f.evalRandom(x)
            
            if SGDType == 'SAG':
                # This is INRIA's random averaged gradient approach
                gk = gi
                
                # recompute average gradient
                if ggs.has_key(i):
                    gtot = gtot - ggs[i] + gk
                    ggs[i] = copy(gk)
                else:
                    ggs[i] = copy(gk)
                    gtot += gk
                    gn += 1
                gavg = gtot/gn
                
                # Take constant step
                mu = initialStep
                x = x - mu * gavg
                
            else:
                mu = initialStep/pow(1.0 + stepScale*iteration, 0.75)
                x -= mu * gi
                
            if iteration > 0:
                xacum += x
                accumed += 1
           
            loss += li

        if averageSGD:
            if iteration == 0:
                xavg = x
            else:
                xavg = xacum / accumed
        else:
            xavg = x

        
        if callback is not None:
            (loss, gk) = f(x)
            callback(x, loss, gk, (iteration+1)*ndata)
        
            logger.info("SGD Pass %d complete. Step %2.4f, loss %2.4f gnorm: %1.2e", 
                    iteration, mu, loss, linalg.norm(gk))
        iteration += 1
    
    return x
