'''
STL Binary File Class
Author: Matthew Stagg
Description: Class to interface with stl files in python
Based on work by Mar Canet's open source project at: https://github.com/mcanet/STL-Volume-Model-Calculator
'''

import struct
import sys

class STL():
    _errorCode = 1
    _failed = False   
    
    _normals = []
    _vertices = []
    _triangles = []
    _bytecount = []
    _centroid = (0, 0, 0)
    
    
    _numberOfTriangles = 0
    _volume = 0
    _width = 0
    _height = 0
    _depth = 0
    
    _xPos = 0
    _xNeg = 0
    _yPos = 0
    _yNeg = 0
    _zPos = 0
    _zNeg = 0
    
    def GetNormals(self):
        return self._normals
    
    def GetVertices(self):
        return self._vertices
        
    def GetTriangles(self):
        return self._triangles
        
    def GetByteCount(self):
        return self._bytecount
    
    def GetCentroid(self):
        return self._centroid
    
    def GetNumberOfTriangles(self):
        return self._numberOfTriangles
        
    def GetVolume(self):
        return self._volume
        
    def GetWidth(self):
        return self._width
        
    def GetHeight(self):
        return self._height
        
    def GetDepth(self):
        return self._depth
        
    def GetDimensions(self):
        return (self._width, self._height, self._depth)
    
    # Constructor
    # Calculates all relevant dimensions
    def __init__(self, filepath):  
        self._path = filepath
    
        # Attempt to open the file to be read
        try:
            # File must be *.stl
            if(self._path.lower().endswith(".stl")):
                self._file = open(self._path, "rb")
            else:
                self._failed = True
                self._errorCode = 1
        except:
            self._failed = True
            self._errorCode = 2
        
        if not self._failed:        
            self._calculateDimensions()

    
    # Reads STL file and calculates all relevant dimensions and geometric information
    def _calculateDimensions(self):
        self._skipHeader()
        self._numberOfTriangles = self._readLength()
        
        for i in range(0, self._numberOfTriangles):
            self._readTriangle()
        
        self._width = self._xPos - self._xNeg
        self._height = self._yPos - self._yNeg
        self._depth = self._zPos - self._zNeg
    
    # Moves the file reader to the 81st byte, the first byte after the header
    def _skipHeader(self):
        self._file.seek(80)
    
    # Reads the total number of triangles from file
    def _readLength(self):
        length = struct.unpack("@i", self._file.read(4))
        return length[0]
    
    # Reads 'length' bytes and returns them in 'format' format
    def _unpack(self, format, length):
        s = self._file.read(length)
        return struct.unpack(format, s)
    
    # Averages the previous centroid with a new vertex to update the centroid position
    def _calculateCentroid(self, vertex):
        if(self._centroid == (0, 0 ,0)):
            self._centroid = vertex
        else:
            newCentroid = (((self._centroid[0] + vertex[0]) / 2), ((self._centroid[1] + vertex[1]) / 2), ((self._centroid[2] + vertex[2]) / 2))
            self._centroid = newCentroid
    
    # Reads a single vertex, updating the centroid and cartesian limits 
    def _readVertex(self, vertex):
        if(vertex[0] >= 0):
            if(vertex[0] > self._xPos):
                self._xPos = vertex[0]
        else:
            if(vertex[0] < self._xNeg):
                self._xNeg = vertex[0]
                
        if(vertex[1] >= 0):
            if(vertex[1] > self._yPos):
                self._yPos = vertex[1]
        else:
            if(vertex[1] < self._yNeg):
                self._yNeg = vertex[1]
                
        if(vertex[2] >= 0):
            if(vertex[2] > self._zPos):
                self._zPos = vertex[2]
        else:
            if(vertex[2] < self._zNeg):
                self._zNeg = vertex[2]
        
        self._calculateCentroid(vertex)
        return vertex
    
    # Reads all vertices relevant to a single triangle
    # Relevant binary STL file information: https://en.wikipedia.org/wiki/STL_(file_format)#Binary_STL
    def _readTriangle(self):
        normalVector  = self._unpack("<3f", 12)
        vertex1 = self._readVertex(self._unpack("<3f", 12))
        vertex2 = self._readVertex(self._unpack("<3f", 12))
        vertex3 = self._readVertex(self._unpack("<3f", 12))
        attrByteCount  = self._unpack("<h", 2)
        
        newTriangle = (vertex1, vertex2, vertex3)
        
        self._normals.append(normalVector)
        self._vertices.append(vertex1)
        self._vertices.append(vertex2)
        self._vertices.append(vertex3)
        self._triangles.append(newTriangle)
        self._bytecount.append(attrByteCount[0])
        self._signedVolumeOfTriangle(vertex1, vertex2, vertex3)
    
    # Calculate volume of the 3D mesh using tetrahedron volume in m3
    # based in: http://stackoverflow.com/questions/1406029/how-to-calculate-the-volume-of-a-3d-mesh-object-the-surface-of-which-is-made-up
    def _signedVolumeOfTriangle(self, vertex1, vertex2, vertex3):
        vector321 = vertex3[0] * vertex2[1] * vertex1[2]
        vector231 = vertex2[0] * vertex3[1] * vertex1[2]
        vector312 = vertex3[0] * vertex1[1] * vertex2[2]
        vector132 = vertex1[0] * vertex3[1] * vertex2[2]
        vector213 = vertex2[0] * vertex1[1] * vertex3[2]
        vector123 = vertex1[0] * vertex2[1] * vertex3[2]
        self._volume += ((1.0 / 6.0) * (-vector321 + vector231 + vector312 - vector132 - vector213 + vector123))