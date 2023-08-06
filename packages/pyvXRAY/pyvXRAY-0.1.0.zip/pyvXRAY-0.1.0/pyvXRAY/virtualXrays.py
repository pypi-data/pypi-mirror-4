# -*- coding: utf-8 -*-

# Copyright (C) 2013 Michael Hogg

# This file is part of pyvXRAY - See LICENSE.txt for information on usage and redistribution

import numpy
from abaqus import session
from abaqusConstants import ELEMENT_NODAL
from cythonMods import createElementMap, tetShapeFunction
from PIL import Image, ImageFilter
from odbAccess import OdbType
import os

# ~~~~~~~~~~

def convert3Dto1Dindex(i,j,k,NX,NY,NZ):
    """Converts 3D array index to 1D array index"""
    index = i+j*NX+k*NX*NY
    return index
    
# ~~~~~~~~~~
  
def convert1Dto3Dindex(index,NX,NY,NZ):
    """Converts 1D array index to 1D array index"""
    k = index / (NX*NY)
    j = (index - k*NX*NY) / NX
    i = index - k*NX*NY - j*NX
    return [i,j,k]
    
# ~~~~~~~~~~   

def transformPoint(TM,point):
    """Transforms point using supplied transform"""
    point = numpy.append(point,1.0)
    return numpy.dot(TM,point)[:3]
    
# ~~~~~~~~~~      

def createTransformationMatrix(Ma,Mb,Vab,rel='a'):
    """
    Creates a transformation matrix that can be used to transform a point from csys a to csys b.
    Ma  = 3x3 matrix containing unit vectors of orthogonal coordinate directions for csys a
    Mb  = 3x3 matrix containing unit vectors of orthogonal coordinate directions for csys b
    Vab = 3x1 vector from origin of csys a to csys b
    rel = 'a' or 'b' = Character to indicate if Vab is relative to csys a or csys b
    """
    if rel!='a' and rel!='b': return None
    a1,a2,a3 = Ma
    b1,b2,b3 = Mb
    # Rotation matrix
    R = numpy.identity(4,numpy.float)
    R[0,0:3] = [numpy.dot(b1,a1), numpy.dot(b1,a2), numpy.dot(b1,a3)]
    R[1,0:3] = [numpy.dot(b2,a1), numpy.dot(b2,a2), numpy.dot(b2,a3)]
    R[2,0:3] = [numpy.dot(b3,a1), numpy.dot(b3,a2), numpy.dot(b3,a3)]    
    # Transformation matrix
    if rel=='b':
        Vab = numpy.append(Vab,1.0)
        Vab = numpy.dot(R.T,Vab)[0:3]
    T = numpy.identity(4,numpy.float)     
    T[0:3,3] = -Vab       
    # Transformation matrix
    return numpy.dot(R,T)
    
# ~~~~~~~~~~ 

def getTMfromCsys(odb,csysName):
    # NOTE: Need to have a drop down list of available coordinates systems, similar to the 
    #       csys manager. Then we will know before hand if the sys is a session csys or odb csys
    if csysName==None: return None
    # Get ABAQUS datumCsys
    lcsys = None
    # Check odb csyses
    if csysName in odb.rootAssembly.datumCsyses.keys(): 
        lcsys = odb.rootAssembly.datumCsyses[csysName]
    # Check scratch odb csyses
    if odb.path in session.scratchOdbs.keys():
        if csysName in session.scratchOdbs[odb.path].rootAssembly.datumCsyses.keys():
            lcsys = session.scratchOdbs[odb.path].rootAssembly.datumCsyses[csysName]
    if lcsys==None: return None
    # Global coordinate system
    Og = numpy.zeros(3)
    Mg = numpy.identity(3)
    # Local coordinate system
    Ol    = lcsys.origin
    Ml    = numpy.zeros((3,3))
    Ml[0] = lcsys.xAxis/numpy.linalg.norm(lcsys.xAxis) # NOTE: This should already be a unit vector
    Ml[1] = lcsys.yAxis/numpy.linalg.norm(lcsys.yAxis) #       Shouldn't need to normalise
    Ml[2] = lcsys.zAxis/numpy.linalg.norm(lcsys.zAxis)
    # Create transformation matrix
    Vgl = Ol-Og
    TM  = createTransformationMatrix(Mg,Ml,Vgl,rel='a')
    return TM
        
