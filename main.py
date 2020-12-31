# OBJ - Bird, Pillar, Ground
import neat
import pygame
import time
import os
import random
import pickle
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
STAT_FONT = pygame.font.SysFont("arial", 50)

class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION = 25
	ROT_VEL = 20
	ANIMATION_TIME = 5 #wings flap speed

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.height = self.y
		self.tilt = 0
		self.tick_count = 0
		self.vel = 0 
		self.img_count = 0
		self.img = self.IMGS[0]
	
	def jump(self):
		self.vel = -10.5
		self.tick_count = 0
		self.height = self.y
	
	def move(self):
		self.tick_count += 1
		#calculate Displacement to understand how many pixels did the bird move
		d = self.vel*self.tick_count + 1.5*self.tick_count**2
		#example = -10.5 * 1 + 1.5*1**2 =  -9 --> -7 --> -5 --> 0 --> 5 --> 7 --> 9

		if d >= 16:
			d = 16
		
		if d < 0:
			d -= 2 #for jumping nicely
		
		self.y += d
		
		if d < 0 or self.y < self.height + 50:
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else:
			if self.tilt > -90:
				self.tilt -= self.ROT_VEL

	def draw(self, win):
		self.img_count += 1

		if self.img_count < self.ANIMATION_TIME:
			self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2:
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4:
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME*4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0
		
		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2
		
		rotated_image = pygame.transform.rotate(self.img, self.tilt)
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
		win.blit(rotated_image, new_rect.topleft)

	def get_mask(self): #Mask figures out where all the pixels are
		#it creates a 2D list with as many rows as there are pixels going down and as many columns as there is pixels going across
		return pygame.mask.from_surface(self.img)

class Pipe:
	GAP = 200
	VEL = 7

	def __init__(self, x):
		self.x = x
		self.height = 0 

		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
		self.PIPE_BOTTOM = PIPE_IMG

		self.passed = False
		self.set_height()

	def set_height(self):
		self.height = random.randrange(50, 450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL

	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
	
	def collide(self, bird):
		bird_mask = bird.get_mask()
		top_mask  = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask  = pygame.mask.from_surface(self.PIPE_BOTTOM)
		
		#Offset - How far away are the masks are from each other, check the pixels against each other
		#Normally, it sees how far away are the two top left corner are from each other 
		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		#Next up is figuring out whether these masks collided
		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask, top_offset)
		#if there is no collision this point returns None
		if t_point or b_point:
			return True
		return False

class Base:
	VEL = 5
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG
	
	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		self.x1 -= self.VEL
		self.x2 -= self.VEL

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH
		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH
	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, obj):
	win.blit(BG_IMG, (0,0))
	for bird in obj[0]:
		bird.draw(win)
	for pipe in obj[1]:
		pipe.draw(win)
	obj[2].draw(win)
	text = STAT_FONT.render("Score: "+ str(obj[3]), 1, (255, 255, 255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
	pygame.display.update()

def main():
	bird = Bird(100,200)
	pipes = [Pipe(500)]
	base = Base(700)
	score = 0
	obj = [bird, pipes, base, score]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	play =  True
	clock = pygame.time.Clock()

	while play:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				play = False

		add_pipe = False
		#obj[0].move()
		for pipe in list(obj[1]):
			if pipe.collide(bird):
				pass
			if pipe.x + pipe.PIPE_TOP.get_width() < 10:
				obj[1].remove(pipe)

			if not pipe.passed and pipe.x < bird.x:
				pipe.passed = True
				add_pipe = True

			pipe.move()
		if add_pipe == True:
			obj[3] += 1
			obj[1].append(Pipe(500))

		if obj[0].y + obj[0].img.get_height() >= 700:
			#print (f"{obj[0].img.get_height() + obj[0].y}")
			pass

		obj[2].move()
		draw_window(win, obj)


	pygame.quit()
	quit()

def fit_func(genomes, config):
	nets = []
	ge = []
	birds = []
	#genomes is a tuple
	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		birds.append(Bird(230, 350))
		g.fitness = 0
		ge.append(g)

	pipes = [Pipe(500)]
	base = Base(700)
	score = 0
	obj = [birds, pipes, base, score]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	play =  True
	clock = pygame.time.Clock()

	while play:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				play = False
				pygame.quit()
				quit()


		#Check which pipe we are comparing to
		pipe_ind = 0
		if len(obj[0]):
			if len(obj[1]) > 1:
				if obj[0][0].x > ( obj[1][0].x + obj[1][0].PIPE_TOP.get_width()) :
					pipe_ind = 1
		else:
			run = False
			break

		for loc, bird in enumerate(obj[0]):
			bird.move()
			ge[loc].fitness += 0.1

			output = nets[loc].activate((bird.y, abs(bird.y - obj[1][pipe_ind].height), abs(bird.y - obj[1][pipe_ind].bottom)))

			if output[0] > 0.5:
				bird.jump()

		add_pipe = False
	
		for pipe in list(obj[1]):
			for loc, bird in enumerate(obj[0]):
				if pipe.collide(bird):
					ge[loc].fitness -= 1
					obj[0].pop(loc)
					nets.pop(loc)
					ge.pop(loc)

				if not pipe.passed and pipe.x < bird.x:
					pipe.passed = True
					add_pipe = True
			if pipe.x + pipe.PIPE_TOP.get_width() < 10:
				obj[1].remove(pipe)

			pipe.move()

		if add_pipe:
			obj[3] += 1
			for g in ge:
				g.fitness += 5
			obj[1].append(Pipe(500))
	
		for loc, bird in enumerate(obj[0]):
			if bird.y + bird.img.get_height() >= 700 or bird.y < 0:
				obj[0].pop(loc)
				nets.pop(loc)
				ge.pop(loc)

		obj[2].move()
		draw_window(win, obj)


def run(config_path):
	# VERY IMPORTANT FOR NEAT, Also neat is feed-forward based neural network
	config = neat.config.Config(
		neat.DefaultGenome,
		neat.DefaultReproduction,
		neat.DefaultSpeciesSet,
		neat.DefaultStagnation,
		config_path
	)
	pop = neat.Population(config)

	pop.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	pop.add_reporter(stats)

	winner = pop.run(fit_func,100)
	
if __name__ == "__main__":
	print ("MAIN")
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)
	

# NEAT - Techincal
# Using a neural network
# we will start with a basic neural network
# with 3 input neurons and one output neuron (all connected)
# Neat changes the "weights" of these connections and randomly add another node while removing another node
# Inputs - Very Important <- bird.y, top pipe, bottom pip
# Outputs - 1 neuron since we only have one decision jump or do not jump
# Activation Function - tanH there is also sigmoid, if value is greater than 0.5 we jump
# Population Size - genetic algorithms, arbitary value, 100 birds in gen 0 --> gen 1 will mutate the best bird in gen 0 --> and so on
# Fitness Function - MOST important - evaluate which bird is the best - its a metric for testing the birds - highest score
# Max Generations - if after 30 generations AI is not succesfull then we restart