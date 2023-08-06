# -*- coding: utf-8 -*-

# Copyright (C) 2013 Michael Hogg

# This file is part of pyvXRAY - See LICENSE.txt for information on usage and redistribution

# cython: profile=True
# cython: boundscheck=False
# cython: wraparound=False
# cython: infer_types=True
# cython: nonecheck=False

import numpy as np
cimport numpy as np
from numpy.linalg import lapack_lite
from libc.math cimport fabs
ctypedef np.float64_t float64
ctypedef np.int32_t int32

# Note: fmin and fmax are not included in math.h for MSVC! (Although they are included
#       in gcc). Work-around is to write own functions
cdef double fmax(double a, double b):
    if (a>=b): return a
    else:      return b

cdef double fmin(double a, double b):
    if (a<=b): return a
    else:      return b


# Packed structure for use in numpy record array 
cdef packed struct mappedPoint:
    int32 label, cte
    float64 g,h,r    


def tetShapeFunction(np.ndarray[float64, ndim=1] nv, np.ndarray[float64, ndim=1] ipc):
    """Shape function for second order tetrahedral (C3D10) element"""    
    cdef double[:] ipcmv = ipc
    return cTetShapeFunction(nv,ipcmv)


cdef double cTetShapeFunction(double[:] nv, double[:] ipc):
    """Shape function for second order tetrahedral (C3D10) element"""
    cdef double U,g,h,r
    g = ipc[0]; h=ipc[1]; r=ipc[2]
    U = (2.0*(1.0-g-h-r)-1.0)*(1.0-g-h-r)*nv[0]+(2.0*g-1.0)*g*nv[1]+ \
        (2.0*h-1.0)*h*nv[2]+(2.0*r-1.0)*r*nv[3]+4.0*(1.0-g-h-r)*g*nv[4]+ \
         4.0*g*h*nv[5]+4.0*(1.0-g-h-r)*h*nv[6]+4.0*(1.0-g-h-r)*r*nv[7]+ \
         4.0*g*r*nv[8]+4.0*h*r*nv[9]
    return U


cdef int cTetShapeFunctionDerivative(double[:] nvU, double[:] ipc, double[:] dUdghr):
    """First derivative of shape function for second order tetrahedral (C3D10) element"""    
    cdef double g,h,r
    g = ipc[0]; h=ipc[1]; r=ipc[2]   
    dUdghr[0] = (4.0*(g+h+r-1.0)+1.0)*nvU[0] + (4.0*g-1.0)*nvU[1] + \
                 4.0*(1.0-2.0*g-h-r)*nvU[4]  +  4.0*h*nvU[5] - 4.0*h*nvU[6] - \
                 4.0*r*nvU[7] + 4.0*r*nvU[8]
    dUdghr[1] = (4.0*(g+h+r-1.0)+1.0)*nvU[0] + (4.0*h-1.0)*nvU[2] - \
                 4.0*g*nvU[4] + 4.0*g*nvU[5] +  4.0*(1.0-g-2.0*h-r)*nvU[6] - \
                 4.0*r*nvU[7] + 4.0*r*nvU[9]
    dUdghr[2] = (4.0*(g+h+r-1.0)+1.0)*nvU[0] + (4.0*r-1.0)*nvU[3] - \
                 4.0*g*nvU[4] - 4.0*h*nvU[6] +  4.0*(1.0-g-h-2.0*r)*nvU[7] + \
                 4.0*g*nvU[8] + 4.0*h*nvU[9]
    return 0

    
cdef int convert3Dto1Dindex(int i, int j, int k, int NX, int NY, int NZ):
    """Converts 3D array index to 1D array index"""
    return i+j*NX+k*NX*NY  
    

cdef double absmaxerror(double[:] error):
    """Calculates absolute maximum of values in list"""
    cdef int i
    cdef double absmax
    absmax = fabs(error[0])
    for i in range(1,error.shape[0]):
        absmax = fmax(absmax,fabs(error[i]))
    return absmax    


