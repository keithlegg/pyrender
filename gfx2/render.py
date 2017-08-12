
import os
import math 
import shutil #?

#this contains PIL blur function among others 
from PIL import ImageFilter 

###################################################
from pycv.raster_ops import * #bitmap images 
from pycv.point_ops import * #vector data
from pycv.kdag import *   #scenegraph and friends
###################################################

""" 
****************************************************
    *** MAGIC MIRROR RENDERER ***
        Ye old polygone cube 

                   Y
                   |
                   |
             V5----|------V6
            / |    |     / |
           /  |         /  |
         V1-----------V2   |
          |   |        |   | 
  X-------|   |        |   |     FRONT VIEW OF CUBE 
          |   /V4------|--/V7       LOOKING ON Z
          |  /         | /
          | /   /      |/
         V0----/-------V3
              /
             /       
            Z
****************************************************
    TODO:
       ###################
       setup scene graph and interface ... 
      
       ###################
       add perspective

       ###################
       ideas for polygon attributes and methods 
         - bounding box
         - center/pivot
         - rotation XYZ
         - scale 
         - translation
         - default color 
         - visibility/ render visible
           
****************************************************
"""
###################################################

class model_3d(PointGen3D):
    """ placeholder that IS actually doing something 
        inherits from point gen 3d- go look at that to see what is here
    """
    pass  


