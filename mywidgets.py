
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk

import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg


from tkinter import Button
from tkinter import Canvas
from tkinter import Frame
from tkinter import PhotoImage
from tkinter import StringVar

from tkinter.ttk import Separator
from tkinter.filedialog import asksaveasfilename

''' class MatplotFrame
Create a Frame containg a canvas to support the image from a matplotlib element.
Can also possess an other frame containing the buttons to realize different actions.
'''
class MatplotFrame(Frame):
#####################################################################################################################################################
#                                                                                                                                                   #
#                                                                    __INIT__                                                                       #
#                                                                                                                                                   #
#####################################################################################################################################################
#  
#
	def __init__(self, master_, options=True):

		# call to super 
		super(MatplotFrame,self).__init__(master_)

		# all the attributes
		self.photo = None
		self.fig = None
		self.last_press_event = None
		self.last_dragged_event = None
		self.rectangular_selection = None
		self.axe_current = None
		self.lim_old = None
		self.lim_new = None

		# current action (changed pressing buttons)
		self.v_action = StringVar(self)
		self.v_action.set("None")

		# variables to undo-redo actions
		self.modif_idx = -1;
		self.modif_list = []

		# create the graphic elements
		self.canvas = Canvas(self, bg='light blue')
		self.frame = Frame(self, bg='light pink', height=50)

		# pack the graphic elements
		self.canvas.pack(expand=True, fill='both', side='top')
		if (options): # construction de la barre d'options
			self.build_frame()
			self.frame.pack(fill='x', side='bottom')

		# bind des actions
		self.canvas.bind('<Configure>', self.configure)
		self.canvas.bind('<Button-1>', self.press)
		self.canvas.bind('<B1-Motion>', self.dragged)
		self.canvas.bind('<ButtonRelease-1>', self.release1)
		self.canvas.bind('<Button-3>', self.press)
		self.canvas.bind('<B3-Motion>', self.dragged)
		self.canvas.bind('<ButtonRelease-3>', self.release3)

	''' class OptionButton
	Class to create all the buttons for the option.
	Decide the width x height and the background color
	'''
	class OptionButton(Button):
		def __init__(self, frame_, command_, photo_):
			super(MatplotFrame.OptionButton, self).__init__(
				frame_, command=command_, image=photo_, # given in parameters
				height=40, width=40, bg='white') # default

	def build_frame(self):

		# keep a reference (or else, the image is not printed)
		self.photo_home = PhotoImage(file="pics\\home.png")
		self.photo_left_arrow =  PhotoImage(file="pics\\arrow_left.png")
		self.photo_right_arrow = PhotoImage(file="pics\\arrow_right.png")
		self.photo_move = PhotoImage(file="pics\\move.png")
		self.photo_zoom = PhotoImage(file="pics\\zoom.png")
		self.photo_save = PhotoImage(file="pics\\save.png")
		
		# the button for the options
		bu_home = MatplotFrame.OptionButton(self.frame, self.command_home, self.photo_home)
		bu_CTRLZ = MatplotFrame.OptionButton(self.frame, self.command_undo, self.photo_left_arrow)
		bu_CTRLY = MatplotFrame.OptionButton(self.frame, self.command_redo, self.photo_right_arrow)
		bu_zoom = MatplotFrame.OptionButton(self.frame, self.command_zoom, self.photo_zoom)
		bu_move = MatplotFrame.OptionButton(self.frame, self.command_move, self.photo_move)
		bu_save = MatplotFrame.OptionButton(self.frame, self.command_savefig, self.photo_save)

		# separators
		sep1 = Separator(self.frame, orient='vertical')
		sep2 = Separator(self.frame, orient='vertical')
		sep3 = Separator(self.frame, orient='vertical')

		bu_home.grid(row=1, column=0)
		sep1.grid(row=1, column=1, sticky='ns', padx=10)

		bu_CTRLZ.grid(row=1,column=2)
		bu_CTRLY.grid(row=1,column=3)
		sep2.grid(row=1,column=4, sticky='ns', padx=10)

		bu_move.grid(row=1,column=5)
		bu_zoom.grid(row=1,column=6)
		sep3.grid(row=1,column=7, sticky='ns', padx=10)

		bu_save.grid(row=1,column=8)

		return
