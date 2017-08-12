

from pycv.raster_ops import *
from pycv.point_ops import *
from pycv.vec3d import *
from pycv.kdag import *

import render



#UNFINSIHED - WORKING ON A SCENE GRAPH FOR MORE FUN 

"""
def new_3d_node(nodename, objfile, pos=(0,0,0), rot=(0,0,0), scale=(1,1,1) ):
	n1 = PointGen3D() #node_base() # PointGen3D()
	n1.name = nodename
	n1.load_obj(objfile)
	n1.set_position(  pos ) 
	n1.addattr('file', objfile)
	return n1

n1 = new_3d_node('sfear' , 'models/sphere.obj')
n2 = new_3d_node('kone'  , 'models/cone.obj', (5,5,5) )
n3 = new_3d_node('torus' , 'models/icosphere.obj')

n2.show_poly(2)

##########3
dg = data_graph()

dg.add(n1)
dg.add(n2)
dg.add(n3)

dg.parent(n2,n1)
dg.parent(n3,n2)

dg.save_graph_file('test.kldag')
 
"""



######################################################################
#MMRT - Magic Mirror Render Toy
######################################################################


"""
#RENDER SCANLINE ANIMATION (ONLY TRIANGLES) 
import shutil
import math
path = 'anim'
if os.path.exists(path):
    print('deleting directory %s'%path)
    shutil.rmtree(path)
print('creating directory %s'%path)    
os.makedirs(path)
############
fb = PixelOp()   
fb.create_buffer(600,600)
fb.graticule(45)
rop = render.renderImage_OP(0,0, fb)
rop.scanline('anim', 150,'models/sphere.obj', 40) #20 = numframes
"""


"""
#DRAW A VECTOR AND TELL US THE ANGLE OF IT IN DEGREES
fb = PixelOp()   
fb.create_buffer(300, 300)
fb.draw_vector_2d( (-2,-4), (0,0)  )
fb.save_file('vec.png')
"""



"""
#LOAD OBJ FILE AND RENDER IT, ALSO DEMO "POST RENDER EFFECTS" 
anim = render.animate()
anim.image_render('models/torus.obj', 3) #number of frames = 3 
"""


############################

"""
 #YOU CAN USE renderImage_OP AS A RENDERER DIRECTLY  (WHICH IS WHAT ANIMATION CLASS CALLS)
 #HERE IS HOW TO CALL IT DIRECTLY 
 #ALL YOU NEED TO DO TO ANIMATE IS PUT IT IN A LOOP !!
 #THE FUNCTION ARGUMENTS ARE EQUIVILANT TO ANIMATBLE PROPERTIES IN BLENDER OR MAYA 
rop = render.renderImage_OP(640, 480)
obj = PointGen3D()
obj.load_obj('models/icosphere.obj')
rop.render( (0,255,0) , 0,0,180, 1, 200, None, obj)
rop.save_image('test.png')
"""

############################

"""
#THIS WILL RENDER A VECTOR IMAGE AND CREATE AN OBJ FILE CONTAINING 2D IMAGE IN VECTOR FORMAT
rop = render.renderImage_OP(640, 480)
rop.vector_render(0, 0, 0, .05, 'models/monkey.obj', 'renderpaths.obj')
"""


############################
"""
#YOU CAN RENDER ON TOP OF ANOTHER FRAMEBUFFER FOR SOME BASIC COMPOSITING EFFECTS
#DONT FORGET, A FRAMEBUFFER IS REALLY A PIL IMAGE OBJECT SO YOU ALSO DO ANYTHING THAT PIL DOES 
fb = PixelOp()   
fb.load_file("maxcat.jpg")
rop = render.renderImage_OP(1200, 940)
obj = PointGen3D()
obj.load_obj('models/monkey.obj')
rop.render( (0,255,0) , 0,0,180, 3, 400, fb, obj)#<--- RENDER ACCEPTS FRAMEBUFFERS TO BE PASSED IN !
rop.save_image("maxheadroom.png")
"""

############################

"""
#CREATE A POLYGON FROM SCRATCH
#GET OUT GRAPH PAPER AND PLOT SOME POINTS TO TEST THIS
x = PointGen3D() #pointgen is both a MODEL and PROCEDURAL 3D TOOLS
x.points = [(-2,0,0), (0,3,0), (2,0,0) ]   #define 3 points in 3D (basically 2D with 0 for Z axis)
x.polygons = [ (1,2,3) ]                   #connect vertecies #1 to #2 to #3
x.show()                                  #<--- This prints stats about your object 
x.save_obj('myprecious.obj') 
"""


############################
"""
##PointGen3D HAS MANY COOL TRICKS INCLUDING BUILT IN PRIMATIVES LIKE CIRCLE, CUBE, AND MORE 
x = PointGen3D() #pointgen is both a MODEL and PROCEDURAL 3D TOOLS
x.prim_cube((5,5,5), 1)
x.save_obj('kube.obj') 
"""

############################

