import pygame
import random
import math

from pygame.locals import *

'''
NOTE: Game may be a little laggy due to blitting background every second cycle.
There is also a lot of optimization that could have been done, such as setting a library
for sounds rather than loading them each time. 

Just throwing it out there that I know about these problems.
'''

# the window is the actual window onto which the camera view is resized and blitted
window_wid = 800
window_hgt = 600

# the frame rate is the number of frames per second that will be displayed and although
# we could (and should) measure the amount of time elapsed, for the sake of simplicity
# we will make the (not unreasonable) assumption that this "delta time" is always 1/fps
frame_rate = 40
delta_time = 1 / frame_rate


# constants for designating the different games states
STATE_TITLE = 0
STATE_IDLE = 1
STATE_SETUP = 2
STATE_READY = 3




def detect_collision_line_circ(u, v):

	# unpack u; a line is an ordered pair of points and a point is an ordered pair of co-ordinates
	(u_sol, u_eol) = u
	(u_sol_x, u_sol_y) = u_sol
	(u_eol_x, u_eol_y) = u_eol

	# unpack v; a circle is a center point and a radius (and a point is still an ordered pair of co-ordinates)
	(v_ctr, v_rad) = v
	(v_ctr_x, v_ctr_y) = v_ctr

	# the equation for all points on the line segment u can be considered u = u_sol + t * (u_eol - u_sol), for t in [0, 1]
	# the center of the circle and the nearest point on the line segment (that which we are trying to find) define a line 
	# that is is perpendicular to the line segment u (i.e., the dot product will be 0); in other words, it suffices to take
	# the equation v_ctr - (u_sol + t * (u_eol - u_sol)) · (u_evol - u_sol) and solve for t
	
	t = ((v_ctr_x - u_sol_x) * (u_eol_x - u_sol_x) + (v_ctr_y - u_sol_y) * (u_eol_y - u_sol_y)) / ((u_eol_x - u_sol_x) ** 2 + (u_eol_y - u_sol_y) ** 2)

	# this t can be used to find the nearest point w on the infinite line between u_sol and u_sol, but the line is not 
	# infinite so it is necessary to restrict t to a value in [0, 1]
	t = max(min(t, 1), 0)
	
	# so the nearest point on the line segment, w, is defined as
	w_x = u_sol_x + t * (u_eol_x - u_sol_x)
	w_y = u_sol_y + t * (u_eol_y - u_sol_y)
	
	# Euclidean distance squared between w and v_ctr
	d_sqr = (w_x - v_ctr_x) ** 2 + (w_y - v_ctr_y) ** 2
	
	# if the Eucliean distance squared is less than the radius squared
	if (d_sqr <= v_rad ** 2):
	
		# the line collides
		return True  # the point of collision is (int(w_x), int(w_y))
		
	else:
	
		# the line does not collide
		return False

	# visit http://ericleong.me/research/circle-line/ for a good supplementary resource on collision detection


	
def game_loop_inputs():

	# look in the event queue for the quit event
	quit_ocrd = False
	jump = False
	for evnt in pygame.event.get():
		if evnt.type == QUIT:
			quit_ocrd = True
		
		if evnt.type == pygame.KEYDOWN:		#Check if space is pressed
			if evnt.key == pygame.K_SPACE: 	#Handled this way so player can not hold down space
				jump = True
			
	keypress = pygame.key.get_pressed()
				

	return quit_ocrd, keypress, jump
	
def handle_menu(keypress):
	if(keypress[pygame.K_RETURN]):
		return STATE_SETUP
	return STATE_IDLE
	

	