# ~~~~~~~~~~            

def projectXrayPlane(spaceArray3D,whichPlane):
    """Project 3D BMD data onto the specified plane"""
    # Perform the projection by summing along orthogonal axis    
    if whichPlane=='xy':
        projected = numpy.sum(spaceArray3D,axis=2,dtype=spaceArray3D.dtype)
    elif whichPlane=='yz':
        projected = numpy.sum(spaceArray3D,axis=0,dtype=spaceArray3D.dtype)
    elif whichPlane=='xz':
        projected = numpy.sum(spaceArray3D,axis=1,dtype=spaceArray3D.dtype)   
    return projected

# ~~~~~~~~~~  

def writeImageFile(xrayImageFilename,BMDprojected,imageSize,imageFormat='bmp',smooth=True):
    """Create an image from array and write to file"""
    
    xray = BMDprojected.copy()

    # Smooth data if required
    #if smooth:
    #    xray[1:-2,1:-2] = (1./13.)*(1.0*xray[0:-3,0:-3] + 1.0*xray[1:-2,0:-3] + 1.0*xray[2:-1,0:-3] +
    #                                1.0*xray[0:-3,1:-2] + 5.0*xray[1:-2,1:-2] + 1.0*xray[2:-1,1:-2] +
    #                                1.0*xray[0:-3,2:-1] + 1.0*xray[1:-2,2:-1] + 1.0*xray[2:-1,2:-1])

    # Convert to 8-bit
    xray = numpy.asarray(xray,dtype=numpy.int8)

    # Create image from array   
    xray      = xray[:,::-1]
    xrayImage = Image.fromarray(xray.transpose(),mode='L')
    
    # Resize image
    xsize,ysize = xrayImage.size    
    bigSide = numpy.argmax(xrayImage.size)
    if bigSide==0: scale = float(imageSize)/xsize
    else:          scale = float(imageSize)/ysize
    xsize = int(numpy.rint(scale*xsize))
    ysize = int(numpy.rint(scale*ysize))  
    # TO DO: Crop image so that its width (and height?) is divisible by 4 (so compatible with Global Image Lab)
    xrayImage = xrayImage.resize((xsize,ysize),Image.BILINEAR)
    if smooth: xrayImage = xrayImage.filter(ImageFilter.SMOOTH)
    
    # Save xray image to file
    # TO DO: Give option of other file formats i.e. png and jpg
    if xrayImageFilename.split('.')[-1]!=imageFormat: xrayImageFilename+='.%s' % imageFormat
    xrayImage.save(xrayImageFilename,imageFormat) 

    return

# ~~~~~~~~~~   

def getPartData(odb,partName,setName,TM):

    """Get part data based on original (undeformed) coordinates"""
    
    p = odb.rootAssembly.instances[partName] 
    pNodes    = p.nodes
    setRegion = p.elementSets[setName]
    pElems    = setRegion.elements
    
    # Create a list of element connectivities (list of nodes connected to each element)
    setNodeLabs     = {}
    numElems        = len(pElems)
    numNodesPerElem = len(pElems[0].connectivity)
    elemConnect     = numpy.zeros(numElems,dtype=[('label','|i4'),('connectivity','|i4',(numNodesPerElem,))])
    for e in xrange(numElems):
        elem = pElems[e]
        conn = elem.connectivity
        elemConnect[e] = (elem.label, conn)
        for n in conn:        
            setNodeLabs[n]=1
    
    # Create a dictionary of node labels and node coordinates for the entire part instance
    numNodes    = len(pNodes)
    numSetNodes = len(setNodeLabs) 
    nodeCount   = 0
    setNodes    = numpy.zeros(numSetNodes,dtype=[('label','|i4'),('coordinates','|f4',(3,))])
    for n in xrange(numNodes):
        node  = pNodes[n]
        label = node.label
        if label in setNodeLabs:
            setNodes[nodeCount] = (label, node.coordinates) 
            nodeCount += 1
        
    # Transform the coordinates from the global csys to the local csys
    if TM is not None:
        for i in xrange(numSetNodes):
            setNodes['coordinates'][i] = transformPoint(TM,setNodes['coordinates'][i])
        
    # Get bounding box
    low  = numpy.min(setNodes['coordinates'],axis=0)
    upp  = numpy.max(setNodes['coordinates'],axis=0) 
    bbox = (low,upp)

    # Convert setNodes to a dictionary for fast indexing by node label
    setNodeList = dict(zip(setNodes['label'],setNodes['coordinates']))       
    
    return setRegion,setNodeList,elemConnect,bbox