###################################################
class renderImage_OP(object): #pycv.kdag.dagop):
    """ 
            inspired by houdini , [raster,vector] compond data container and operator.
            The idea is - make code as small as possible, but powerfull enough to facilitate
            programatic access to any part of the data you want to work with.

 
        Works in 2D and 3D!

        this object is the "meat and potatoes" of this whole operarion.
        Inspired by Side Effects Houdini, it is a renderer that returns three things:

        - A frambuffer with the rendered result,
        - Vector cache of what was rendered, so you can tweak things post process.
        - Vector cache of the 3D geometry that was rendered, so you can procedurally use the output to build other thigns.
  
        ---------------------------------------------
        TODO:
            - draw normals 
            - draw origin 
            - draw vectors 
            
        ---------------------------------------------

    """
    ## ## ## ## ## 
    def __init__(self, resx, resy, framebuffer=None):
        self.pg = PointGen3D()       #use this for the matrix rotation and more
        self.fb = PixelOp()         #framebuffer and raster freinds
        self.rp   = [] #render path data  (lines)
        self.rpts = [] #render point data
        
        if framebuffer==None:
            self.res = [resx, resy]
            self.fb.create_buffer(resx, resy)
        
        if framebuffer:
            self.fb = framebuffer
            self.res = [framebuffer.res_x, framebuffer.res_y]

        self.is_orthographic = True

    ## ## ## ## ##  
    def scribe(self, str):
        print(str)

    ## ## ## ## ##  
    def project_point(self, pt,  rx, ry, rz, scale, res_x=None, res_y=None):
        """
           project 3D point geometry into 2D
        """
        if res_x==None:
            res_x = self.res[0]
        if res_y==None:
            res_y = self.res[1]

        center = (int(res_x/2), int(res_y/2) ) #we will need to know center of image when we project geometry into screen space
        pvtxs = self.pg.rotate_mat4( [pt], rx, ry, rz )

        sx =  ((pt[0]*scale) +center[0])  
        sy =  ((pt[1]*scale) +center[1])  
   
        return (sx,sy)

    ## ## ## ## ##  
    def project_points(self, object3d,  rx, ry, rz, scale, res_x=None, res_y=None):
        """
           project 3D point geometry into 2D
        """
        if res_x==None:
            res_x = self.res[0]
        if res_y==None:
            res_y = self.res[1]

        center = (int(res_x/2), int(res_y/2) ) #we will need to know center of image when we project geometry into screen space
        pvtxs = self.pg.rotate_mat4( object3d.points, rx, ry, rz )
        points_projected = []

        for p in pvtxs:
            x = p[0]  
            y = p[1]  
            sx =  ((x*scale) +center[0])  
            sy =  ((y*scale) +center[1])  
            points_projected.append( (sx,sy) )
   
        return points_projected

    ## ## ## ## ##  
    def project_polygons(self, object3d,  rx, ry, rz, scale, res_x=None, res_y=None):
        """
          project 3D line geometry into 2D.

          You can convert this data INTO 3d by adding an empty Z axis.
             - - - 
          iterate through each point (vector) and mutliply it by a rotation 4X4 matrix
          A matrix is not that scary, it is simply a container for 3 rotations
          it can also be thought of as three vectors X rot, Y rot, and Z rot.
        """
        if res_x==None:
            res_x = self.res[0]
        
        if res_y==None:
            res_y = self.res[1]

        center = (int(res_x/2), int(res_y/2) ) #we will need to know center of image when we project geometry into screen space

        #this were the 3d rotation happens , rx ry and rz is combined rotation for the object
        #the three numbers work togther to appear to rotate in space, 
        #Its really just fancy rotating in a circle based on sin and cos 
        pvtxs = self.pg.rotate_mat4( object3d.points, rx, ry, rz )
        
        #pvtxs = self.pg.buildPerspProjMat( object3d.points )

        ##########################
        #you can render a 3d object without any math at all! it will be awfully boring without rotations.
        #pvtxs = object3d.points <- uncomment to draw with NO projection at all

        lines_to_draw = []
        ##########################
        #print('render geom info  points:%s poly:%s'%(len(object3d.points), len(object3d.polygons) )  )
        ##########################
        #project rotated points into screen space  
        for ply in object3d.polygons:
            num_idx = len(ply) #walk array of indeces to vertecies
            for pt in range(num_idx):

                if pt<num_idx-1:
                    #a line needs two points, simply walk through the list two at a time
                    idx  = int(ply[pt])-1 #index start of line in 2d
                    idx2 = int(ply[pt+1])-1 #index end of line in 2d
                    
                    # #start of line
                    x = pvtxs[idx][0] #first vtx - x component  
                    y = pvtxs[idx][1] #first vtx - y component 
                    # #end of line
                    x2 = pvtxs[idx2][0] #first vtx - x component  
                    y2 = pvtxs[idx2][1] #first vtx - y component 

                    #attempt at perspective rendering . math, BLAH!
                    if self.is_orthographic==False:
                        #here is my sad attempt at cheapo perspective:
                        scale   = (scale+(z/5) )   #terrible perspective illusion,  but a really cool effect
                    
                    #start of line to draw in 2d 
                    sx =  ((x*scale) +center[0])  
                    sy =  ((y*scale) +center[1])  
                    #end of line to draw in 2d
                    ex =  ((x2*scale)+center[0])  
                    ey =  ((y2*scale)+center[1])    
                    lines_to_draw.append(  ( (sx,sy), (ex, ey) ) )
   
        return lines_to_draw

    ## ## ## ## ## 
    def render(self, color, rx, ry, rz, thick, scale, framebuffer=None, object3d =None,):
        """
                                 **$$!! inspired by Houdini !!$$** 

            returns compund data so you can wire this object into itself
            format is [raster,vector] 

            this strives to be a container and operator.

            framebuffer and object3d are not required, if none specified it will automatically 
            create deafaults. 

            If you pass in a framebuffer, you can render on top of other images, like simple compositing.

            Object3d can be (any object?) as long as it contains  self.points and self.polygons data 
            
            The goal is to procedurally create and store all creation history. 

        """               
        #output image properties 
        res_x = self.res[0]
        res_y = self.res[1]

        ###########################

        #if no object specified, build a default cube  
        if object3d==None:  
            kube = model_3d() 
            kube.prim_cube()
            #kube.make_sphere()
            object3d = kube #assign object to be cube we just built
        
        ###########################

        #optional framebuffer passed in so we can render on top of other images
        if framebuffer:
            rndr_bfr = framebuffer
        else:
            #default is to just make a new framebuffer from scratch
            rndr_bfr = self.fb 
            rndr_bfr.create_buffer(res_x, res_y)#make a new image in memory
            rndr_bfr.fill_color( (25,20,25) ) #make bg all dark 
        
        ###########################
        #RENDER LINE GEOM 
        self.rp = self.project_polygons(object3d, rx, ry, rz, scale, res_x, res_y)
        for l in self.rp:
            #DRAW LINES - cool ghosting effect by rendering twice in different thickness
            rndr_bfr.connect_the_dots( l ,  self.fb.tint(color,'drkr') ,thick        )  #points, color, thickness  
            if thick>1:                  
                rndr_bfr.connect_the_dots( l ,  color                   ,int(thick/2) )  #points, color, thickness
          

        ###########################
        #RENDER POINT GEOM 
        self.rpts = self.project_points(object3d, rx, ry, rz, scale, res_x, res_y)
        rndr_bfr.draw_points_batch( self.rpts ,  (255,255,0) , int(thick)        )  #points, color, thickness
        
        self.fb = rndr_bfr

        return [self.fb, self.pg, self.rp]# [FRAMEBUFFER, GEOMETRY, RENDER PATHS] 

    ## ## ## ## ##  
    def vector_render(self, rx, ry, rz, vscale, infile, outfile):
        """ render an image and output the data to an OBJ file!! """

        x = model_3d() 
        x.load_obj(infile)
        
        rscale = 100 #size of points projected

        """
         use image render op to run a render a 2D image so we can have some renderpath data
         thickness and color are meaningless here, only the shapes it generates
         below is an OBJ polygon exporter than saves vector data into a wavefront OBJ 
        """
        mypic = self.render( (0,0,0), rx, ry, rz, 1, rscale*4, None, x)
        vtx_bfr = []
        face_bfr = []
        idx = 1

        for line in mypic[2]:
            paths3d = ( self.pg.cvt_2d_to_3d(line) )
            for dat in paths3d:
                vtx_bfr.append('v %s %s %s'%(dat[0]*vscale, dat[1]*vscale, dat[2]*vscale) )
            face_bfr.append('l %s %s'%(idx+1, idx) )
            idx+=2 #since we always add two pts at a time this works
        """
         Our OBJ model data is in two arrays of float type data (points and polygons) 
         we need a single string to stream out to a file 
         these two for loops flatten the data into a single string 
        """
        output = ''
        for s in vtx_bfr:
            output=output+'%s\n'%s
        for s in face_bfr:
            output=output+'%s\n'%s

        self.scribe('#saving file %s'%outfile)
        #save OBJ file to disk , it is 2d data in 3d space
        fobj = open( outfile,"w", encoding='utf-8')
        fobj.write(output)
        fobj.close()

   
    ## ## ## ## ##
    ## ## ## ## ##
       
    #def render(self, color, rx, ry, rz, thick, scale, framebuffer=None, object3d =None,):
    def scanline(self, path, scale=200, infile=None, numframes=5):
        vecmath = Vec2d(0,0) #use for math operations
        output = self.fb 
        #scale = 200 #projection scale

        res_x = self.res[0]
        res_y = self.res[1]
        center = (self.res[0]/2, self.res[1]/2)
        
        ###############################################
        #RENDER PROPERTIES TO PLAY WITH 
        SHOW_VEC_HITS = False  #faces cover this up!
        SHOW_EDGES = True
        SHOW_FACES = True
        SHOW_NORMALS = True #NOT DONE JUST A DOT IN 3D CENTER
        COLOR_MODE = 'zdepth'    ####'flat', 'zdepth',  'normal' 
        ###############################################

        #mark the 0 point for convenience
        #output.horiz_line(res_y/2, (255,0,255) ) 

        #obj.prim_triangle()
        #obj.scale_pts( (.5,.5,.5) )
        #obj.move_pts( (5,5,5) )

        ###############################################
        #save current buffer as tmp to "freeze" it prior to animation
        self.fb.save_file('tmp.png')

        ###############################################
        for ct in range(1,numframes):  
            #output.create_buffer(res_x,res_y)# reset fb
            #you could also save and load tmp fil to "clear" it
            self.fb.load_file('tmp.png')

            #rotatedvtx = self.pg.rotate_mat4( obj.points, ct, ct, 0 )
            #sortedply = self.z_sort(rotatedvtx, obj.polygons)
            
            obj = model_3d() 
            #obj.prim_cube()
            obj.load_obj(infile)
            #obj.move_pts( (0,0,10) ) 
            #obj.points = [(-2,0,0), (0,3,0), (2,0,0) ]   #define 3 points in 3D (basically 2D with 0 for Z axis)
            #obj.polygons = [ (1,2,3) ]                   #connect vertecies #1 to #2 to #3
            
            #obj.triangulate()
            obj.rotate_pts(ct*5,ct*5,180)
            obj.z_sort()
            
            cnt = 0

            for ply in obj.polygons:
                num_idx = len(ply) #number of vertecies per poly 
                drwply = [] #3 points of triangle to draw
                
                for pt in range(num_idx):
                    idx = int(ply[pt])  
                    drwply.append( obj.points[idx-1] )

                #build up line data for three sides of triangle
                s1 = ( (drwply[0][0]*scale)+center[0], (drwply[0][1]*scale)+center[1] )
                e1 = ( (drwply[1][0]*scale)+center[0], (drwply[1][1]*scale)+center[1] )
                #
                s2 = ( (drwply[1][0]*scale)+center[0], (drwply[1][1]*scale)+center[1] )
                e2 = ( (drwply[2][0]*scale)+center[0], (drwply[2][1]*scale)+center[1] )
                #
                s3 = ( (drwply[2][0]*scale)+center[0], (drwply[2][1]*scale)+center[1] )
                e3 = ( (drwply[0][0]*scale)+center[0], (drwply[0][1]*scale)+center[1] )
              
                ##########                ##########   
                
                """
                 PERSPECTIVE TEST - ALWAYS CRASHED ON FRAME 17??
                 I think because values need to be clamped AND/OR clipped to screen 

                """
                # s1 = ( ((drwply[0][0]/drwply[0][2])*scale)+center[0], ((drwply[0][1]/drwply[0][2])*scale)+center[1] )
                # e1 = ( ((drwply[1][0]/drwply[1][2])*scale)+center[0], ((drwply[1][1]/drwply[1][2])*scale)+center[1] )
                # s2 = ( ((drwply[1][0]/drwply[1][2])*scale)+center[0], ((drwply[1][1]/drwply[1][2])*scale)+center[1] )
                # e2 = ( ((drwply[2][0]/drwply[2][2])*scale)+center[0], ((drwply[2][1]/drwply[2][2])*scale)+center[1] )
                # s3 = ( ((drwply[2][0]/drwply[2][2])*scale)+center[0], ((drwply[2][1]/drwply[2][2])*scale)+center[1] )
                # e3 = ( ((drwply[0][0]/drwply[0][2])*scale)+center[0], ((drwply[0][1]/drwply[0][2])*scale)+center[1] )
      
                ##########                ##########      
                #edge lines
                l1 = [(s1[0], s1[1]), (e1[0], e1[1])]  
                l2 = [(s2[0], s2[1]), (e2[0], e2[1])]  
                l3 = [(s3[0], s3[1]), (e3[0], e3[1])]  

                ##########                ##########   
                #calculate the normal for the triangle and use to generate color
                n = vecmath.crossProduct(drwply[0], drwply[1] )
                n2 = vecmath.normalize3d(n) 

                ##########                ##########   
                #add some color to the polygons here  
                    
                if COLOR_MODE=='normal':    
                    #attempt at coloring by face normal - not good
                    facecolor = output.normal_to_color(n2)
             
                if COLOR_MODE=='zdepth':                 
                    #COLOR BY Z DISTANCE FROM CAMERA
                    zgrad = int(drwply[0][2]*200)
                    facecolor = (zgrad,zgrad,zgrad )
                
                if COLOR_MODE=='flat':                 
                    facecolor = (100,100,100 )

                ##########
                #HERE IS THE SCANLINE - ITERATE EACH HORIZONTAL ROW AND DO VECTOR MATH
                for hscan in range(1,res_x):
                    s_hvec = (-1*(res_x/2),hscan)
                    e_hvec = (       res_x,hscan)

                    i = vecmath.intersect(s_hvec, e_hvec, s1, e1) #left  side of triangle
                    j = vecmath.intersect(s_hvec, e_hvec, s2, e2) #right side of triangle
                    k = vecmath.intersect(s_hvec, e_hvec, s3, e3) #top   side of triangle

                    if SHOW_VEC_HITS:
                        #DRAW INTERSECTION POINTS FOR SCAN LINE 
                        #THESE BECOME THE LINE SEGMENTS THAT FILL THE POLYGON
                        if i: 
                            output.draw_fill_circle( i[0], i[1], 1, (255,0,0) ) 
                        if j: 
                            output.draw_fill_circle( j[0], j[1], 1, (0,255,0) )  
                        if k: 
                            output.draw_fill_circle( k[0], k[1], 1, (0,0,255) )  

                    if SHOW_FACES:
                        if i and j: 
                            drawlin = [i,j]
                            output.connect_the_dots( drawlin, facecolor, 1)
                        if i and k:
                            drawlin = [i,k]
                            output.connect_the_dots( drawlin, facecolor, 1)
                        if j and k:
                            drawlin = [j,k]
                            output.connect_the_dots( drawlin, facecolor, 1) 

                
                ##################                
                if SHOW_NORMALS:
                    #draw face normal 
                    cn =  obj.poly_centroid(drwply) 
                    cntr_pt = ( (cn[0]*scale)+center[0], (cn[1]*scale)+center[1] ) 
                    output.draw_fill_circle( cntr_pt[0], cntr_pt[1], 2, (255,255,20) )

                if SHOW_EDGES:
                    #draw polygon edges 
                    output.connect_the_dots( l1, (0,255,0), 1) 
                    output.connect_the_dots( l2, (0,255,0), 1) 
                    output.connect_the_dots( l3, (0,255,0), 1)                 
 
            output.save_file('%s/scanlinez_%s.png'%(path, ct)) 
   
   
    ## ## ## ## ## 
    def post_process(self, command):
        """ you can do anything to the image that PIL can do. Here are some examples of that. """
        if command =='blur':
            #self.fb.fb.imgflt()
            self.fb.fb = self.fb.fb.filter(ImageFilter.GaussianBlur)

    ## ## ## ## ## 
    def save_image(self, filename='output.png'):
        self.fb.save_file(filename)
 