def game_loop_update(rotating_line, circle_hitbox, power_up):

	#move the circle down, based on velocity and acceleration
	circle_hitbox['pos'][0] += circle_hitbox["velocity"][0]
	circle_hitbox['pos'][1] += circle_hitbox["velocity"][1]
	circle_hitbox['velocity'][0] += circle_hitbox['acceleration'][0]
	circle_hitbox['velocity'][1] += circle_hitbox['acceleration'][1]
	
	#if player goes beyond bounds, set collision to true (collision ends game)
	if circle_hitbox['pos'][1] > 600 or circle_hitbox['pos'][1] < -40: #provide some maneuverability for going too high
		circle_hitbox['col'] = True
		return rotating_line, circle_hitbox, power_up
	if circle_hitbox['pos'][0] > 800 or circle_hitbox['pos'][0] < 0: 
		circle_hitbox['col'] = True
		return rotating_line, circle_hitbox, power_up
	
	#set powerup location and type
	if power_up["initiate"]:
		power_up["pos"] = [random.randint(30, 650), random.randint(20, 400)]
		power_up["type"] = random.randint(1, 3)
		if power_up["type"] == 1:
			power_up["colour"] = (255, 0, 0)
		elif power_up["type"] == 2:
			power_up["colour"] = (0, 255, 0)
		else:
			power_up["colour"] = (0, 0, 255)
		power_up["initiate"] = False
		
	#check for collision with powerup
	tempX = ((circle_hitbox["pos"][0] + circle_hitbox["rad"]/2)  - (power_up["pos"][0] + power_up["rad"]))
	tempY = ((circle_hitbox["pos"][1] + circle_hitbox["rad"]/2)  - (power_up["pos"][1] + power_up["rad"]))
	if (tempX**2 + tempY**2) <= ((circle_hitbox["rad"] + power_up["rad"])**2):
		power_up["col"] = True
		power_up["pos"] = [900, 900]	#blit offscreen
		power_up["start_time"] = 5 	#set time powerup is active
		power_up["active"] = False
	
	if power_up["col"] and power_up["start_time"] > 0:
		power_up["start_time"] -= delta_time
		
	
		
	
	
	# increase the angle of the rotating line
	rotating_line["ang"] = (rotating_line["ang"] + 1)

	# the rotating line angle ranges between 90 and 180 degrees
	if rotating_line["ang"] > 180:

		# when it reaches an angle of 180 degrees, reposition the circular hitbox
		#circle_hitbox["pos"] = [random.randint(0, window_wid), random.randint(0, window_hgt)]    #REMOVED RANDOM CIRCLE PLACEMENT
		rotating_line["ang"] = 90
		tempRandVal = random.randint(10,85)/100
		rotating_line["len"] = [(0, tempRandVal), (tempRandVal+0.20, 1.25)]
		rotating_line["counter"] += 1
		
	# the points associated with each line segment must be recalculated as the angle changes
	rotating_line["seg"] = []
	
	# consider every line segment length
	for len in rotating_line["len"]:
	
		# compute the start of the line...
		sol_x = rotating_line["ori"][0] + math.cos(math.radians(rotating_line["ang"])) * window_wid * len[0]
		sol_y = rotating_line["ori"][1] + math.sin(math.radians(rotating_line["ang"])) * window_wid * len[0]
		
		# ...and the end of the line...
		eol_x = rotating_line["ori"][0] + math.cos(math.radians(rotating_line["ang"])) * window_wid * len[1]
		eol_y = rotating_line["ori"][1] + math.sin(math.radians(rotating_line["ang"])) * window_wid * len[1]
		
		# ...and then add that line to the list
		rotating_line["seg"].append( ((sol_x, sol_y), (eol_x, eol_y)) )

	# start by assuming that no collisions have occurred
	circle_hitbox["col"] = False
	
	# consider possible collisions between the circle hitbox and each line segment
	for seg in rotating_line["seg"]:
	
		# if there is any collision at all, the circle hitbox flag is set
		if detect_collision_line_circ(seg, (circle_hitbox["pos"], circle_hitbox["rad"])):
			circle_hitbox["col"] = True
			break

	# return the new state of the rotating line and the circle hitbox
	return rotating_line, circle_hitbox, power_up

	
