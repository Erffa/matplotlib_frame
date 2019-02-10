
from tkinter import Tk
import matplotlib as mpl
import numpy as np

from mywidgets import MatplotFrame

tk = Tk()
mf = MatplotFrame(tk)
mf.pack(expand=True, fill='both')	


xx = np.linspace(0,5,1000)
yy = np.sin(xx)
fig = mpl.figure.Figure()
ax = fig.add_subplot(111)	
ax.plot(xx,yy)

''' test superposition figure 
fig = mpl.figure.Figure()
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(1,2,2)
xx = np.linspace(-5,5,500)
yy = np.sin(xx)
ax1.plot(xx,yy)
ax2.plot(xx,yy)
# '''

''' test two figure and 3d
from mpl_toolkits.mplot3d import Axes3D

fig = mpl.figure.Figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212,  projection='3d')
xx1 = np.linspace(-5,5,500)
xx2 = np.linspace(100,110,500)
ax1.plot(xx1, np.sin(xx1))
ax2.plot(xx2, 100+np.cos(2*xx2))
# '''


mf.set_figure(fig)

tk.mainloop()