# ~~~~~~~~~~    

def checkInputs(odb,bPartName,bSetName,iPartName,iSetName):
#def checkInputs(odb,bPartName,bSetName,BMDfoname,iPartName,iSetName,stepList):

    print 'Performing additional checks'

    # Check that bone region exists and contains only supported element types
    #if bPartName not in odb.rootAssembly.instances.keys():
    #    return 'Part instance %s does not exist' % bPartName
    #if bSetName not in odb.rootAssembly.instances[bPartName].elementSets.keys():
    #    return 'Element set %s does not exist' % bSetName
    eTypes   = {}
    elements = odb.rootAssembly.instances[bPartName].elementSets[bSetName].elements    
    for e in elements: eTypes[e.type]=1
    usTypes = [str(i) for i in eTypes.keys() if 'C3D10' not in str(i)]
    if len(usTypes) > 0:
        return 'Element types %s are not supported' % ', '.join(usTypes)   
    
    # Check that implant region exists
    #if iPartName not in odb.rootAssembly.instances.keys():
    #    return 'Part instance %s does not exist' % iPartName
    #if iSetName not in odb.rootAssembly.instances[iPartName].elementSets.keys():
    #    return 'Element set %s does not exist' % iSetName
    eTypes   = {}
    elements = odb.rootAssembly.instances[bPartName].elementSets[iSetName].elements    
    for e in elements: eTypes[e.type]=1
    usTypes = [str(i) for i in eTypes.keys() if 'C3D10' not in str(i)]
    if len(usTypes) > 0:
        return 'Element types %s are not supported' % ', '.join(usTypes)         
    
    # Check that all steps in step list exist and that density variable exists in all steps
    #stepInfo = {}
    #for stepName,step in odb.steps.items():
    #    stepInfo[step.number] = step.frames[-1].fieldOutputs.keys()
    #for stepNumber in stepList:
    #    if stepNumber not in stepInfo:
    #        return 'Step number %i does not exist in odb' % stepNumber
    #    if BMDfoname not in stepInfo[stepNumber]:
    #        return 'Density variable %s is not available in Step number %i' % (BMDfoname,stepNumber) 

    return None