#####################################################################################################################################################
#                                                                                                                                                   #
#                                                            ACTIONS BOUTONS                                                                        #
#                                                                                                                                                   #
#####################################################################################################################################################

########################################################################################
#                                       SAVE PNG                                       #
########################################################################################

	def command_savefig(self):

		# authorized extensions
		mask = [
		(".png","*.png"),
    	(".ppm","*.ppm")]

    	# ask for the name and format (if cancel, return False)
		filename = asksaveasfilename(
			defaultextension=".png",
			filetypes=mask )#confirmoverwrite = False
		if (filename == ""):
			return False
		fileformat = filename.split('.')[-1]

		# create the picture
		self.photo.write(filename, format=fileformat)

		return True

######################################################################################## 
#                                        UNDO REDO                                     #
########################################################################################

	''' Modif
	class to register the modification on a axe
	used to accomplish te undo-redo action '''
	class Modif():

		def __init__(self, axe_, lim_old_, lim_new_):
			self.axe = axe_
			self.lim_old = lim_old_
			self.lim_new = lim_new_

		def undo(self):
			self.axe.set_xlim(self.lim_old[0])
			self.axe.set_ylim(self.lim_old[1])

		def redo(self):
			self.axe.set_xlim(self.lim_new[0])
			self.axe.set_ylim(self.lim_new[1])

	''' BackHome
	Register all the change involved to go back to the begining, and possibly undo
	this action to do all the modification again'''
	class BackHome():

		def __init__(self, frame_):
			self.frame = frame_
			self.idx = int(frame_.modif_idx)+1

		def redo(self):
			# BackHome undo all the precedent actions
			for action in self.frame.modif_list[self.idx-1::-1]:
				if isinstance(action, MatplotFrame.Modif):
					action.undo()
			

		def undo(self):
			# BackHome redo,redoes all the precedent actions
			for action in self.frame.modif_list[self.idx-1::-1]:
				if isinstance(action, MatplotFrame.Modif):
					action.redo()


	def register_modif(self):

		# catch the new lim of the axe
		self.lim_new = (self.axe_current.get_xlim() , self.axe_current.get_ylim())

		# if no changes to be seen, cancel
		if (self.lim_new==self.lim_old):
			return False

		# delete everything after the idx
		self.modif_list[self.modif_idx+1:] = []

		# add the new modification
		self.modif_list += [ MatplotFrame.Modif(self.axe_current, self.lim_old,self.lim_new) ] 
		self.modif_idx += 1 # move the idx up
		self.modif_list[self.modif_idx].redo() # execute the modification

		self.paint_figure()
		return True


	def command_undo(self):

		# if first index, nothing to do
		if (self.modif_idx >= 0):

			# undo the last modification
			self.modif_list[self.modif_idx].undo()

			# the last modification is now the previous one
			self.modif_idx -= 1

			#
			self.paint_figure()

		return 

	def command_redo(self):

		# if last index, there s no going up
		if (self.modif_idx<len(self.modif_list)-1):
			
			# move to the next modif
			self.modif_idx += 1

			# redo the modification
			self.modif_list[self.modif_idx].redo()

			#
			self.paint_figure()

		return
	
	def command_home(self):
		# we verify if 
		# - there has been an action before (if no modif, action is useless)
		# - if the last action was a back home, we ain't going twice (won't change anything)

		if self.modif_idx==-1:
			return False

		if isinstance(self.modif_list[self.modif_idx], MatplotFrame.BackHome):
			return False

		

		# delete everything after the idx
		self.modif_list[self.modif_idx+1:] = []

		# add the new modification
		self.modif_list += [ MatplotFrame.BackHome(self) ] 
		self.modif_idx += 1 # move the idx up
		self.modif_list[self.modif_idx].redo() # execute the modification

		#
		self.paint_figure()

		return

########################################################################################                                                                                                                                                   #
#                                        ZOOM MOVE                                     #                                                                                                                                                 #
########################################################################################

	def command_zoom(self):
		self.canvas.configure(cursor='tcross')
		self.v_action.set("zoom")

	def command_move(self):
		self.canvas.configure(cursor='fleur')
		self.v_action.set("move")

