from tkinter import * 
import reader
from PIL import Image, ImageTk



book = reader.open_book('motivation.pdf')
root = Tk() 
pix = reader.get_page(book[0])
# set the mode depending on alpha
mode = "RGBA" if pix.alpha else "RGB"
img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
tkimg = ImageTk.PhotoImage(img)
root.geometry('720x480') 
root.title("PyReader") 
root.mainloop() 