cdef double minval(double[:] arr):
    """Get minimum value in list"""
    cdef int i, numvals = arr.shape[0]
    cdef double minimum = arr[0]
    for i in range(1,numvals):
        minimum = fmin(minimum,arr[i])
    return minimum
    
    
cdef double maxval(double[:] arr):
    """Get maximum value in list"""
    cdef int i, numvals = arr.shape[0]
    cdef double maximum = arr[0]
    for i in range(1,numvals):
        maximum = fmax(maximum,arr[i])
    return maximum  
    
           
cdef int getNearest(double[:] arr, double val, int side):
    """Get nearest index to value in list"""    
    cdef int indx, i, numvals = arr.shape[0]
    if val<=arr[0]: return 0
    if val> arr[numvals-1]: return numvals-1
    for i in range(numvals-1):
        if val>arr[i] and val<=arr[i+1]:
            if side==0: return i  
            if side==1: return i+1            
 
       
def createElementMap(dict nodeList, np.ndarray[int32,ndim=1] nConnect_labels, 
                                    np.ndarray[int32,ndim=2] nConnect_connectivity,                    
                                    double[:] x, double[:] y, double[:] z):
    """Creates a map between a list of points and a list of second order tetrahedral (C3D10) elements"""

    cdef int i,j,k,e,nlabel,NX,NY,NZ,iLow,jLow,kLow,iUpp,jUpp,kUpp,numElems,numNodesPerElem,elemLabel
    cdef double xLow,yLow,zLow,xUpp,yUpp,zUpp
    cdef double[:] tetXcoords=np.empty(10),tetYcoords=np.empty(10),tetZcoords=np.empty(10)
    cdef double[:] gridPointCoords=np.empty(3),ipc=np.zeros(3),error=np.zeros(3) 
    cdef double[:] dXdghr=np.empty(3),dYdghr=np.empty(3),dZdghr=np.empty(3)
    cdef np.ndarray[float64,ndim=2,mode='c'] JM=np.zeros((3,3),order='c'), f=np.zeros((3,1),order='c')
    cdef np.ndarray[int32,  ndim=1,mode='c'] pivots=np.zeros(3,np.intc)     
    
    NX=x.shape[0]; NY=y.shape[0]; NZ=z.shape[0]
    numGridPoints = NX*NY*NZ
    cdef np.ndarray[mappedPoint,ndim=1] elementMap = np.zeros(numGridPoints,dtype=np.dtype([('label',np.int32),('cte',np.int32),
                                                             ('g',np.float64),('h',np.float64),('r',np.float64)]))
    # Set default values. Label = index+1, and cte=0 if no intersection is found
    for i in range(numGridPoints):    
        elementMap[i].label = i+1
    
    numElems = nConnect_labels.shape[0]
    numNodesPerElem = nConnect_connectivity.shape[1]
    for e in range(numElems): 
        
        elemLabel = nConnect_labels[e]

        for i in range(numNodesPerElem):            
            nlabel = nConnect_connectivity[e,i] 
            tetXcoords[i] = nodeList[nlabel][0]
            tetYcoords[i] = nodeList[nlabel][1]
            tetZcoords[i] = nodeList[nlabel][2] 
            
        xLow = minval(tetXcoords); yLow = minval(tetYcoords); zLow = minval(tetZcoords)
        xUpp = maxval(tetXcoords); yUpp = maxval(tetYcoords); zUpp = maxval(tetZcoords)    

        iLow = getNearest(x,xLow,0); jLow = getNearest(y,yLow,0); kLow = getNearest(z,zLow,0) 
        iUpp = getNearest(x,xUpp,1); jUpp = getNearest(y,yUpp,1); kUpp = getNearest(z,zUpp,1) 
        
        for k in range(kLow,kUpp+1):
            for j in range(jLow,jUpp+1):
                for i in range(iLow,iUpp+1):
                    gridPointCoords[0] = x[i] 
                    gridPointCoords[1] = y[j] 
                    gridPointCoords[2] = z[k]
                    foundIntersection  = testPointInElement(gridPointCoords,tetXcoords,tetYcoords,tetZcoords,
                                                           ipc,dXdghr,dYdghr,dZdghr,error,JM,f,pivots)
                    if foundIntersection:
                        gridPointIndex = convert3Dto1Dindex(i,j,k,NX,NY,NZ)
                        elementMap[gridPointIndex].cte   = elemLabel                        
                        elementMap[gridPointIndex].g     = ipc[0]
                        elementMap[gridPointIndex].h     = ipc[1]
                        elementMap[gridPointIndex].r     = ipc[2]
    
    return elementMap


