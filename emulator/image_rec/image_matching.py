import cv2
import numpy as np
import time;  # This is required to include time module.


from matplotlib import pyplot as plt
from class_obstacles import Obstacles


#Attributes
search_area_widht = 100
search_area_h = 70
amount_of_skiped_frames = 5



#template = cv2.imread('test.png',cv2.IMREAD_UNCHANGED) #'test.png', 0) #'messi_face.jpg',0)
#template_enemie = cv2.imread('enemie.png',cv2.IMREAD_UNCHANGED) 

#load templates
box = cv2.imread('box_obstacles.png',cv2.IMREAD_UNCHANGED) #'test.png', 0) #'messi_face.jpg',0)
rock = cv2.imread('rock_obstacle.png',cv2.IMREAD_UNCHANGED) #'test.png', 0) #'messi_face.jpg',0)
tube = cv2.imread('tube_obstacle.png',cv2.IMREAD_UNCHANGED)	
canyon = cv2.imread('canyon_obstacle.png',cv2.IMREAD_UNCHANGED)
canyon_long = cv2.imread('canyon_obstacle_long.png',cv2.IMREAD_UNCHANGED) 

# transform screenshot into grey color
box_g = cv2.cvtColor(box, cv2.COLOR_RGB2GRAY)
rock_g = cv2.cvtColor(rock, cv2.COLOR_RGB2GRAY)
tube_g = cv2.cvtColor(tube, cv2.COLOR_RGB2GRAY)
canyon_g = cv2.cvtColor(canyon, cv2.COLOR_RGB2GRAY)
canyon_long_g = cv2.cvtColor(canyon_long, cv2.COLOR_RGB2GRAY)
	


	 

#find shape of obstacles
d, w_box, h_box = box.shape[::-1]
d, w_rock, h_rock = rock.shape[::-1]
d, w_tube, h_tube = tube.shape[::-1]
d, w_canyon, h_canyon = canyon.shape[::-1]
d, w_canyon_long, h_canyon_long = canyon_long.shape[::-1]

#global counter
i_frame = 0


def transform_points(widht, x):
	return x[0] + widht;

	

def compare(screenshot, x_speed):

	print(x_speed)

	global i_frame
	# skip frames
	if(i_frame == 0):
		i_frame = amount_of_skiped_frames
	else:
		i_frame = i_frame-1 
		return	

	# transform screenshot into grey color
	out = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)

	#img_rgb = cv2.imread('mario-22.png',cv2.IMREAD_UNCHANGED)
	#out = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

	# size of given screenshot
	w_screen, h_screen = out.shape[::-1]

	# shrink search area
	search_area_w =  (w_screen- search_area_widht)
	img = out[0:h_screen , search_area_w:w_screen]
	img_canyon = out[(h_screen-search_area_h):h_screen , search_area_w:w_screen]
	
	if(w_screen < w_canyon_long):
		print 'too small, sorry'		
		return 
	
		

	#cvtColor(InputArray src, OutputArray dst, int code, int dstCn=0 )
	#cv2.cvtColor(img, img, cv2.COLOR_RGB2GRAY )	

	#height, width, depth = img.shape
	#print height, width, depth;
	#height2, width2, depth = template.shape
	#print height2, width2, depth;

	#print img.dtype
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
	res_box = cv2.matchTemplate(img,box_g,method)
	res_rock = cv2.matchTemplate(img,rock_g,method)
	res_tube = cv2.matchTemplate(img,tube_g,method)
	res_canyon = cv2.matchTemplate(img_canyon,canyon_g,method)
	res_canyon_long = cv2.matchTemplate(img_canyon,canyon_long_g,method)	

	# Apply template Matching _ enemie
	#res = cv2.matchTemplate(img,template_enemie,method)
	#min_val_e, max_val_e, min_loc_e, max_loc_e = cv2.minMaxLoc(res)



	# If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
	#if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
	#	top_left = min_loc
	#else:
	#	top_left = max_loc
	#bottom_right = (top_left[0] + w, top_left[1] + h)

	threshold = 0.8

	#BOX
	loc_box = np.where( res_box >= threshold)
	loc_box_r = map(lambda x:((x[0] + search_area_w, x[1]), (x[0] + search_area_w + w_box, x[1] + h_box)), zip(*loc_box[::-1]))
	for pt in loc_box_r:
		
   		cv2.rectangle(out, pt[0], pt[1], 0, 2)

	#Rock
	loc_rock = np.where( res_rock >= threshold)
	loc_rock_r = map(lambda x:((x[0] + search_area_w, x[1]), (x[0] + search_area_w + w_rock, x[1] + h_rock)), zip(*loc_rock[::-1]))
	for pt in loc_rock_r:
   		cv2.rectangle(out, pt[0], pt[1],  255, 2)

	#Tube
	loc_tube = np.where( res_tube >= threshold)
	loc_tube_r = map(lambda x:((x[0] + search_area_w, x[1]), (x[0] + search_area_w + w_tube, x[1] + h_tube)), zip(*loc_tube[::-1]))


	for pt in loc_tube_r:
		cv2.rectangle(out, pt[0], pt[1], 50, 2)
	#for pt in zip(*loc_tube[::-1]):
   	#	cv2.rectangle(out, (search_area_w + pt[0], pt[1]), (search_area_w + pt[0] + w_tube, pt[1] + h_tube), 50, 2)
	
	#Canyon
	loc_canyon = np.where( res_canyon >= threshold)
	loc_canyon_r = map(lambda x:((x[0] + search_area_w, x[1] + (h_screen-search_area_h)), (x[0] + search_area_w + w_canyon, x[1] + h_canyon + (h_screen-search_area_h))), zip(*loc_canyon[::-1]))
	for pt in loc_canyon_r:
   		cv2.rectangle(out, pt[0], pt[1], 150, 2)

	#Canyon_long
	loc_canyon_long = np.where( res_canyon_long >= threshold)
	loc_canyon_long_r = map(lambda x:((x[0] + search_area_w, x[1] + (h_screen-search_area_h)), (x[0] + search_area_w + w_canyon_long, x[1] + h_canyon_long + (h_screen-search_area_h))), zip(*loc_canyon_long[::-1]))
	for pt in loc_canyon_long_r:
   		cv2.rectangle(out, pt[0], pt[1], 150, 2)

	#cv2.rectangle(out,top_left, bottom_right, 255, 2)

	# If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
	#if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
	#	top_left = min_loc_e
	#else:
	#	top_left = max_loc_e
	#bottom_right = (top_left[0] + w, top_left[1] + h)
	#cv2.rectangle(out,top_left, bottom_right, 0, 2)


	cv2.imshow('found',out);
	
	

        plt.show()

	#return array
	all_obstacles = Obstacles(loc_box_r, loc_rock_r, loc_canyon_r, loc_tube_r);
       
	return all_obstacles