#####################################################################################################################################################
#                                                                                                                                                   #
#                                                            ACTIONS SOURIS/TOUCHES                                                                 #
#                                                                                                                                                   #
#####################################################################################################################################################
#  
#
	def is_event_inside_axe(self, axe, event):
		# position proportionelle de l'event
		x_prop = event.x/self.fig.dpi/self.fig.get_figwidth()
		y_prop = event.y/self.fig.dpi/self.fig.get_figheight()

		# position des sommets de la zone de l'axe
		((x0,y0),(x1,y1)) = axe.get_position().get_points()

		# test si inside
		if ((x_prop >= x0)	and	(x_prop <= x1) and (y_prop <= 1-y0) and (y_prop >= 1-y1)):
			return True

		return False

	def get_axes_selected(self, event):
		
		axes_list = []
		for axe in self.fig.get_axes():
			if self.is_event_inside_axe(axe, event):
				axes_list.append(axe)
			
		return axes_list

		
	def press(self, event):

		# identify which axes is pressed first (None if no axe clicked)
		try:
			# try to get the axe pressed
			self.axe_current = self.get_axes_selected(event)[-1]
			# register the current disp of the axe to create the Modif instances
			self.lim_old = (self.axe_current.get_xlim() , self.axe_current.get_ylim())
		except(IndexError):
			self.axe_current = None

		# register the event as the first event
		self.last_press_event = event # to create the Modif instances
		self.last_dragged_event = event # to make the move action possible without changing the last_press_event

		return

	def dragged(self, event):

		# if no action or no axe selected
		if (self.v_action.get()=='None' or self.axe_current==None):
			return

		# MOVE ACTION
		# The graph have to move following the mouse
		if (self.v_action.get()=='move'):
			
			# si en dehors de la zone, pas d'action
			# if (test inside canva...)

			# calcul du deplacement selon x et y
			old_pos =  self.get_pos_inside_axe(self.axe_current, self.last_dragged_event)
			new_pos =  self.get_pos_inside_axe(self.axe_current, event)
			move_x = new_pos[0] - old_pos[0]
			move_y = new_pos[1] - old_pos[1]

			# changement du dernier event pris en compte
			self.last_dragged_event = event

			# deplacement du cadre
			xlim_left, xlim_right = self.axe_current.get_xlim()
			ylim_left, ylim_right = self.axe_current.get_ylim()
			self.axe_current.set_xlim(xlim_left-move_x, xlim_right-move_x)
			self.axe_current.set_ylim(ylim_left-move_y, ylim_right-move_y)

			# redessin de la figure
			self.paint_figure()

			return			

		# ZOOM ACTION
		# La sélection rectangulaire doit suivre la position de la souris
		if (self.v_action.get()=='zoom'):

			# delete rectangular selection if existing
			if (self.rectangular_selection!=None):
				self.canvas.delete(self.rectangular_selection)

			# create new rectangular selection 
			old_x,old_y = (self.last_press_event.x, self.last_press_event.y)
			new_x,new_y = (event.x,event.y)
			self.rectangular_selection = self.canvas.create_rectangle(old_x,old_y, new_x,new_y, dash=(4, 4))
			return

		return
	
	def release1(self, event):

		# if no action or no axe selected
		if (self.v_action.get()=='None' or self.axe_current==None):
			return

		if (self.v_action.get()=='move'):
			self.register_modif()
			return

		if (self.v_action.get()=='zoom'):

			# delete rectangular selection
			if (self.rectangular_selection!=None):
				self.canvas.delete(self.rectangular_selection)

			# if no movement, no action
			if ( (self.last_press_event.x,self.last_press_event.y)  == (event.x,event.y) ):
				return

			# if the release event is inside the current axe
			if (self.is_event_inside_axe(self.axe_current, event)):
				old_pos_x,old_pos_y = self.get_pos_inside_axe(self.axe_current, self.last_press_event)
				new_pos_x,new_pos_y = self.get_pos_inside_axe(self.axe_current, event)
				self.axe_current.set_xlim(min(old_pos_x,new_pos_x),max(old_pos_x,new_pos_x))
				self.axe_current.set_ylim(min(old_pos_y,new_pos_y),max(old_pos_y,new_pos_y))
				
				# register the modif in the listing
				self.register_modif()
			return
		return

	def release3(self, event):

		# if no action or no axe selected
		if (self.v_action.get()=='None' or self.axe_current==None):
			return

		if (self.v_action.get()=='zoom'):

			# delete rectangular selection
			if (self.rectangular_selection!=None):
				self.canvas.delete(self.rectangular_selection)

			# if no movement, no action
			if ( (self.last_press_event.x,self.last_press_event.y)  == (event.x,event.y) ):
				return

			# if the release event is inside the current axe
			if (self.is_event_inside_axe(self.axe_current, event)):

				old_pos_x,old_pos_y = self.get_pos_inside_axe(self.axe_current, self.last_press_event)
				new_pos_x,new_pos_y = self.get_pos_inside_axe(self.axe_current, event)

				x_inf,x_sup = self.axe_current.set_xlim()
				y_inf,y_sup = self.axe_current.set_ylim()
				
				new_x_inf = x_inf - (min(old_pos_x,new_pos_x)-x_inf)
				new_x_sup = x_sup + (x_sup - max(old_pos_x,new_pos_x))

				new_y_inf = y_inf - (min(old_pos_y,new_pos_y)-y_inf)
				new_y_sup = y_sup + (y_sup - max(old_pos_y,new_pos_y))

				self.axe_current.set_xlim(new_x_inf,new_x_sup)
				self.axe_current.set_ylim(new_y_inf,new_y_sup)

				# register / show the modification
				self.register_modif()

				return
			return 	

	def get_prop_inside_fig(self, event):

		x_prop = event.x/self.fig.dpi/self.fig.get_figwidth()
		y_prop = event.y/self.fig.dpi/self.fig.get_figheight()

		xi = (x_prop-self.fig.subplotpars.left)/(self.fig.subplotpars.right-self.fig.subplotpars.left)
		yi = (y_prop-1+self.fig.subplotpars.top)/(self.fig.subplotpars.top-self.fig.subplotpars.bottom)

		return (xi,yi)

	def get_pos_inside_axe(self, axe, event):

		xi,yi = self.get_prop_inside_fig(event)
		
		x_inf, x_max = axe.set_xlim()
		y_inf, y_max = axe.set_ylim()

		x_pos = xi*(x_max-x_inf)+x_inf
		y_pos = (1-yi)*(y_max-y_inf)+y_inf

		return (x_pos,y_pos)