def game_loop_render(rotating_line, circle_hitbox, power_up, window_sfc, game_state):
	pygame.display.flip()
	
	
	# load coin image
	coin = pygame.image.load("coin.png").convert()
	coin = pygame.transform.scale(coin, (60, 60))
	coin.set_colorkey((0, 0, 0))
	
	# setup text for counter
	font = pygame.font.Font(None, 24)
	
	#set score variable for endgame
	if rotating_line["counter"] != -1:
		rotating_line["past_score"] = rotating_line["counter"]
	
	if game_state == STATE_TITLE:
		title_screen = pygame.image.load("title.png").convert_alpha()
		window_sfc.blit(title_screen, (0, 0))
		
	# setup counter text for game over
		if not rotating_line["first_play"]:
			if rotating_line["past_score"] == 1: #single coin
				text = font.render("You deposited " + str(rotating_line["past_score"]) + " coin.", True, (215, 54, 244))
			else:								#plural coins
				text = font.render("You deposited " + str(rotating_line["past_score"]) + " coins.", True, (215, 54, 244))
			window_sfc.blit(text, (300, 550))
			
		
	if game_state == STATE_READY:
		game_screen = pygame.image.load("game.png").convert_alpha()
		window_sfc.blit(game_screen, (0, 0))
	
		#game_screen = pygame.image.load("game.png").convert_alpha()
			
		if not circle_hitbox["col"]:
			text = font.render("Coins deposited: " + str(rotating_line["counter"]), True, (215, 54, 244))
			window_sfc.blit(text, (350, 550))
	# draw each of the rotating line segments
		for seg in rotating_line["seg"]:
		
			pygame.draw.aaline(window_sfc, (0, 0, 0), seg[0], seg[1])
	
	
		#display the powerup
		if power_up["active"]:
			pygame.draw.circle(window_sfc, power_up["colour"], power_up["pos"], power_up["rad"])
			
		
		if power_up["col"] and power_up["start_time"] > 4.95:
			#redraw off screen then stop drawing
			pygame.draw.circle(window_sfc, power_up["colour"], power_up["pos"], power_up["rad"])
			#play pickup sound
			pickupfx = pygame.mixer.Sound("pickup.wav")
			pickupfx.set_volume(0.1)
			pickupfx.play()
			
		#activate powerup
		if power_up["col"] and power_up["start_time"] > 0:
			if power_up["type"] == 1:		#shrink
				coin = pygame.transform.scale(coin, (30, 30))
				circle_hitbox["rad"] = 15
			elif power_up["type"] == 2:  	#speed up
				circle_hitbox["speed"] = 6
			else:							#big jump
				circle_hitbox["jump_height"] = -13
		elif power_up["col"]:		#powerup runs out
			#play sound when pickup ends
			expirefx = pygame.mixer.Sound("expire.wav")
			expirefx.set_volume(0.1)
			expirefx.play()
			
			if power_up["type"] == 1:
				circle_hitbox["rad"] = 30
			elif power_up["type"] == 2:
				circle_hitbox["speed"] = 4
			elif power_up["type"] == 3:
				circle_hitbox["jump_height"] = -10
			power_up["col"] = False
			power_up["timer"] = random.randint(3, 7)
			
			
		# End the game if there has been a collision
		if circle_hitbox["col"]:
			endfx = pygame.mixer.Sound("end.wav")
			endfx.set_volume(0.1)
			endfx.play()
		
			#reset circle values
			
			
			window_sfc.blit(coin, (900, 900)) #blit offscreen
			#position = coin.get_rect()
			#window_sfc.blit(game_screen, position, position)
			#window_sfc.blit(game_screen, circle_hitbox["pos"], (circle_hitbox["pos"][0], circle_hitbox["pos"][1], 60, 60))
		
			circle_hitbox["pos"] = [window_wid // 2, window_hgt // 2]
			circle_hitbox["velocity"] = [0, 0]
			circle_hitbox["acceleration"] = [0, 1]
			circle_hitbox["rad"] = 30
			circle_hitbox["speed"] = 4
			circle_hitbox["jump_height"] = -10
			
			#reset line values
			for seg in rotating_line["seg"]:
				pygame.draw.aaline(window_sfc, (0, 0, 0), (900,900), (901, 901)) #draw off screen
			rotating_line["ori"] = (window_wid, 0)               
			rotating_line["ang"] = 135                            
			rotating_line["len"] = [ (0.00, 0.55), (0.75, 1.25)]    
			rotating_line["seg"] = [] 
			rotating_line["counter"] = -1
			rotating_line["first_play"] = False
			
			#reset powerup values
			power_up["active"] = False
			power_up["initiate"] = False
			power_up["col"] = False
			power_up["start_time"] = 0
			power_up["timer"] = random.randint(3,7)
			
		else:
			
			if circle_hitbox["right"] == True:
				coin = pygame.transform.rotate(coin, 0)
			elif circle_hitbox["left"] == True:
				coin = pygame.transform.rotate(coin, 180)
				coin = pygame.transform.flip(coin, False, True)
			elif circle_hitbox["velocity"][1] > 0:
				coin = pygame.transform.rotate(coin, 270)
			else:
				coin = pygame.transform.rotate(coin, 90)
		
			#pygame.draw.circle(window_sfc, (255, 255, 255), circle_hitbox["pos"], circle_hitbox["rad"])
			window_sfc.blit(coin, (circle_hitbox['pos'][0] - circle_hitbox['rad'], circle_hitbox['pos'][1] - circle_hitbox['rad']))
			
			
			
			#window_sfc.blit(game_screen, circle_hitbox["pos"], (circle_hitbox["pos"][0], circle_hitbox["pos"][1], 60, 60)
		
	# update the display, skip every second frame for slightly improved framerate
	#NOTE: I know that drawing the background over every time is not the best way,
	#but I had a lot of trouble trying to get the other methods working
	if not rotating_line["skip_frame"]:
		pygame.display.update()
		rotating_line["skip_frame"] = True
	else:
		rotating_line["skip_frame"] = False

def main():
	
	# initialize pygame
	pygame.init()

	# initialize font
	pygame.font.init()
	
	# initialize mixer
	pygame.mixer.init()
	
	#setup jump sound
	jumpfx = pygame.mixer.Sound("jump.wav")
	jumpfx.set_volume(.1)
	
	#setup music
	pygame.mixer.music.load("music.mp3")
	pygame.mixer.music.set_volume(0.06)
	
	# create the window and set the caption of the window
	window_sfc = pygame.display.set_mode( (window_wid, window_hgt) )
	pygame.display.set_caption('"Toy" for the MDA Exercise')
	title_screen = pygame.image.load("title.png").convert_alpha()
	window_sfc.blit(title_screen, (0, 0))
	
	# create a clock
	clock = pygame.time.Clock()
	
	
	
	# this is the initial game state
	game_state = STATE_TITLE


	#####################################################################################################
	# these are the initial game objects that are required (in some form) for the core mechanic provided
	#####################################################################################################

	# this game object is a line segment, with a single gap, rotating around a point
	rotating_line = {}
	rotating_line["ori"] = (window_wid, 0)                 # the "origin" around which the line rotates 
	rotating_line["ang"] = 135                             # the current "angle" of the line
	rotating_line["len"] = [ (0.00, 0.55), (0.75, 1.25)]    # the "length" intervals that specify the gap(s)
	rotating_line["seg"] = []                              # the individual "segments" (i.e., non-gaps)
	rotating_line["counter"] = -1
	rotating_line["past_score"] = 0
	rotating_line["first_play"] = True
	rotating_line["skip_frame"] = False
	
	# this game object is a circulr
	circle_hitbox = {}
	circle_hitbox["pos"] = [window_wid // 2, window_hgt // 2]
	circle_hitbox["rad"] = 30
	circle_hitbox["col"] = False
	circle_hitbox["velocity"] = [0, 0]
	circle_hitbox["acceleration"] = [0, 1]
	circle_hitbox["left"] = False
	circle_hitbox["right"] = False
	circle_hitbox["speed"] = 4
	circle_hitbox["jump_height"] = -10
	
	power_up = {}
	power_up["active"] = False
	power_up["initiate"] = False
	power_up["rad"] = 10
	power_up["col"] = False
	power_up["pos"] = [0, 0]
	power_up["type"] = 0
	power_up["start_time"] = 0
	power_up["timer"] = random.randint(3,7)
	power_up["colour"] = (0, 0, 0)
	
	
	# the game loop is a postcondition loop controlled using a Boolean flag
	closed_flag = False
	while not closed_flag:

			
		#####################################################################################################
		# this is the "inputs" phase of the game loop, where player input is retrieved and stored
		#####################################################################################################

		closed_flag, keypress, jump = game_loop_inputs()
		
	
		#setup ignore timer
		#if ignore_tmr > 0:
		#	ignore_tmr = max(ignore_tmr - delta_time, 0)
		#	keypress = tuple([0] * 323)
			
		
		
		
		#####################################################################################################
		# this is the "update" phase of the game loop, where the changes to the game world are handled
		#####################################################################################################
		if game_state == STATE_TITLE:
			next_state = STATE_IDLE
		elif game_state == STATE_IDLE:
			next_state = handle_menu(keypress)
			
		elif game_state == STATE_SETUP:
			#start music
			pygame.mixer.music.play(-1)
			
			power_up["start_time"] = clock
			next_state = STATE_READY
			
		elif game_state == STATE_READY:
			if power_up["timer"] > 0:  
				power_up["timer"] -= delta_time
			elif power_up["timer"] == -1:
				pass
			else:
				power_up["active"] = True
				power_up["initiate"] = True
				power_up["timer"] = -1

			
			rotating_line, circle_hitbox, power_up = game_loop_update(rotating_line, circle_hitbox, power_up) 
			
			circle_hitbox["left"] = False
			circle_hitbox["right"] = False
			
			#Handle left and right movement
			if keypress[pygame.K_a] or keypress[pygame.K_LEFT]:
				circle_hitbox['pos'][0] -= circle_hitbox["speed"]
				circle_hitbox["left"] = True
			if keypress[pygame.K_d] or keypress[pygame.K_RIGHT]:
				circle_hitbox['pos'][0] += circle_hitbox["speed"]
				circle_hitbox["right"] = True
				
			#handle jump
			if jump:
				circle_hitbox['velocity'][1] = circle_hitbox["jump_height"]
				jumpfx.play()
			
		
				
				
			
		
		#####################################################################################################
		# this is the "render" phase of the game loop, where a representation of the game world is displayed
		#####################################################################################################

		
		game_loop_render(rotating_line, circle_hitbox, power_up, window_sfc, game_state)
		
			# enforce the minimum frame rate
		clock.tick(frame_rate)
			
		if circle_hitbox['col'] == True:
			#stop music
			pygame.mixer.music.stop()
			
			game_loop_render(rotating_line, circle_hitbox, power_up, window_sfc, game_state) #render again to reset screen
			next_state = STATE_TITLE
			circle_hitbox['col'] = False
		game_state = next_state
		
		
if __name__ == "__main__":
	main()
