import cv2
import numpy as np
import time;  # This is required to include time module.


from matplotlib import pyplot as plt
from class_obstacles import Obstacles
from class_obstacles import filterMount

#Attributes
search_area_widht = 100 # deactivated
search_area_h = 70 # set by hight of canyon

#template = cv2.imread('test.png',cv2.IMREAD_UNCHANGED) #'test.png', 0) #'messi_face.jpg',0)
#template_enemie = cv2.imread('enemie.png',cv2.IMREAD_UNCHANGED)

#load templates
box = cv2.imread('box_obstacles.png',cv2.IMREAD_UNCHANGED) #'test.png', 0) #'messi_face.jpg',0)
rock = cv2.imread('rock_obstacle.png',cv2.IMREAD_UNCHANGED) #'test.png', 0) #'messi_face.jpg',0)
mount = cv2.imread('mount_obstacle.png',cv2.IMREAD_UNCHANGED) #'test.png', 0) #'messi_face.jpg',0)
tube = cv2.imread('tube_obstacle.png',cv2.IMREAD_UNCHANGED)
gap = cv2.imread('gap.png',cv2.IMREAD_UNCHANGED)


# transform screenshot into grey color
box_g = cv2.cvtColor(box, cv2.COLOR_RGB2GRAY)
rock_g = cv2.cvtColor(rock, cv2.COLOR_RGB2GRAY)
mount_g = cv2.cvtColor(mount, cv2.COLOR_RGB2GRAY)
tube_g = cv2.cvtColor(tube, cv2.COLOR_RGB2GRAY)
gap_g = cv2.cvtColor(gap, cv2.COLOR_RGB2GRAY)


# find shape of obstacles
d, w_box, h_box = box.shape[::-1]
d, w_rock, h_rock = rock.shape[::-1]
d, w_mount, h_mount = mount.shape[::-1]
d, w_tube, h_tube = tube.shape[::-1]
d, w_gap, h_gap = gap.shape[::-1]


def transform_points(widht, x):
    return x[0] + widht


def compare(screenshot):


	# transform screenshot into grey color
	out = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)

	#img_rgb = cv2.imread('mario-24.png',cv2.IMREAD_UNCHANGED)
	#out = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

	# size of given screenshot
	w_screen, h_screen = out.shape[::-1]

	# shrink search area
	search_area_w = 0# (w_screen- search_area_widht)
	search_area_h =  (h_screen- h_gap)

	img = out[0:(search_area_h) , search_area_w:w_screen]
	img_gap = out[(search_area_h):h_screen , search_area_w:w_screen]

	if(w_screen < w_gap):
		print 'too small, sorry'
		return



	#cvtColor(InputArray src, OutputArray dst, int code, int dstCn=0 )
	#cv2.cvtColor(img, img, cv2.COLOR_RGB2GRAY )

	#height, width, depth = img.shape
	#print height, width, depth;
	#height2, width2, depth = template.shape
	#print height2, width2, depth;

	#print img.dtypei_frame
	#print template.dtype






	# All the 6 methods for comparison in a list
	methods = ['CV_TM_CCOEFF']#, 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
	#ticks = time.time()
	#localtime = time.localtime(time.time())
	#print "start" , localtime

	#img = img2.copy()
	method = eval('cv2.TM_CCOEFF_NORMED')
	#method_e = eval('cv2.TM_SQDIFF')






	# Apply template Matching _ mario
	#res_box = cv2.matchTemplate(img,box_g,method)
	#res_rock = cv2.matchTemplate(img,rock_g,method)
	#res_mount = cv2.matchTemplate(img,mount_g,method)
	res_tube = cv2.matchTemplate(img,tube_g,method)
	res_gap = cv2.matchTemplate(img_gap,gap_g,method)


	# Apply template Matching _ enemie
	#res = cv2.matchTemplate(img,template_enemie,method)
	#min_val_e, max_val_e, min_loc_e, max_loc_e = cv2.minMaxLoc(res)



	# If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
	#if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
	#	top_left = min_loc
	#else:
	#	top_left = max_loc
	#bottom_right = (top_left[0] + w, top_left[1] + h)

	threshold = 0.9

	threshold_gap = 0.6

	#BOX
	loc_box_r = []
	#loc_box = np.where( res_box >= threshold_canyon)
	#loc_box_r = map(lambda x:((x[0] + search_area_w, x[1]), (x[0] + #search_area_w + w_box, x[1] + h_box)), zip(*loc_box[::-1]))
	#for pt in loc_box_r:

   	#	cv2.rectangle(out, pt[0], pt[1], 0, 2)

	#Rock
	loc_rock_r = []
	#loc_rock = np.where( res_rock >= threshold)
	#loc_rock_r = map(lambda x:((x[0] + search_area_w, x[1]), (x[0] #+ search_area_w + w_rock, x[1] + h_rock)), #zip(*loc_rock[::-1]))
	#for pt in loc_rock_r:
   	#	cv2.rectangle(out, pt[0], pt[1],  255, 2)

	#Mount
	#loc_mount = np.where( res_mount >= threshold)
	#loc_mount_r = map(lambda x:((x[0] + search_area_w, x[1]), (x[0] #+ search_area_w + w_mount, x[1] + h_mount)), #zip(*loc_mount[::-1]))
	#loc_mount_r = filterMount(loc_mount_r)
	#for pt in loc_mount_r:
   #		cv2.rectangle(out, pt[0], pt[1],  255, 2)

	#Tube
	loc_tube_r = []
	loc_tube = np.where( res_tube >= threshold)
	loc_tube_r = map(lambda x:((x[0] + search_area_w, x[1]), (x[0] + search_area_w + w_tube, x[1] + h_tube)), zip(*loc_tube[::-1]))


	#for pt in zip(*loc_tube[::-1]):
   	#	cv2.rectangle(out, (search_area_w + pt[0], pt[1]), (search_area_w + pt[0] + w_tube, pt[1] + h_tube), 50, 2)

	#Canyon
	loc_gap_r = []
	loc_gap = np.where( res_gap >= threshold_gap)
	loc_gap_r = map(lambda x:((x[0] + search_area_w, x[1] + (search_area_h)), (x[0] + search_area_w + w_gap, x[1] + h_gap + (search_area_h))), zip(*loc_gap[::-1]))


	#merge lists

	list_hover_obstacle =  loc_box_r + loc_rock_r
	list_canyon_obstacle = loc_gap_r
	list_fixed_obstacle = loc_tube_r #+ loc_mount_r


	#return array
	all_obstacles = Obstacles(list_hover_obstacle, list_canyon_obstacle, list_fixed_obstacle);
       	#print list_canyon_obstacle
	#print "--------"
	#print list_fixed_obstacle
	#print "new round--------------------------------"
	#print (w_screen , h_screen)
	#cv2.waitKey()

	return all_obstacles