#####################################################################################################################################################
#                                                                                                                                                   #
#                                                        DESSINS MATPLOTLIB SUR CANVAS                                                              #
#                                                                                                                                                   #
#####################################################################################################################################################

	def configure(self, event):
		self.paint_figure()
		return

	def set_figure(self, figure_):

		self.fig = figure_
		self.paint_figure()
		self.modif_idx = -1
		
	def paint_figure(self): 
		''' 
		Draw a matplotlib figure onto a Tk canvas
		loc: location of top-left corner of figure on canvas in pixels.
		Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
		'''
		# si pas de figure, no bother
		if (self.fig==None):
			return

		# set the size of the figure
		self.canvas.update()
		w = self.canvas.winfo_width()
		h = self.canvas.winfo_height()
		self.fig.set_size_inches(w/self.fig.dpi, h/self.fig.dpi)
				
		#
		figure_canvas_agg = FigureCanvasAgg(self.fig)
		figure_canvas_agg.draw()

		figure_x,figure_y, figure_w,figure_h = self.fig.bbox.bounds
		figure_w,figure_h = int(figure_w), int(figure_h)
		
		self.photo = PhotoImage(master=self.canvas, width=figure_w, height=figure_h)

		# Position: convert from top-left anchor to center anchor
		self.canvas.create_image(0 + figure_w/2, 0 + figure_h/2, image=self.photo)

		# Unfortunately, there's no accessor for the pointer to the native renderer
		tkagg.blit(self.photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)

		# Return a handle which contains a reference to the photo object
		# which must be kept live or else the picture disappears
		return self.photo