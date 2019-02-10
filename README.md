# matplotlib_frame
A python script to get the possibility to add a &lt;'matplotlib.figure.Figure'> to a tkinter GUI.

## The problem
For different school projects, I had the need to use Matplotlib figures, and I wonder how to include them into some tkinter GUI. 
I find online solutions to show a single image onto a tkinter.Canvas but I wanted to have the zooming/moving/saving options you use
with matplotlib.pyplot.  

## The code
The script contains a class MatplotFrame inheriting from tkinter.Frame. The Frame contain a canva to put the PhotoImage from
the matplotlib.figure.Figure and at the bottom part, an other Frame to put all the tkinter.Button for the different actions.

The code to draw the image onto the Canvas is directly taken from this web page : https://stackoverflow.com/questions/52015845/how-to-add-matplotlib-line-chart-to-tkinter-gui
Big thanks to Stanley.
