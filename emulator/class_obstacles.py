def comparef(a,b):
  if(getLTPoint(a)[0] < getLTPoint(b)[0]):
    return -1
  elif(getLTPoint(a)[0] > getLTPoint(b)[0]):
    return +1
  else:
    if(getLTPoint(a)[1] < getLTPoint(b)[1]):
	return -1
    else:
	return +1

def reduce_fct(list, elem):
  if(not list):
	print "nil"
	return [elem]
  elif not(type(list) == type([])):
	list = [list] + []

  last_value = list[len(list)-1]



  leftPoint_l = getLTPoint(last_value)
  leftPoint_e = getLTPoint(elem)
  if (leftPoint_l[0] == leftPoint_e[0]):
	return list
  else:
	return list + [elem]



def filterMount(x):
  if( not x ):
	return []
  tmp = sorted(x, cmp=comparef)
  return reduce(lambda x,y: reduce_fct(x,y), tmp )




# all the arrays contain elements of this structure
#--------------------------------------------------
# Element:{
# Point1 - left top corner of the obstacle
# Point2 - right bottom corner of the obstacle
# }
#
# each Point contains x and y coordinates
#
class Obstacles(object):

  def __init__(self, array_hover, array_canyon, array_fixed):
     self.y0 = array_hover
     self.y1 = array_canyon
     self.y2 = array_fixed

	# mario can go under this kind of obstacle
  def getHover(self):
	return self.y0

	#mario can fall into this kind of obstacle
  def getCanyon(self):
	return self.y1

	#mario cant go under this kind of obstacle
  def getFixed(self):
	return self.y2

def getLTPoint( a):
  return a[0]

def getRBPoint( a):
  return a[1]