def createVirtualXrays(bPartName,bSetName,BMDfoname,showImplant,iPartName,iSetName,
                       iDensity,stepList,csysName,resGrid,imageNameBase,preferredXraySize,
                       imageFormat,smooth):
    """Creates virtual x-rays from an ABAQUS odb file. The odb file should contain \n""" + \
    """a number of steps with a fieldoutput variable representing bone mineral density (BMD)"""
    
    # User message
    print '\npyvXRAY: Create virtual x-rays plugin'
    
    # Process inputs    
    resGrid           = float(resGrid)
    stepList          = eval(stepList)
    preferredXraySize = int(preferredXraySize)
    imageFormat       = imageFormat.strip()
        
    # Set variables
    dx,dy,dz  = (resGrid,)*3
    iDensity /= 1000.    

    # Use odb in current viewport. Check type is OdbType
    vpname = session.currentViewportName
    odb    = session.viewports[vpname].displayedObject
    #if type(odb)!=OdbType:
    #    print 'Object in current viewport is not an odb file object'
    #    return None
    #else:
    #    print 'Odb in current viewport is %s' % odb.name      

    # Check inputs
    err = checkInputs(odb,bPartName,bSetName,iPartName,iSetName)
    if err!=None:
        print 'Error in inputs: %s. No x-rays created.' % err
        return None
        
    # Get transformation matrix to convert from global to local coordinate system
    TM = getTMfromCsys(odb,csysName)
    if TM is None: csysName = 'the global csys'
    print 'X-ray views will be relative to %s' % csysName

    # Get part data and create a bounding box. The bounding box should include the implant if specified
    bRegion,bNodeList,bElemConnect,bBBox = getPartData(odb,bPartName,bSetName,TM)
    if showImplant:    
        iRegion,iNodeList,iElemConnect,iBBox = getPartData(odb,iPartName,iSetName,TM)
        bbLow = numpy.min((bBBox[0],iBBox[0]),axis=0)
        bbUpp = numpy.max((bBBox[1],iBBox[1]),axis=0)
    else:
        bbLow,bbUpp = bBBox 
    
    border   = 0.05*(bbUpp-bbLow)  
    bbLow    = bbLow - border
    bbUpp    = bbUpp + border 
    bbSides  = bbUpp - bbLow
    x0,y0,z0 = bbLow 
    xN,yN,zN = bbUpp 
    lx,ly,lz = bbSides

    # Generate Xray grid
    NX = int(numpy.ceil(lx/dx+1))
    x  = numpy.linspace(x0,xN,NX)
    NY = int(numpy.ceil(ly/dy+1))
    y  = numpy.linspace(y0,yN,NY)
    NZ = int(numpy.ceil(lz/dz+1))
    z  = numpy.linspace(z0,zN,NZ) 

    # Create element map for the implant, map tp 3D space array and then project onto 3 planes 
    if showImplant: 
        # Get element map       
        iElementMap  = createElementMap(iNodeList,iElemConnect['label'],iElemConnect['connectivity'],x,y,z)        
        # Mask 3D array
        iMask = numpy.zeros((NX,NY,NZ),dtype=numpy.float64)   
        for gpi in xrange(iElementMap.size):
            gridPoint = iElementMap[gpi]
            if gridPoint['cte'] > 0:
                i,j,k = convert1Dto3Dindex(gpi,NX,NY,NZ)
                iMask[i,j,k] = iDensity
        # Create projections of 3D space array onto planes 
        iProjectedXY = projectXrayPlane(iMask,'xy')
        iProjectedYZ = projectXrayPlane(iMask,'yz')
        iProjectedXZ = projectXrayPlane(iMask,'xz')
        # Create xrays of implant without bone        
        iprojXY = iProjectedXY.copy()
        iprojYZ = iProjectedYZ.copy()
        iprojXZ = iProjectedXZ.copy()        
        prXY    = [numpy.min(iprojXY),numpy.max(iprojXY)]
        prYZ    = [numpy.min(iprojYZ),numpy.max(iprojYZ)]
        prXZ    = [numpy.min(iprojXZ),numpy.max(iprojXZ)]        
        iprojXY[:,:] = (iprojXY[:,:]-prXY[0])/(prXY[1]-prXY[0])*255.
        iprojYZ[:,:] = (iprojYZ[:,:]-prYZ[0])/(prYZ[1]-prYZ[0])*255. 
        iprojXZ[:,:] = (iprojXZ[:,:]-prXZ[0])/(prXZ[1]-prXZ[0])*255.         
        writeImageFile('implant_XY',iprojXY,preferredXraySize,imageFormat,smooth)
        writeImageFile('implant_YZ',iprojYZ,preferredXraySize,imageFormat,smooth)
        writeImageFile('implant_XZ',iprojXZ,preferredXraySize,imageFormat,smooth)

    # Create the element map for the bone
    bElementMap = createElementMap(bNodeList,bElemConnect['label'],bElemConnect['connectivity'],x,y,z)
    
    # Interpolate HU values from tet mesh onto grid using quadratic tet shape function
    # (a) Get HU values from frame
    numSteps  = len(stepList)
    xraysXY   = numpy.zeros((numSteps,NX,NY),dtype=numpy.float64)
    xraysYZ   = numpy.zeros((numSteps,NY,NZ),dtype=numpy.float64)
    xraysXZ   = numpy.zeros((numSteps,NX,NZ),dtype=numpy.float64)
    mappedBMD = numpy.zeros((NX,NY,NZ),dtype=numpy.float64)
    for s in xrange(numSteps):
        # Step details
        stepId   = stepList[s]               
        stepName = "Step-%i" % (stepId)
        frame    = odb.steps[stepName].frames[-1]
        # Get BMD data for bRegion in current frame
        BMDfov    = frame.fieldOutputs[BMDfoname].getSubset(region=bRegion, position=ELEMENT_NODAL).values
        BMDvalues = {}
        for i in xrange(len(BMDfov)):
            val = BMDfov[i]            
            elementLabel = val.elementLabel            
            if elementLabel not in BMDvalues:
                if 'C3D10' in val.baseElementType: numNodesPerElem = 10
                BMDvalues[elementLabel] = numpy.zeros(numNodesPerElem)
                count=0
            else:
                count+=1
            BMDvalues[elementLabel][count] = val.data        
        # Perform the interpolation from elementMap to 3D space array
        for gpi in xrange(bElementMap.size):
            gridPoint = bElementMap[gpi]
            cte = gridPoint['cte']
            if cte > 0:
                nv  = BMDvalues[cte] 
                ipc = numpy.array([gridPoint['g'],gridPoint['h'],gridPoint['r']])
                i,j,k = convert1Dto3Dindex(gpi,NX,NY,NZ)
                mappedBMD[i,j,k] = tetShapeFunction(nv,ipc)
        # Project onto orthogonal planes    
        xraysXY[s] = projectXrayPlane(mappedBMD,'xy')
        xraysYZ[s] = projectXrayPlane(mappedBMD,'yz')
        xraysXZ[s] = projectXrayPlane(mappedBMD,'xz')
        
    # Get min/max pixel values. Use zero for lower limit (corresponding to background)
    prXY = [0.,numpy.max(xraysXY)]
    prYZ = [0.,numpy.max(xraysYZ)]
    prXZ = [0.,numpy.max(xraysXZ)]
    # Add projected implant to projected bone
    if showImplant:
        xraysXY[:] += iProjectedXY
        xraysYZ[:] += iProjectedYZ
        xraysXZ[:] += iProjectedXZ
    # Scale each projection using pixel range from bone
    xraysXY[:,:,:] = (xraysXY[:,:,:]-prXY[0])/(prXY[1]-prXY[0])*255.      
    xraysYZ[:,:,:] = (xraysYZ[:,:,:]-prYZ[0])/(prYZ[1]-prYZ[0])*255.           
    xraysXZ[:,:,:] = (xraysXZ[:,:,:]-prXZ[0])/(prXZ[1]-prXZ[0])*255.                
    xraysXY[numpy.where(xraysXY<0.)]   = 0.
    xraysYZ[numpy.where(xraysYZ<0.)]   = 0.
    xraysXZ[numpy.where(xraysXZ<0.)]   = 0.
    xraysXY[numpy.where(xraysXY>255.)] = 255.
    xraysYZ[numpy.where(xraysYZ>255.)] = 255.
    xraysXZ[numpy.where(xraysXZ>255.)] = 255.
    
    # Create images
    for s in xrange(numSteps):
        stepId = stepList[s]
        writeImageFile(('%s_XY_%i' % (imageNameBase,stepId)),xraysXY[s,:,:],preferredXraySize,imageFormat,smooth)
        writeImageFile(('%s_YZ_%i' % (imageNameBase,stepId)),xraysYZ[s,:,:],preferredXraySize,imageFormat,smooth) 
        writeImageFile(('%s_XZ_%i' % (imageNameBase,stepId)),xraysXZ[s,:,:],preferredXraySize,imageFormat,smooth)
        
    # User message
    print 'Virtual x-rays have been created in %s\n' % os.getcwd()        
