#!/usr/local/bin/python3


import itertools 
import math
import os
#import operator


from pycv.constants import * #deg_to_rad, etc 
from pycv.vec3d import *  
from pycv.kdag import *  

###############################################
class Vec2d(object):    

    def __init__(self,x,y):
        self.x = x;self.y = y    

    def __repr__(self):
        return '(%s, %s)' % (self.x, self.y)

    def __abs__(self):
        return type(self)(abs(self.x), abs(self.y))

    def __add__(self, other):
        return type(self)(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return type(self)(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return type(self)(self.x * other.x, self.y * other.y)

    def __truediv__(self, other):
        #untested - normalized? 
        #return type(self)(self.x / other.x, self.y / other.y)
        self.x = other.x/other.length()
        self.y = other.y/other.length()
        return type(self)(self.x, self.y)

    def __getitem__(self,index):
        if index==0:
            return self.x
        if index==1:
            return self.y
    ## ## ##
    def div_scalar(self, scalar):
        self.x = self.x/scalar
        self.y = self.y/scalar
        return type(self)(self.x , self.y )
        ## ## ##
    def normalize(self):
        #untested 
        invLength = 1.0/math.sqrt(self.x*self.x + self.y*self.y)
        self.x *= invLength
        self.y *= invLength
    ## ## ##
    def length(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    ## ## ##
    def dot_product(self, other):
        return self.x * other.x + self.y * other.y

    #def dotProduct (self, v1, v2):
    #     return v1[0]*v2[0] + v1[1]*v2[1] 

    def makefloat(self,v):
        tmp = []
        tmp.append( float(v[0]) )
        tmp.append( float(v[1]) )
        tmp.append( float(v[2]) )
        return tmp

    def crossProduct (self, v1, v2):
        """ UNTESTED -only works in 3D -  <y*z-z*y, z*x-x*z, x*y,y*x> """
        v1 = self.makefloat(v1)
        v2 = self.makefloat(v2)
        return (
                v1[1]*v2[2]-v1[2]*v2[1], 
                v1[2]*v2[0]-v1[0]*v2[2], 
                v1[0]*v2[2]-v1[0]*v2[0]
               )

    def normalize3d(self, in_vec):
        #untested 
        try:
           invLength = 1.0/math.sqrt(in_vec[0]*in_vec[0] + in_vec[1]*in_vec[1]+ in_vec[2]*in_vec[2])
           return (in_vec[0] *invLength, in_vec[1] * invLength,  in_vec[2] * invLength)
        except:
           print('normalize3d: divide by zero error.') 
           return [0,0,1]

    ## ## ##
    def distance_to(self, other, doRound=False):
        val = math.hypot((self.x - other.x), (self.y - other.y))
        if not doRound:        
            return val
        if doRound: 
           return int(val)
    ## ## ## 
    def project_pt(self, A, B, offset , doRound=False):
        nX = B.x - A.x;nY = B.y - A.y
        distX = pow( (A.x - B.x ) , 2.0 ) 
        distY = pow( (A.y - B.y ) , 2.0 ) 
        vecLength = math.sqrt(distX + distY )
        # normalized vector  
        calcX = nX / vecLength
        calcY = nY / vecLength
        # project point along vector with offset (can use negative too)
        ptX = B.x + (calcX * offset)
        ptY = B.y + (calcY * offset)
        if not doRound:
            return type(self)(ptX, ptY)
        if doRound:
            return type(self)(int(ptX), int(ptY) )

    def intersect(self, v1s, v1e, v2s, v2e ):

        #start and end coords for two 2D lines
        p0_x = float(v1s[0])
        p0_y = float(v1s[1])
        p1_x = float(v1e[0])
        p1_y = float(v1e[1])
        p2_x = float(v2s[0])
        p2_y = float(v2s[1])
        p3_x = float(v2e[0])
        p3_y = float(v2e[1])

        #return values
        i_x = 0
        i_y = 0 

        #??
        s1_x = 0
        s1_y = 0
        s2_x = 0
        s2_y = 0

        s1_x = p1_x - p0_x  
        s1_y = p1_y - p0_y
        s2_x = p3_x - p2_x
        s2_y = p3_y - p2_y

        s = 0
        t = 0
        try: 
            s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / (-s2_x * s1_y + s1_x * s2_y)
            t = ( s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / (-s2_x * s1_y + s1_x * s2_y)
        except:
            #print('we no worky')
            return 0
        
        if (s >= 0 and s <= 1 and t >= 0 and t <= 1):
            # Collision detected
            i_x = p0_x + (t * s1_x);
            i_y = p0_y + (t * s1_y);
            return (i_x,i_y)  

        return 0; # No collision


    ## ## ## 
            
    def calc_normal(self):
        """
        Quoting from http://www.opengl.org/wiki/Calculating_a_Surface_Normal
        A surface normal for a triangle can be calculated by taking the vector cross product of two edges of that triangle. 
        The order of the vertices used in the calculation will affect the direction of the normal 
        (in or out of the face w.r.t. winding).
        So for a triangle p1, p2, p3, 
        if the vector U = p2 - p1 and the vector V = p3 - p1 then the normal N = U x V and can be calculated by:
        Nx = UyVz - UzVy
        Ny = UzVx - UxVz
        Nz = UxVy - UyVx
        """
        """
        The cross product of two sides of the triangle equals the surface normal. So, if VV = P2P2 - P1P1 and WW = P3P3 - P1P1, and NN is the surface normal, then:
        Nx=(Vy∗Wz)−(Vz∗Wy)Nx=(Vy∗Wz)−(Vz∗Wy)
        Ny=(Vz∗Wx)−(Vx∗Wz)Ny=(Vz∗Wx)−(Vx∗Wz)
        Nz=(Vx∗Wy)−(Vy∗Wx)Nz=(Vx∗Wy)−(Vy∗Wx)
        If AA is the new vector whose components add up to 1, then:
        Ax=Nx/(|Nx|+|Ny|+|Nz|)Ax=Nx/(|Nx|+|Ny|+|Nz|)
        Ay=Ny/(|Nx|+|Ny|+|Nz|)Ay=Ny/(|Nx|+|Ny|+|Nz|)
        Az=Nz/(|Nx|+|Ny|+|Nz|)
        """

        out = []

        #Nx = UyVz - UzVy
        #Ny = UzVx - UxVz
        #Nz = UxVy - UyVx

        return out

    
    ## ## ## 


###############################################


class PointGen2D(object):
    """
      Geometric cartesian point operator, coordinate generator, utils for 2d vector manipulation. 
      
      Top Left, Bottom Right , ect are abbreivated as TL/tl, BR/br, ect      

      STANDARDS:
        works internally in float where applicable, but has a doRound option to return integer 
        points are tuples
        point arrays are lists of tuples
        low level functions accept 4 floats
        "extents" - are 4 xy coordinates - (top left, top right , bottom right, bottom left ) 
        "bbox"    - is 4 extent values   - (left, upper, right, and lower ) , (west north east south)
        "diagonal" - top left to bottom right tuple - (tl,br)    

        fiducials - 3 tuples (x,y) in a list, [0-top left , 1-top right, 2-bottom left ]
    """
    
    def aggregate_extents(self, points, offset=False):
        """ needs at least three points to work 
            take any number of points - (3 or more tuples of (x,y) ),  and find the min/max of all of them as a whole
        """
       
        minx = points[0][0];maxx = 0
        miny = points[0][1];maxy = 0
        if not offset:
            for p in points:
                if p[0]<=minx:
                    minx = p[0]
                if p[0]>=maxx:
                    maxx = p[0]
                if p[1]<=miny:
                    miny = p[1]
                if p[1]>=maxy:
                    maxy = p[1]
        if offset:
            for p in points:
                if p[0]<=minx:
                    minx = p[0]-offset
                if p[0]>=maxx:
                    maxx = p[0]+offset
                if p[1]<=miny:
                    miny = p[1]-offset
                if p[1]>=maxy:
                    maxy = p[1]+offset

        return [minx, miny, maxx, maxy ]
            
    def add_margin_bbox(self, bbox, size):
        """ return center (x,y) from two diagonal coordinates """
        
        out = []
        out.append( bbox[0]-size  ) 
        out.append( bbox[1]-size  )
        out.append( bbox[2]+size  )
        out.append( bbox[3]+size  )
        return out

    def extents_fr_bbox(self, bbox, offset=None):
        """ return center (x,y) from a tuple of 4 numbers (PIL bbox [left, top, right, bottom]) 
            offset (int) adds a margin to the size of the page edges 
        """
        
        out = []
        if not offset:
            out.append( (bbox[0], bbox[1]) ) #top left
            out.append( (bbox[2], bbox[1]) ) #top right
            out.append( (bbox[2], bbox[3]) ) #bottom right
            out.append( (bbox[0], bbox[3]) ) #bottom left
        
        #increase the margins, (pixels are indexed with top left at 0,0)
        if offset:
            out.append( (bbox[0]-offset , bbox[1]-offset ) ) #top left
            out.append( (bbox[2]-offset , bbox[1]+offset ) ) #top right
            out.append( (bbox[2]+offset , bbox[3]+offset ) ) #bottom right
            out.append( (bbox[0]-offset , bbox[3]-offset ) ) #bottom left

        return out
      
    def tuple_pop(self, listTuples, tup):

        out = []
        for t in listTuples:
            if(t != tup):
                out.append(t)
        return out

    def closest_to_axis(self, points, val, axis):
        """ return the closest point to X OR Y """
        
        tmpsort = []

        for pt in points:
            if axis=='x':
                sp = ( val ,pt[1]  )
            if axis=='y':
                sp = ( pt[0]  ,val )

            tmpsort.append( (self.calc_line_length(pt[0], pt[1], sp[0], sp[1] ), pt) )
        
        ###
        tmpsort.sort()
        return tmpsort[0][1]

    def sort_anchors(self, resx, resy, points):
        """ 
            This is important - it takes the 3 fiducials and sorts them 
            Many other downsteram functions depend on the fiducials being in the proper order.
            Proper order is (1-Top Left/TL, 2-Top Right/TR, 3-Bottom Left/BL)
 
        """

        if len(points)!=3:
            print('sort_anchors: try again, I need 3 points ONLY')
            return None 

        TL=0;TR=0;BL=0

        cornerdat = self.orient_by_corner( resx, resy, points, True)
        popd      = self.tuple_pop(points, cornerdat[2])
        TR        = cornerdat[2] #this will always be the closest to a corner

        if cornerdat[1]=='tl':
            TL=( self.closest_to_axis( popd, 0      , 'x')  )  #"TL" = BL 
        if cornerdat[1]=='tr':
            TL=( self.closest_to_axis( popd, TR[1]  , 'y')  )  #"TL" = TL 
        if cornerdat[1]=='bl':
            TL=( self.closest_to_axis( popd, TR[1]  , 'y')  )  #"TL" = BR
        if cornerdat[1]=='br':
            TL=( self.closest_to_axis( popd, TR[0]  , 'x')  )  #"TL" = TR

        #now that we know the top left , pop it off and keep the remainder
        popd      = self.tuple_pop(popd, TL)

        return (TL,TR,popd[0])

    def calc_square_diag(self, tl, br):
        """ creates 4 coordinates representing an extent box from a diagonal coordinate pair """ 
        out =[]  
        out.append( (tl[0], tl[1])  ) #tl
        out.append( (br[0], tl[1])  ) #tr
        out.append( (br[0], br[1])  ) #br
        out.append( (tl[0], br[1])  ) #bl

        return out

    def calc_square_pt(self, size, origin=None ):
        """ UNTESTED 
            DEBUG - this is unclamped  
            calc the XY coodrinates for a square  
            (top left, top right , bottom right, bottom left ) 
        """
        
        out =[]  

        if origin:
            out.append( ( origin[0]-size, origin[1]+size)  ) #tl
            out.append( ( origin[0]+size, origin[1]+size)  ) #tr
            out.append( ( origin[0]+size, origin[1]-size)  ) #br
            out.append( ( origin[0]-size, origin[1]-size)  ) #bl
        else:
            out.append( ( -size,  size)  )
            out.append( (  size,  size)  )
            out.append( (  size, -size)  )
            out.append( ( -size, -size)  )
        return out
    
    def calc_bbox_pt(self, size, origin=None ):
        """ DEBUG - this is unclamped!
            calc extents for a square (left, upper, right, and lower)
        """
                
        out =[]  
        
        if origin:
            out.append(  origin[0]-size  ) #west
            out.append(  origin[1]-size  ) #north
            out.append(  origin[0]+size  ) #east
            out.append(  origin[1]+size  ) #south
        else:
            out.append(  -size  ) #west
            out.append(  -size  ) #north
            out.append(  size  ) #east
            out.append(  size  ) #south
        return out
                
    def deg_to_rad (self, deg ):
       return deg * DEG_TO_RAD

    def rad_to_deg (self, rad ):
       return rad * RAD_TO_DEG

    def dotProduct (self, v1, v2):
         """ UNTESTED - scalar - mag but not direction """
         return v1[0]*v2[0] + v1[1]*v2[1] 

    def crossProduct (self, v1, v2):
        """ UNTESTED -only works in 3D -  <y*z-z*y, z*x-x*z, x*y,y*x> """
        return (v1[1]*v2[2]-v1[2]*v2[1], v1[2]*v2[0]-v1[0]*v2[2], v1[0]*v2[2]-v1[0]*v2[0])
    
    def vectAdd(self, v):
        return [x+v[0], y+v[1], z+v[2]]

    def vectMult (self, v, scalar):
        return [v[0]*scalar, v[1]*scalar, v[2]*scalar ]

    def calc_line_length(self, x1, y1, x2, y2):
        return math.sqrt( ((x1-x2)**2)+ ((y1-y2)**2) )
    
    def calc_line_length_pt(self, pt1, pt2 ):
        return self.calc_line_length(pt1[0], pt1[1], pt2[0], pt2[1] )

    def matrix_identity(self):
        """ using the "standard" 16 element, Row major, 4X4 rotation matrix """
        return  [ 1,0,0,0 ,0,1,0,0 ,0,0,1,0 ,0,0,0,1]
      
    def mult_vec3_mat4(self, m, v):
        """ multiplies a 4X4 matrix by a 3D vector - returns a vector tuple """
        
        outx = m[0] * v[0] + m[4] * v[1] + m[8]  * v[2] + m[12]
        outy = m[1] * v[0] + m[5] * v[1] + m[9]  * v[2] + m[13]
        outz = m[2] * v[0] + m[6] * v[1] + m[10] * v[2] + m[14]
          
        return  (outx, outy, outz)
          
    def mult_mat4(self, m, n):  
        """multiply two 4X4 matricies together """
                          
        return [
                m[0]*n[0]  + m[1]*n[4]  + m[2]*n[8]   + m[3]*n[12],
                m[0]*n[1]  + m[1]*n[5]  + m[2]*n[9]   + m[3]*n[13],
                m[0]*n[2]  + m[1]*n[6]  + m[2]*n[10]  + m[3]*n[14],
                m[0]*n[3]  + m[1]*n[7]  + m[2]*n[11]  + m[3]*n[15],
                m[4]*n[0]  + m[5]*n[4]  + m[6]*n[8]   + m[7]*n[12],
                m[4]*n[1]  + m[5]*n[5]  + m[6]*n[9]   + m[7]*n[13],
                m[4]*n[2]  + m[5]*n[6]  + m[6]*n[10]  + m[7]*n[14],
                m[4]*n[3]  + m[5]*n[7]  + m[6]*n[11]  + m[7]*n[15],
                m[8]*n[0]  + m[9]*n[4]  + m[10]*n[8]  + m[11]*n[12],
                m[8]*n[1]  + m[9]*n[5]  + m[10]*n[9]  + m[11]*n[13],
                m[8]*n[2]  + m[9]*n[6]  + m[10]*n[10] + m[11]*n[14],
                m[8]*n[3]  + m[9]*n[7]  + m[10]*n[11] + m[11]*n[15],
                m[12]*n[0] + m[13]*n[4] + m[14]*n[8]  + m[15]*n[12],
                m[12]*n[1] + m[13]*n[5] + m[14]*n[9]  + m[15]*n[13],
                m[12]*n[2] + m[13]*n[6] + m[14]*n[10] + m[15]*n[14],
                m[12]*n[3] + m[13]*n[7] + m[14]*n[11] + m[15]*n[15]
               ]
    
    def buildPerspProjMat(self, m, fov, aspect, znear, zfar):
        """
            DEBUG - THIS NEVER WORKED - UNTESTED 

            #http://stackoverflow.com/questions/8633034/basic-render-3d-perspective-projection-onto-2d-screen-with-camera-without-openg
            
            # Transpose from column major to row major 
            # [0  4  8   12]   # [0  1  2  3]  
            # [1  5  9   13]   # [4  5  6  7]
            # [2  6  10  14]   # [8  9  10 11] 
            # [3  7  11  15]   # [12 13 14 15]
        """

        PI_OVER_360 = 0.00872664625
        xymax = 100

        ymax = znear * math.tan(fov * PI_OVER_360);
        ymin = -xymax;
        xmin = -xymax;

        width = xymax - xmin;
        height = xymax - ymin;

        depth = zfar - znear;
        q = -(zfar + znear) / depth;
        qn = -2 * (zfar * znear) / depth;

        w = 2 * znear / width;
        w = w / aspect;
        h = 2 * znear / height;

        m[0]  = w;
        m[1]  = 0;
        m[2]  = 0;
        m[3]  = 0;

        m[4]  = 0;
        m[5]  = h;
        m[6]  = 0;
        m[7]  = 0;
        
        m[8]  = 0;
        m[9]  = 0;
        m[10] = q;
        m[11] = qn;

        m[12] = 0;
        m[13] = 0;
        m[14] = -1;

        print(m)
        return m


    def rotate_mat4(self, points, xrot, yrot, zrot):
        """
           using the "standard" 16 element, Row major, 4X4 rotation matrix used by Maya, and most others
           However I am rotating only the Z axis (2D), but leaving the other axes commented out
          
                 
           [0  1  2  3]      xx xy xz 0
           [4  5  6  7]      yx yy yz 0
           [8  9  10 11]     zx zy zz 0
           [12 13 14 15]     0  0  0  0
           ------------------------------
           rotate Y matrix     
           |  cos(y)  0      -sin(y)  0 | 
           |  0       1       0       0 | 
           |  sin(y)  0       cos(y)  0 | 
           |  0       0       0       1 | 
           ------------------------------
           rotate Z  matrix 
           |  cos(z)  sin(z)  0       0 | 
           | -sin(z)  cos(z)  0       0 |
           |  0       0       1       0 |
           |  0       0       0       1 |
           ------------------------------
           rotate X matrix  
           |  1       0       0       0 |  
           |  0       cos(x)  sin(x)  0 |  
           |  0      -sin(x)  cos(x)  0 |  
           |  0       0       0       1 | 
        """
        #initialize rotation matrix to identity          
        self.ROTMATRIX = self.matrix_identity()
        ####
        #build rotationY (see diagram above) 
        y_matrix =  self.matrix_identity()
        y_matrix[0]  =  math.cos(self.deg_to_rad( yrot ))
        y_matrix[2]  = -math.sin(self.deg_to_rad( yrot ))
        y_matrix[8]  =  math.sin(self.deg_to_rad( yrot ))
        y_matrix[10] =  math.cos(self.deg_to_rad( yrot ))

        ####                
        #build rotationZ (see diagram above) 
        z_matrix    =  self.matrix_identity()
        z_matrix[0] =  math.cos(self.deg_to_rad( zrot ))
        z_matrix[1] =  math.sin(self.deg_to_rad( zrot ))
        z_matrix[4] = -math.sin(self.deg_to_rad( zrot ))
        z_matrix[5] =  math.cos(self.deg_to_rad( zrot ))
        tmp_matr = self.mult_mat4( y_matrix, z_matrix)   
        
        ####
        #build rotationX (see diagram above) 
        x_matrix =  self.matrix_identity()
        x_matrix[5]  =   math.cos(self.deg_to_rad( xrot )) 
        x_matrix[6]  =   math.sin(self.deg_to_rad( xrot )) 
        x_matrix[9]  =  -math.sin(self.deg_to_rad( xrot ))
        x_matrix[10] =   math.cos(self.deg_to_rad( xrot ))
        self.ROTMATRIX = self.mult_mat4( x_matrix, tmp_matr )  

        ####
        #sad attempt at perspective, I am lost..... 
        #idm =  self.matrix_identity()
        #persp =  self.buildPerspProjMat(idm, 180, 10, .1, 1)
        #self.ROTMATRIX = self.mult_mat4( persp, self.ROTMATRIX )  

        ############ 
        tmp_buffer = []
        out = None
        #rotate points to scan  
        for pvec in points:  
            out = self.mult_vec3_mat4(self.ROTMATRIX, (pvec[0], pvec[1], pvec[2]) )
            tmp_buffer.append( ( out[0], out[1], out[2] ) )

        return tmp_buffer

    def rotate_points_shifted(self, points, oldpivot, newpivot, angle, doOffset=False, doRound=False):
        """ rotate points and shift the output from an old point to a new point 
            doOffset is a SECOND shift of the points if you want to nudge them more, ( fine tuning )
        """

        rotated_fids =  self.batch_rotate_pts( points, oldpivot, angle , doRound)

        deltax = newpivot[0]-oldpivot[0]
        deltay = newpivot[1]-oldpivot[1]

        newfids = []
        for pt in rotated_fids:
            if not doOffset:
                newfids.append( (pt[0]+deltax, pt[1]+deltay) )
            if doOffset:
                newfids.append( (pt[0]+(deltax+doOffset[0]), pt[1]+(deltay+doOffset[1])  ) )

        return newfids 

    def rotate_point(self, point, pivot, angle, doRound=False):
        """ helper to rotate a single point, for more advanced tranforms use self.rotate( [pts], angle) """
        
        x1 = point[0] - pivot[0]  #x
        y1 = point[1] - pivot[1]  #y  

        a = x1 * math.cos(self.deg_to_rad(angle)) - y1 * math.sin(self.deg_to_rad(angle))
        b = x1 * math.sin(self.deg_to_rad(angle)) + y1 * math.cos(self.deg_to_rad(angle))
                
        if not doRound:
            return (a + pivot[0], b + pivot[1]);
        if doRound:
            return ( round(a + pivot[0]), round(b + pivot[1]) );

    def batch_transform_pts(self, pts, new_coord, doround=False):
        """ UNTESTED ? - takes a list of tuples and returns a shifted list of tuples , based on a tuple of (x,y) shift"""

        out = []
        for pt in pts:
            if not doround:
                out.append( (pt[0]+ new_coord[0], pt[1]+ new_coord[1] ) ) 
            if doround:
                out.append( ( int(pt[0]+ new_coord[0]), int(pt[1]+ new_coord[1]) ) )         
        return out

    def batch_rotate_pts(self, pts, pivot, angle, doround=False):
        out = []
        for pt in pts:
            out.append( self.rotate_point(pt, pivot, angle, doround) )
        return out

    def calc_circle(self, x_orig, y_orig, dia, periodic=True, spokes=23, doRound=False):
        """ spokes = num spokes """

        plot_x = 0;plot_y = 0;
        out = []
        
        degs = 360/spokes
        dit = 0
        for i in range(spokes):

            plot_x = x_orig + (math.sin(self.deg_to_rad(dit))*dia) 
            plot_y = y_orig + (math.cos(self.deg_to_rad(dit))*dia) 
            if doRound:
                out.append( (int(plot_x), int(plot_y)) ) 
            else:
                out.append( (plot_x, plot_y))
            dit+=degs
        
        if periodic:
             out.append( out[0] )

        return out
 
    def calc_line(self, x1, y1, x2, y2):        
        """ bresenham's algorithm 
            from http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm
        """
        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)

        points = []
        issteep = abs(y2-y1) > abs(x2-x1)
        if issteep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        rev = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            rev = True
        deltax = x2 - x1
        deltay = abs(y2-y1)
        error = int(deltax / 2)
        y = y1
        ystep = None
        if y1 < y2:
            ystep = 1
        else:
            ystep = -1
        for x in range(x1, x2 + 1):
            if issteep:
                points.append((y, x))
            else:
                points.append((x, y))
            error -= deltay
            if error < 0:
                y += ystep
                error += deltax
        # Reverse the list if the coordinates were reversed
        if rev:
            points.reverse()
        return points
   
    def pt_offset_to_line( self, vector, pt): # x3,y3 is the point
        """
           given a vector and a point, return a vector between them 
           (you can get the length of that to calculate distance)
        """
        x1 = vector[0][0] ; y1 = vector[0][1]
        x2 = vector[1][0] ; y2 = vector[1][1]
        x3 = pt[0]        ; y3 = pt[1]

        px = x2-x1
        py = y2-y1
        
        notzero = px*px + py*py
        u =  ((x3 - x1) * px + (y3 - y1) * py) / float(notzero)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py
        dx = x - x3
        dy = y - y3

        return [ pt , (pt[0]+dx, pt[1]+dy) ]
        
        ###################
        #if you want to get distance
        #return math.sqrt(dx*dx + dy*dy)

    def extract_pt_vector(self, vector, offset):
        """
          given a vector [(x,y), (x,y)] and an offset - return a point (x,y)

          same as vector class project pt along a vector - even beyond its extent
        """

        a=(vector[0][0], vector[0][1])
        b=(vector[1][0], vector[1][1])
        
        nX = b[0] - a[0];nY = b[1] - a[1]
        distX = pow( (a[0] - b[0] ) , 2.0 ) 
        distY = pow( (a[1] - b[1] ) , 2.0 ) 
        vecLength = math.sqrt(distX + distY )
        # normalized vector  
        calcX = nX / vecLength
        calcY = nY / vecLength
        # project point along vector with offset (can use negative too)
        ptX = b[0] + (calcX * offset)
        ptY = b[1] + (calcY * offset)
        return (ptX, ptY)

    def locate_pt_along(self, x1, y1, x2, y2, num):
        """ taken from my old 3d character rigging code (with the Z axis removed)
            this was used to place vertebra along a spine
        """

        pts_created = []
        fpos=(x1, y1)
        spos=(x2, y2)
         
        for n in range(num):
            npos = [2]
            npos[0]    =spos[0]+(((fpos[0]-spos[0])/(num+1))*(n+1))
            npos.append(spos[1]+(((fpos[1]-spos[1])/(num+1))*(n+1)) )
            pts_created.append( (npos[0], npos[1]) )
        return pts_created

    def calc_mid(self, pt1, pt2, num=1, doround=False):
        """ get the midpoint of a 2d vector """

        out = self.locate_pt_along( pt1[0], pt1[1], pt2[0], pt2[1], num )
        if doround:
            return ( int(out[0][0]), int(out[0][1]) )
        if not doround:
            return ( out[0][0], out[0][1] )





    ########################################################################
    #scanner specific stuff - consider moving 
    ######################################################################## 


    def fiducial_pivot(self, fiducials ):
        """
          assumes the fiducials have been pre-sorted 
          get the "pivot"  of the right triangle - center point of the hypotenuse
        """

        a = self.locate_pt_along(fiducials[1][0], fiducials[1][1], fiducials[2][0], fiducials[2][1], 1) 
        return a[0]

    def orient_by_corner(self, res_x, res_y, points, getAll=False):
        """
           take a random collection of 3 coordinates and determine the page rotation from that 
           this operates on ther assumption that the TOP RIGHT fiducial anchor is always closest to a corner

           1> look for which coordinate is closest to a corner 
           2> look for which corner it is closest to
           
        """
        #turn the page resolution into 4 (x,y) coordinates
        tl = (0,0);tr = (res_x,0)  
        bl = (0,res_y);br = (res_x,res_y)
        
        sortBuffer = []

        #print(tl,tr,bl,br)
        for pt in points:
            dist = self.calc_line_length( tl[0], tl[1], pt[0], pt[1] )
            sortBuffer.append( (dist, 'tl', pt ) ) 
            
            dist = self.calc_line_length( tr[0], tr[1], pt[0], pt[1] )
            sortBuffer.append( (dist, 'tr', pt ) )
            
            dist = self.calc_line_length( bl[0], bl[1], pt[0], pt[1] )
            sortBuffer.append( (dist, 'bl', pt ) )

            dist = self.calc_line_length( br[0], br[1], pt[0], pt[1] )
            sortBuffer.append( (dist, 'br', pt ) )
       
        sortBuffer.sort()

        if not getAll:
            return sortBuffer[0][1]
        if getAll:
            return sortBuffer[0] #return all of it 
                
    def old_calc_theta_vert(self, bot_xy, top_xy):
        #OLD ANGLE CALCULATOR - DOES NOT WORK WITH ALL CASES 
        #get the corner angle of theta from right triangle 
        #corner_xy = (top_xy[0],bot_xy[1])

        #####################
        # http://stackoverflow.com/questions/9614109/how-to-calculate-an-angle-from-points
        # dy = ey - cy
        # dx = ex - cx
        # theta = arctan(dy/dx)
        # theta *= 180/pi // rads to degs

        # function angle(cx, cy, ex, ey) {
        #   var dy = ey - cy;
        #   var dx = ex - cx;
        #   var theta = Math.atan2(dy, dx); // range (-PI, PI]
        #   theta *= 180 / Math.PI; // rads to degs, range (-180, 180]
        #   return theta;
        # }
        # function angle360(cx, cy, ex, ey) {
        #   var theta = angle(cx, cy, ex, ey); // range (-180, 180]
        #   if (theta < 0) theta = 360 + theta; // range [0, 360)
        #   return theta;
        # }

        a = bot_xy[1]-top_xy[1]  
        o = bot_xy[0]-top_xy[0]
        #if a==0 or o ==0:
        #    r = self.rad_to_deg(math.atan(o)) 
        #else:
        r = self.rad_to_deg(math.atan(o/a)) 
        return r


    def calc_theta_vert(self, start_xy, end_xy, corner, mode='relative'):
        """
           convert a 2 point line segment into a meaningful rotation value in degrees
           outputs a 0-360(?) degree rotation with 0/360 facing left from center , 180 right from center
           converts the line into a right triangle, calculates theta,
               absolute mode - projects the angle into a quadrant of a 0-360 degree circle
               relative mode - number of degrees of current rotation to get back to a normal page orientation

            instead of attempting more complex math, the rotation is filtered though a series of steps 
            that use the corner fiducial as a variable to determine which end is proper +Y axis.
            There are 4 cases, positive and negative (i.e.  rotated to the left , or the right for each of the 4 orintations) 
            the four states represent four page orientations (i.e.  up, down left,right)   
        """


        #get corner to build a right triangle
        a_x = end_xy[0]-start_xy[0]  
        a_y = end_xy[1]-start_xy[1]

        r = 0
        #relative offset (depending on order of start-end)
        if a_x != 0 and a_y !=0:
            r = ( self.rad_to_deg(math.atan(a_x/a_y))  )

        #make it positive
        if r <0:
            r = -r

        ################################
        ### if you want absolute rotation - "projected" into a circle to get 0-360
        #this is with 0/360 pointing to the left of center
        #DEBUG - ABSOLUTE MODE IS UNFINISHED/UNTESTED 
        if mode=='absolute':
            #this works with positive rotation ??debug            
            if end_xy[1]<start_xy[1]:
                if end_xy[0]<start_xy[0]:
                    r+=270
                if end_xy[0]>start_xy[0]:
                    r+=180       
            if end_xy[1]>start_xy[1]:
                  if end_xy[0]>start_xy[0]:
                    r+=90  

        ################################
        ###  if you want relative offset 
        if mode=='relative':        
            isnegative = False
            #first we need to determine if offset is positive or negative 
            if corner=='bl':
                if end_xy[0]<start_xy[0]:
                    isnegative = True
            if corner=='tr':
                if end_xy[0]>start_xy[0]:
                    isnegative = True            
            if corner=='br' :
                if end_xy[1]>start_xy[1]:
                    isnegative = True
            if corner== 'tl':
                if end_xy[1]<start_xy[1]:
                    isnegative = True

            #deal with positive rotation 
            if not isnegative:
                if end_xy[1]<start_xy[1]:
                    if end_xy[0]<start_xy[0]:
                        r=180-r
                    if end_xy[0]>start_xy[0]:
                        r=r+180       
                if end_xy[1]>start_xy[1]:
                      if end_xy[0]<start_xy[0]:
                        r=r  
                      if end_xy[0]>start_xy[0]:
                        r=360-r  

            #deal with negative rotation
            if isnegative:
                if end_xy[1]<start_xy[1]:
                    if end_xy[0]<start_xy[0]:
                        r=180-r
                    if end_xy[0]>start_xy[0]:
                        r=r+180       
                if end_xy[1]>start_xy[1]:
                    if end_xy[0]<start_xy[0]:
                        r=r   
                    if end_xy[0]>start_xy[0]:
                        r=360-r  

        #####
        if r == 0 or r == -0:
            """
              at this point we are done - unless the rotation came back as 0 or -0.
              why does it come back zero you may ask? because it uses a right triangle to calculate the theta - if the page is 
              too perfect it gets a line instead of a triangle and we cant form an anlge from it. In that case we fall back on 
              the self.corner to calculate the rotation.
            """
            #if it is zero - we can safely assume page is axis aligned - therefore we simply look at self.corner and Bob's yer uncle.
            if corner=='tl':
                r  = -90
            if corner=='tr':
                r  = 0                
            if corner=='br':
                r  = 90                
            if corner=='bl':       
                r = 180  
                                                           
        return r

    def sort_3_distances(self, mode, coords):
        """ take 3 XY points (triangle) and get the distances between all 3 
            return the sorted distances represented as two coordinate pairs
        """
        out = []
        tmp = []

        tmp.append((self.calc_line_length(coords[0][0], coords[0][1], coords[1][0], coords[1][1]), coords[0], coords[1]))
        tmp.append((self.calc_line_length(coords[1][0], coords[1][1], coords[2][0], coords[2][1]), coords[2], coords[1]))
        tmp.append((self.calc_line_length(coords[2][0], coords[2][1], coords[0][0], coords[0][1]), coords[2], coords[0]))

        tmp.sort()

        if mode=='shortest':
            out.append(tmp[0][1]);out.append(tmp[0][2])

        if mode=='middle':
            out.append(tmp[1][1]);out.append(tmp[1][2])

        if mode=='longest':
            out.append(tmp[2][1]);out.append( tmp[2][2])

        #we have the data but we need to keep the order intact 
        newout = [0,0,0]#create a work buffer with 3 elements
        
        for x in out:
            count = 0
            for f in coords:
                if x == f:
                    newout[count]=x
                count += 1
        
        #remove empty elements
        tmp = []
        for y in newout:
            if y:
                tmp.append(y)
        return tmp

    def project_axis_aligned_grid(self, topPts, sidePts, corner, fiducials, doRound=True, keepStraight=False):
        """
            calculates the score zone grid and performs auto rotation to the page 

            topPts       - the X axis scan "ticks"
            sidePts      - the Y axis scan "ticks"
            fiducials    - [3] - list of tuples of (x,y) anchors that form a triangle  
            doRound      - Bool  - works in integer instead of float 
            keepStraight - Bool  - returns the Axis aligned grid instead of the rotated grid 

        """
        
        rotation    = self.calc_theta_vert(fiducials[0], fiducials[2], corner)
        negrotation = -rotation
        pivot = self.fiducial_pivot(fiducials)
        x_rotated = []
        y_rotated = []

        if not topPts:
            return [] 
        
        if not sidePts:
            return [] 
        
        # rotate the ticks to "true" (e.g. axis aligned) so we can build a neat clean grid of boxes, 
        #  which then get rotated back to where they are originally
        tr_rotd = self.batch_rotate_pts(topPts , pivot, negrotation, doRound)
        sr_rotd = self.batch_rotate_pts(sidePts, pivot, negrotation, doRound)

        scoreZones = []  # list of zones to scan = N questions of 6 rows : [ [6], [6], etc ]
        
        
        row_ct = 0;col_ct = 0
  
        isr = iter(sr_rotd)
        y = int(len(sr_rotd)/2)

        #number of columns to look for in the scanned data  
        num_columns = 9
        
        def y_sorted_quad(item):
            return item[1]
        
        #build the grid of points using itertools looping through X and Y tick locations
        for sr in range(y):
            srilst = list( itertools.islice(isr, 2) )
            itr = iter( (tr_rotd) )
            question_row = [] #the six zones on a horizontal row 
        
            for t in range(num_columns): 
                trilst = list(itertools.islice(itr, 2))
                try:
                    quad = ( (trilst[0][0], srilst[0][1]), (trilst[1][0], srilst[0][1]), (trilst[1][0], srilst[1][1]), (trilst[0][0], srilst[1][1]) )
                except IndexError:
                    # We probably have a grid that ran off the page
                    continue
                    
                out_quad = []

                # We need quads:
                # quads[0] --> top left
                # quads[1] --> top right
                # quads[2] --> bottom right
                # quads[3] --> bottom left
                # sort by y then x value in the quad (sorted sorts by the first value of a tuple if not given a key)
                quad = sorted(quad, key=y_sorted_quad)
                top_quad = sorted(quad[0:2])
                bottom_quad = sorted(quad[2:4])
                bottom_quad.reverse()
                out_quad.extend(top_quad)
                out_quad.extend(bottom_quad)
                # end sort

                question_row.append( out_quad )
                 
            scoreZones.append(question_row) #add the horizontal rows to list of columns

        #if you want the "Axis aligned" non-oriented zones 
        #(you probably dont, unless you are testing or page is pre rotated) 
        if keepStraight:
            return scoreZones #no further rotation required 
            
        #this will rotate the grid score zones back to original orientation 
        else:  
            outZones = [] 
            for SZ in scoreZones:
               out_quad = [] 
               for quad in SZ:
                   sorted_quad = []
                   quad = self.batch_rotate_pts( quad, pivot, rotation, doRound)
                   out_quad.append(quad)
               outZones.append(out_quad)   
            return outZones 

###############################################

#class PointGen3D(PointGen2D, node_base):
class PointGen3D(PointGen2D, node_base):
    """
      point generator and container for a 3D object.

      It inherits all the 2D vector code (PointGen2D) so it is a Swiss Army Knife for all geometry.
      It also has a simple method to convert the 2D vectors into 3D so you can do fancy stuff.
      This does not use fancy math, it just adds a Z axis set to zero.

    """

    def __init__(self):
        super(PointGen3D , self).__init__()  

        self.points    = []                     #list of tuples of XYZ points per vertex         -  [(x,y,z), (x,y,z)]  
        self.polygons  = []                     #list of tuples for 2 or more vertex connections -  [(1,2,5,8) , (1,2)] 
        self.matrix44  = self.matrix_identity() #4X4 matrix for rotation of THIS object
        self.vec2d     = Vec2d(1,1)             #2Dvector to play around with 
        self.vec3d     = Vec3d(1,1,1)           #3Dvector to play around with

        #second buffer for file writing so the main buffer can be used as a work area
        self.pts_out  = []
        self.poly_out = []

        #render properties
        self.linecolor = (0,240,00)
        self.vtxcolor  = (0,240,00)

        #self.geom_history = []
        self.rot       = [0,0,0]
        self.pos       = [0,0,0]
        self.scale     = [1,1,1]



    ###############################################  
    def show(self):
        data = []
 
        tris = 0
        quads = 0
        other = 0        
        for p in self.polygons:
            if len(p)==3:
                tris+=1
            elif len(p)==4:
                quads+=1  
            else:
                other+=1

        data.append('\n############################')
        data.append('  position      : %s %s %s'%( self.pos[0], self.pos[1], self.pos[2]) )
        data.append('  rotation      : %s %s %s'%( self.rot[0], self.rot[1], self.rot[2]) )
        data.append('  scale         : %s %s %s'%( self.scale[0], self.scale[1], self.scale[2]) )
        data.append(' --------------------------- ' )        
        data.append('  num normals   : %s'      %(  'null' ) )#unimplemented
        data.append('  num verts     : %s'      %(  len(self.points) ) )
        data.append('  num polygons  : %s'      %(  len(self.polygons) ) )
        data.append(' --------------------------- ' )         
        data.append('  num triangles : %s'      %(   tris) )
        data.append('  num quads     : %s'      %(   quads) )  
        data.append('  num other     : %s'      %(   other) ) 
        data.append('############################\n')

        for d in data:
            print(d)

    ############################################### 
    def get_mean_z(self, triangle):
        z1 = triangle[0][2]
        z2 = triangle[1][2]
        z3 = triangle[2][2]
        return (z1+z2+z3)/3

    ###############################################     
    def calc_bbox(self, object):
        """ UNFINISHED """
        maxx = 0
        maxy = 0
        maxz = 0
        
        for p in self.points:
            print(p)

    ###############################################  
    def get_face_verts(self, fid):
        """ lookup and return the constituent points of a polygon """
        tmp = []

        if fid<0 or fid > len(self.polygons)-1:
            print('#show_poly- bad face index : %s'%fid)
            return None

        for v_id in self.polygons[fid]:
            tmp.append(self.points[v_id-1])

        return tmp

    ###############################################  
    def get_face_normal(self, fid):
        """ UNFINISHED """
        tmp = self.get_face_verts(fid) 

        data = []
        data.append('\n############################')
        #data.append(str(tmp) )
        data.append('############################\n')

        #for d in data:
        #    print(d)  

    ###############################################  
    def get_face_edges(self, fid):
        """ UNFINISHED 
            return boundary edge segments as arrays of lines in 3D
            for extruding  
        """
        tmp = self.get_face_verts(fid) 

        data = []
        data.append('\n############################')
        #data.append(str(tmp) )
        data.append('############################\n')

        #for d in data:
        #    print(d) 

    ###############################################  
    def get_face_centroid(self, fid):
        """ UNFINISHED 
            return center of a polygon by ID 

            for extruding  
        """
        tmp = self.poly_centroid(self.points) 

        data = []
        data.append('\n############################')
        #data.append(str(tmp) )
        data.append('############################\n')

        #for d in data:
        #    print(d)  


    ###############################################  
    def show_poly(self, id):
        """ lookup and return the constituent points of a polygon """
        tmp = self.get_face_verts(id)   
        data = []
        data.append('\n############################')
        data.append(str(tmp) )
        data.append('############################\n')

        for d in data:
            print(d)

    ###############################################  
        
    def extrude_face(self, f_id):
        """ UNFINISHED """
        #edges = self.get_face_edges
        #for e in edge:
        #    build_poly(e)
        #ETC
        pass 

    ###############################################   
    def poly_centroid(self, triangle):
        """ get 3D center of object (average XYZ point) """
        x1 = triangle[0][0]
        x2 = triangle[1][0]
        x3 = triangle[2][0]  
        
        y1 = triangle[0][1]
        y2 = triangle[1][1]
        y3 = triangle[2][1]
        
        z1 = triangle[0][2]
        z2 = triangle[1][2]
        z3 = triangle[2][2]
        
        x= (x1+x2+x3)/3
        y= (y1+y2+y3)/3
        z= (z1+z2+z3)/3

        return [x,y,z]

    ###############################################  
    def z_sort(self):
        """ return a sorted list of polygons by average Z coordinate 
            lowest z value is (closest?) to camera 
        """
        out = []
        tmp = []
        #build a list of [mean z, [points, polygon] ]
        #sort by mean z value, and return the sorted list 
        for p in self.polygons:
            tri = []
            for idx in p:
                tri.append(self.points[idx-1])
            mean = self.get_mean_z(tri)
            tmp.append( (mean, p) )
        
        #tmp.sort(reverse=True)
        tmp.sort()

        for t in tmp:
            out.append(t[1])    
        
        self.polygons = out
        #return out

    ###############################################  
    def scribe(self, str):
        print(str)

    ###############################################  
    def move_pts(self, offset=(0,0,0)):
        """ transform POINTS not object - actually changes geometry"""
        shifted = []
        for pt in self.points:
            shifted.append( (pt[0]+offset[0], pt[1]+offset[1], pt[2]+offset[2] )  ) 
        self.points = shifted

    ###############################################  
    def scale_pts(self, offset=(0,0,0)):
        """ transform POINTS not object - actually changes geometry"""        
        shifted = []
        for pt in self.points:
            shifted.append( (pt[0]*offset[0], pt[1]*offset[1], pt[2]*offset[2] )  ) 
        self.points = shifted

    ###############################################  
    def rotate_pts(self, rx, ry, rz):
        """ 
            transform POINTS not object - actually changes geometry        
            derived from pointgen2d method rotate_mat4 
            this simply rotates a 4X4 matrix to be attached to a 3D object
        """
        self.repair()#may fix or find problems 

        self.rot = [rx, ry, rz]

        #build rotationY (see diagram above) 
        y_matrix =  self.matrix_identity()
        y_matrix[0]  =  math.cos(self.deg_to_rad( ry ))
        y_matrix[2]  = -math.sin(self.deg_to_rad( ry ))
        y_matrix[8]  =  math.sin(self.deg_to_rad( ry ))
        y_matrix[10] =  math.cos(self.deg_to_rad( ry ))
              
        #build rotationZ (see diagram above) 
        z_matrix    =  self.matrix_identity()
        z_matrix[0] =  math.cos(self.deg_to_rad( rz ))
        z_matrix[1] =  math.sin(self.deg_to_rad( rz ))
        z_matrix[4] = -math.sin(self.deg_to_rad( rz ))
        z_matrix[5] =  math.cos(self.deg_to_rad( rz ))
        tmp_matr = self.mult_mat4( y_matrix, z_matrix)   

        #build rotationX (see diagram above) 
        x_matrix =  self.matrix_identity()
        x_matrix[5]  =   math.cos(self.deg_to_rad( rx )) 
        x_matrix[6]  =   math.sin(self.deg_to_rad( rx )) 
        x_matrix[9]  =  -math.sin(self.deg_to_rad( rx ))
        x_matrix[10] =   math.cos(self.deg_to_rad( rx ))
        self.matrix44 = self.mult_mat4( x_matrix, tmp_matr )  

        
        self.apply_transforms()


    ############################################### 
    def triangulate(self):
        """ 
            Only works on 3 or 4 sided polygons. 3 are passed unchanged, 4 are triangulated  
            turn a quad into two triangles 
            return a new 3d object (possibly with more new polygons, all triangles) 
        """
        out_polys = []

        for f_id in range(len(self.polygons)):
            num_vtx = (len(self.polygons[f_id]))
            tri1 = []
            tri2 = []
            #####four sided ######
            if num_vtx==4:
                print('FOUR SIDED!')
                out_polys.append( (2,3,4) )               
                out_polys.append( (1,2,3) )              
                #out_polys.append(self.polygons[f_id])

            #####three sided #########
            if num_vtx==3:
                #print('THREE SIDED!')                
                out_polys.append(self.polygons[f_id])

        #overwrite old data 
        self.polygons = out_polys



    ###############################################  
    
    def repair(self):
        """ walk internal data and fix any bad data found  (empty point tuples, etc) """

        fix = []

        for pt in self.points:

            #iftype ==  <class 'tuple'>
            if len(pt)==0:
                self.scribe('found bad data - empty vertex')
             
            #CASE     
            #elif len(pt)==0:
            #    self.scribe('found bad data ')
            
            #CASE
            #

            else:
                fix.append( pt )
        self.points = fix


    ###############################################  
    def apply_transforms(self):
        """
            update the point data to reflect internal matricies 
        """
        ############ 
        tmp_buffer = []
        out = None
        #rotate points to scan  
        for pvec in self.points:  
            out = self.mult_vec3_mat4(self.matrix44, (pvec[0], pvec[1], pvec[2]) )
            tmp_buffer.append( ( out[0], out[1], out[2] ) )
        
        self.points= tmp_buffer
        #return tmp_buffer

    ###############################################  
    def cvt_2d_to_3d(self, points):
        """ convert 2d points into 3d by adding an empty z axis 
        """

        newpts = []
        for pt in points:
            newpts.append( (pt[0], pt[1], 0)   )
        return newpts

    ############################################### 
    def locate_pt_along3d(self, x1, y1, z1, x2, y2, z2, num):
        """
            overloaded method for 3D 
            given two 3D points, return a series of N number connecting points in 3D 
        """

        pts_created = []
        fpos=(x1, y1, z1)
        spos=(x2, y2, z2)
         
        for n in range(num):
            npos = [3]

            npos[0]     = spos[0]+(((fpos[0]-spos[0])/(num+1))*(n+1))
            npos.append(  spos[1]+(((fpos[1]-spos[1])/(num+1))*(n+1))  )
            npos.append(  spos[2]+(((fpos[2]-spos[2])/(num+1))*(n+1))  )

            pts_created.append( (npos[0], npos[1], npos[2]) )
        return pts_created


    ############################################### 
    ############################################### 
    ############################################### 

    #load/dump numbered point caches and reload - very powerful idea!
    def load_obj(self, filename):
        """ 
            DEBUG - DOES NOT CLEAR BUFFERS FIRST!!
            so if you load two models, the points - polygons will be merged and have bad topology

            load a wavefront OBJ file into model's point/poly memory 
            you can save shape or cache data 
        """

        if os.path.lexists(filename) == 0:
            self.scribe("%s DOES NOT EXIST !! "%filename )
            #raise
            
        if os.path.lexists(filename):
            f = open( filename,"r", encoding='utf-8')
            contents = f.readlines()
            for x in contents :
                #lines = x
                nonewline = x.split('\n')
                tok =  nonewline[0].split(" ") 
                if tok[0]!='#':
                    ###
                    #THIS NONSENSE IS TO CLEAN UP ERRANT SPACES IN FILE 
                    clndat = []
                    for f in tok:
                        if(f!='' ):
                            clndat.append(f) 
                    if len(clndat)==5 or len(clndat)==4:
                        tok=clndat    
                        numtok = len(tok)               
                        #THIS NONSENSE IS TO CLEAN UP ERRANT SPACES IN FILE 
                        
                        ###
                        #VERTECIES 
                        if tok[0]=='v':
                            self.points.append( (float(tok[1]), float(tok[2]), float(tok[3]) ) ) 

                        #FACES
                        if tok[0]=='f':
                           # print('face found ', tok[1],tok[2],tok[3],tok[4])
                           b1 = tok[1].split('/')
                           b2 = tok[2].split('/')
                           b3 = tok[3].split('/')

                           #four sided polygons   
                           if numtok==4:
                               poly = ( int(b1[0]),  int(b2[0]), int(b3[0])  )
                               
                           #three sided polygons      
                           if numtok==5:
                               b4 = tok[4].split('/')
                               poly = ( int(b1[0]),  int(b2[0]), int(b3[0]), int(b4[0]) )


                           self.polygons.append( poly )

                #NORMALS 
                #if tok[0]=='vn':
                #    print('normal found ', tok)
                
                #UV's
                #if tok[0]=='vt':
                #    print('texture UV found ', tok)

    ###############################################  

    def save_obj(self, filename, as_lines=False):
        """ format the data so blender (or anything else) can read it  
            this will save points and polygons as a wavefront OBJ file 
            you can save shape or cache data. 
        """    
        
        ##################
        self.repair()#optional but this will help find/fix problems later


        buf = [] #array of strings to be written out as the OBJ file

        buf.append("# Created by Magic Mirror render toy.")
        buf.append("# Keith Legg - December 2015.\n\n")        

        buf.append('\n#these define the vertecies')
        for p in self.points:
             buf.append('v %s %s %s'%( p[0], p[1], p[2]) ) #x y z components 
        
        buf.append('\n#these define the polygon geometry')
        for ply in self.polygons:
            plybuf = ''
            for f in ply:
                #plybuf = plybuf +(' %s'%str(int(f)+1) ) #add one because OBJ is NOT zero indexed
                plybuf = plybuf +(' %s'%str(int(f)) ) #add one because OBJ is NOT zero indexed

            if as_lines:#save as lines
                buf.append('l %s'%plybuf)
            else:#save as polygons 
                buf.append('f %s'%plybuf)
 
        buf.append('\n')

        ################################### 
        #Our filebuffer is an array, we need a string so flatten it 
        output = ''
        for s in buf:
            output=output+s+'\n'

        self.scribe('###file "%s" saved' % filename)

        #save it to disk now
        fobj = open( filename,"w") #encoding='utf-8'
        fobj.write(output)
        fobj.close()
  
    ############################################### 
    ###############################################  
    def make_sphere(self, size=1.0):
        """ Not done yet - this makes a circle """
        spokes = 8
        circpts = self.calc_circle(0, 0, size, spokes, False)   #2D data
        self.points = self.cvt_2d_to_3d(circpts)            #converted to 3D
 

        tmp = []
        for x in range(spokes):
            tmp.append(x)
        tmp.append(0) #make periodic - insert start at end to close the cicle
        self.polygons = [tuple(tmp)]


    ###############################################  
    def make_cone(self, size=1.0):
        """ Not done yet - this makes a cone """
        spokes = 8
        circpts = self.calc_circle(0, 0, size, spokes, False)   #2D data
        self.points = self.cvt_2d_to_3d(circpts)            #converted to 3D
        tmp = []
        for x in range(spokes):
            tmp.append(x)
        tmp.append(0) #make periodic - insert start at end to close the cicle
        self.polygons = [tuple(tmp)]


    ###############################################  
    def prim_triangle(self, size=1):
        """ single polygon operations (that can be stacked together ?) """
        tripts = [(-size,0,0), (0,size,0), (size,0,0) ]
        plyidx = (1,2,3)
       
        n = len(self.points) # add this number to the indexes in case of existing geom 
        #append points to internal 
        for p in tripts:
            self.points.append(p)
        
        #append poly indexes to internal 
        plytmp = []      
        for x in plyidx:
            plytmp.append(x+n)            
        self.polygons.append( tuple(plytmp) ) #polygons are tuples so convert from list 

    ###############################################  
    def prim_circle(self, pos=(0,0,0), rot=(0,0,0), size=1, spokes = 5):
        """ single polygon operations (that can be stacked together ?) """        
        n = len(self.points) #add index value to the end of the current number of points
        circpts = self.calc_circle(0, 0, size, False, spokes, False)   #2D data
        for pt in self.cvt_2d_to_3d(circpts):  #converted to 3D
            self.points.append(pt)
        tmp = []
        for x in range(spokes):
            #we add one because  calc_circle returns zero indexed data but OBJ is NOT zero indexed
            tmp.append(x+1+n)#add this number to the indexes in case of existing geom 
        self.polygons.append( tuple(tmp) )        


    ###############################################  
    def prim_cube(self, pos=(0,0,0), size=1):
        """ single polygon operations (that can be stacked togteher ?) """
        pointbfr = []
        plybfr   = []
       
         
        #by adding position argument we can create it in different places
        pointbfr.append( (-size+pos[0], -size+pos[1], size+pos[2])  )#vertex 0
        pointbfr.append( (-size+pos[0],  size+pos[1], size+pos[2])  )#vertex 1
        pointbfr.append( ( size+pos[0],  size+pos[1], size+pos[2])  )#vertex 2  
        pointbfr.append( ( size+pos[0], -size+pos[1], size+pos[2])  )#vertex 3
        #notice these next 4 are the same coordinates with a negative Z instead!
        pointbfr.append( (-size+pos[0], -size+pos[1], -size+pos[2])  )#vertex 4
        pointbfr.append( (-size+pos[0],  size+pos[1], -size+pos[2])  )#vertex 5
        pointbfr.append( ( size+pos[0],  size+pos[1], -size+pos[2])  )#vertex 6  
        pointbfr.append( ( size+pos[0], -size+pos[1], -size+pos[2])  )#vertex 7

        #plot the connections between the points that will form polygons
        plybfr.append( (1,2,3,4) ) #polygon 0  #front
        plybfr.append( (5,8,7,6) ) #polygon 1  #top
        plybfr.append( (1,5,6,2) ) #polygon 2  #back
        plybfr.append( (2,6,7,3) ) #polygon 3  #right
        plybfr.append( (3,7,8,4) ) #polygon 4  #bottom
        plybfr.append( (5,1,4,8) ) #polygon 4  #bottom
        
        ######################
        n = len(self.points) # add this number to the indexes in case of existing geom 
        #append points to internal 
        for p in pointbfr:
            self.points.append(p)
        
        #append poly indexes to internal 
        for ply in plybfr:
            plytmp = []  
            for pt in ply:
                plytmp.append(pt+n)            
            self.polygons.append( tuple(plytmp) ) #polygons are tuples so convert from list 