"""
#YOU CAN STACK MULITPLE PRIMATIVES INTO THE SAME MODEL
#THINK OF A PointGen3D OBJECT AS A STACK OF OPERATIONS AS WELL AS SIMPLY STATIC GEOMETRY
x = PointGen3D()
x.prim_triangle()
x.rotate_pts(45,0,0)
x.prim_circle()
x.rotate_pts(45,0,0)
#self, pos=(0,0,0), rot=(0,0,0), size=1, spokes = 5):
x.prim_circle((0,0,0), (45,0,0), 2, 15)
x.rotate_pts(45,0,0)
#x.show()                             #<--- This prints stats about your object
x.save_obj('multi_primitves.obj')
"""

############################
"""
#BUILD A PROCEDURAL OBJECT AND ANIMATE IT !!! THE FUN NEVER ENDS 
obj = PointGen3D() #pointgen is both a MODEL and PROCEDURAL 3D TOOLS
for x in range(36):
    obj.prim_cube((0,.5,0), .05)
    obj.rotate_pts(0,0,x*10)
obj.save_obj('multi_kubez.obj') 
#now we built a model - render it 
anim = render.animate()
anim.image_render('multi_kubez.obj', 36) #number of frames = 30 
"""

############################

"""
#THIS IS A TEST OF A FUNCTION THAT GIVEN TWO POINTS, WILL FILL A LINE BETWEEN THEM WITH MORE POINTS
#THIS IS THE FUNCTION I USE IN THE POST RENDER DEMO TO PUT A DOT IN THE MIDDLE OF EACH POLYGON EDGE 
#THERE IS A 2D AND 3D VERSION OF THIS FUNCTION 
obj = PointGen3D() 
obj.points = obj.locate_pt_along3d(0,0,0 ,1.5,1.5,1.5,  10)
rop = render.renderImage_OP(640, 480)
rop.render( (0,255,0) , 0,45,180, 3, 200, None, obj)
rop.save_image('test.png')
"""




######################################################################
######################################################################
######################################################################
######################################################################


#here is how you load and convert an image
"""
fb = RasterObj()
fb.load_file("maxcat.jpg")
fb.save_file("foo.png")
"""

######################################################################

"""
#Pixel op inherits raster op ... example
fb = PixelOp()   #<---this is the NOT raster but it works
#fb.load_file("maxcat.jpg") #<- LOAD AUTOMATICALLY BUILDS FB BUFFER OBJECT
fb.create_buffer(100, 100)  #<- IF YOU DONT LOAD CREATE A BUFFER
fb.fill_color( (255,0,0) )
fb.save_file("foo.png")
"""

######################################################################
"""
#Pixel op inherits raster op ... example
xres = 150
yres = 150
fb = PixelOp()   #<---this is the NOT raster but it works
fb.load_file("maxcat.jpg") #<- LOAD AUTOMATICALLY BUILDS FB BUFFER OBJECT
#fb.create_buffer(xres, yres)  #<- IF YOU DONT LOAD CREATE A BUFFER
#fb.fill_color( (255,0,0) ) #RGB IS A TUPLE IN PARENS
fb.draw_fill_circle( int(xres/2), int(yres/2), int(yres/10), (255, 255, 0) )
fb.save_file("foo.png")
"""
######################################################################
"""
#THIS SHOWS HOW TO USE POINT GENERATTOR AND RASTER TOGETHER
xres = 150
yres = 150
pg = PointGen2D()   #POINT GENERATOR (LIST OF TUPLES)
fb = PixelOp()   #FRAMEBUFFER OBJECT
fb.create_buffer(xres, yres)  #<- IF YOU DONT LOAD AN IMAGE, CREATE A BUFFER
#def calc_circle(self, x_orig, y_orig, dia, periodic=True, spokes=23, doRound=False):
my_circle_geom =  pg.calc_circle(xres/2, yres/2, 50, True, 5, False ) 
fb.connect_the_dots( my_circle_geom, (255, 0, 255) , 1 ) 
fb.save_file("circle.png")
"""

######################################################################
"""
#DRAW A BUNCH OF LINES WITH BRESENHAM ALGORITHM
#CHANGE THE COLOR TO GET A WEIRD GRADIENT EFFECT
xres = 150
yres = 150
pg = PointGen2D()   #POINT GENERATOR (LIST OF TUPLES)
fb = PixelOp()   #FRAMEBUFFER OBJECT
fb.create_buffer(xres, yres)  #<- IF YOU DONT LOAD CREATE A BUFFER
for x in range(250):
    linegeom = pg.calc_line(x, 0, x+10, x)
    fb.connect_the_dots( linegeom, (x , 255-x, 0) , 1 )  #CONNECT THE DOTS DRAWS POINTS!!!!
    linegeom = pg.calc_line(-x, 0, x-10, x)
    fb.connect_the_dots( linegeom, (x , 255-x, 0) , 1 )  #CONNECT THE DOTS DRAWS POINTS!!!!
fb.save_file("bunchOlines.png")
"""




################################################################################
################################################################################

"""
#TEST OF TRIANGULATE 
obj = PointGen3D() 
##triangle
#  obj.points = [(-2,0,0), (0,3,0), (2,0,0) ]   #define 3 points in 3D (basically 2D with 0 for Z axis)
#  obj.polygons = [ (1,2,3) ]                   #connect vertecies #1 to #2 to #3
##quad
obj.points = [(-2,-2,0), (-2,2,0), (2,2,0), (2,-2,0) ]    
obj.polygons = [ (1, 2, 3, 4) ]  

#obj.triangulate()
obj.show()
#obj.show_poly(5)
"""