###################################################

class animate(object):
    """ a test class that interfaces to all the others and exports animation.
        All the other fucntions accept arguemnts that you can pass in that will adjust 
        animatable properties to affect the look of a render.

    """
    def __init__(self):
        #render properties
        self.rscale = 70
        self.numframes = 1
        #this is the node that is both image and geometry.
        #you can use its output as in inpu bck to itself
        self.irop = renderImage_OP(640,480)  

    def setup_disk(self, path = 'anim'):
        """ create output folder for the frames to end up in.
            Warning - It destructivly deletes what is there if it finds anything.

        """
        print('\n\n')
        #delete folder if it exists
        if os.path.exists(path):
            print('deleting directory %s'%path)
            shutil.rmtree(path)
        print('creating directory %s'%path)    
        os.makedirs('anim')


    def image_render(self, filename=None, numframes=20):
        """
          Prototype interface to renderImage_OP 
          
          The idea is that renderImage_OP is a nestable object tree/ renderer. 
          You can render and feed it back into itself! 
        """    
        self.numframes = int(numframes/2)
        self.setup_disk()#clear output if exists and make new

        useobj = model_3d() 
        if filename:
            #load a wavefront OBJ exported fron Blender
            useobj.load_obj(filename)
            #useobj.make_sphere() 
        else:
            useobj.prim_cube(.6)

        framect = 0 
        dorot = 0
        for p in range(self.numframes):
            #start with an ordinary render - it will return a compound type of framebuffer AND geometry
            #you can reuse the geometry to build other post-render effects, neat huh?
            mypic = self.irop.render( (0,200,0), dorot, dorot, 180, 2, self.rscale*4, None, useobj)
       
            dorot = p*5
            ##########
            #save out the numbered image result when we are done playing 
            self.irop.save_image('anim/out_%s_.png'%framect );framect+=1

        ####################################################################################
        """
           demo of post render effects drawn after the render
        """
        #you can step into another render loop and pass variables between them to pass state 
        for p in range(self.numframes):
            mypic = self.irop.render( (0,200,0), dorot, dorot, 180, 3, self.rscale*4, None, useobj)
            
            #clear the render cache and redraw it with renderpath data, damn this is cool!            
            self.irop.fb.fill_color((0,0,0)) #fill the background with all black 
            for pt in mypic[2]:
                subrender = ( self.irop.pg.locate_pt_along( pt[0][0], pt[0][1], pt[1][0], pt[1][1], 1 ) )
                self.irop.fb.draw_points_batch( subrender ,  (55,55,222)   , 7  ) 
                self.irop.fb.draw_points_batch( subrender ,  (200,200,255) , 4  ) 
            ##########
            for pt in mypic[2]:
                subrender = ( self.irop.pg.locate_pt_along( pt[0][0], pt[0][1], pt[1][0], pt[1][1], 8 ) )
                self.irop.fb.draw_points_batch( subrender ,  (255,0,255) , 2  ) 

            #render more 3d on top of the framebuffer we pass in
            #self.irop.render( (255,0,0), 40, 40, 0, 2, 21, mypic[0], None)

            dorot+=5
            ##########            
            #you can use raw PIL commands if you dont care to get fancy.
            #this is a guassian blur , google "PIL" for others
           
            #self.irop.post_process('blur')

            self.irop.save_image('anim/out_%s_.png'%framect );framect+=1


#######################################################################################