cdef int testPointInElement(double[:] point,  double[:] nvX,    double[:] nvY,    
                            double[:] nvZ,    double[:] ipc,    double[:] dXdghr, 
                            double[:] dYdghr, double[:] dZdghr, double[:] dghr, 
                            np.ndarray[float64,ndim=2,mode='c'] JM, 
                            np.ndarray[float64,ndim=2,mode='c'] f, 
                            np.ndarray[int32,  ndim=1,mode='c'] pivots):
                                
    """Tests if a point lies within a second order tetrahedral (C3D10) element"""
    
    cdef int maxIter,numIter,result
    cdef double tol,maxerror,lowLim,uppLim,pvX,pvY,pvZ

    # Solver parameters
    maxIter=50; tol=1.0e-6
    
    # Set initial values
    numIter=1; maxerror=1.0; ipc[0]=0.5; ipc[1]=0.5; ipc[2]=0.5

    # Run iterative loop to find iso-parametric coordinates ipc=g,h,r using Newton's method
    while (numIter<=maxIter):

        # Form vector f
        pvX    = cTetShapeFunction(nvX,ipc)
        pvY    = cTetShapeFunction(nvY,ipc)
        pvZ    = cTetShapeFunction(nvZ,ipc)
        f[0,0] = -(pvX-point[0])
        f[1,0] = -(pvY-point[1])
        f[2,0] = -(pvZ-point[2])
        
        # Form Jacobian matrix JM
        cTetShapeFunctionDerivative(nvX,ipc,dXdghr)
        cTetShapeFunctionDerivative(nvY,ipc,dYdghr)
        cTetShapeFunctionDerivative(nvZ,ipc,dZdghr)
        JM[0,0] = dXdghr[0]; JM[0,1] = dYdghr[0]; JM[0,2] = dZdghr[0]
        JM[1,0] = dXdghr[1]; JM[1,1] = dYdghr[1]; JM[1,2] = dZdghr[1]
        JM[2,0] = dXdghr[2]; JM[2,1] = dYdghr[2]; JM[2,2] = dZdghr[2]        
        
        # Solve for change in isoparametric coordinates. NOTE: In call to lapack_dgesv,
        # f is modified to be the result dg,dh,dr. JM is also modified, but this is not needed 
        lapack_dgesv(JM,f,pivots)
        for i in range(3): 
            dghr[i]  = f[i,0]
            ipc[i]  += dghr[i]

        # Exit if error below tolerance
        maxerror = absmaxerror(dghr)
        if maxerror <= tol: break
        
        # Increment loop counter
        numIter+=1        

    # Test if point lies within tet element
    lowLim=0.0-tol; uppLim=1.0+tol;     
    if (maxerror<=tol) and (ipc[0]+ipc[1]+ipc[2]<=uppLim)      and \
                           (ipc[0]>=lowLim and ipc[0]<=uppLim) and \
                           (ipc[1]>=lowLim and ipc[1]<=uppLim) and \
                           (ipc[2]>=lowLim and ipc[2]<=uppLim):
        return 1
    else:
        return 0


cdef lapack_dgesv(np.ndarray[float64,ndim=2,mode='c'] A, 
                  np.ndarray[float64,ndim=2,mode='c'] b, 
                  np.ndarray[int32,  ndim=1,mode='c'] pivots): 
    """Direct call to lapack function dgesv to solve system of linear equations Ax=b"""                      
    cdef int n_eq  = A.shape[0]  # Number of equations
    cdef int n_rhs = b.shape[1]  # Number of vectors on rhs of equation
    cdef dict results = lapack_lite.dgesv(n_eq, n_rhs, A, n_eq, pivots, b, n_eq, 0)
