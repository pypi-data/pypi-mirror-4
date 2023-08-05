######################## BEGIN LICENSE BLOCK ########################
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
######################### END LICENSE BLOCK #########################
from tkinter import *
from tkinter.ttk import *
import sys
sys.path.append('../non-free/Mojang')
import Mojang
from Mojang import *
import Knowledge
from Knowledge import *

root = Tk()
fram = Frame(root)
listbox = Listbox(root)
class Cage():
    def __init__(self):
        print("Cahe")
    def health(event):
        global category
        index = listbox.curselection()[0]
        chosen = listbox.get(index)
        try:
            if "top" in chosen:
                category = "beginning"
            elif "beginning" in category:
                category = chosen
        except:
            category = chosen

        thatLogo = Mojang.images(category,chosen,"na")

        label = Label(fram, image=thatLogo)
        label.image = thatLogo
        label.place(x=20, y=20)

        if not "not-found" in Knowledge.remember(chosen.lower()):
            listbox.delete(0, END)
            listbox.insert(END, "top")
            for item in Knowledge.remember(chosen):
                listbox.insert(END, item)
    def weild():
        root.title("pCanary by Mr. O'Neal")
        root.minsize(265,465)
        fram.pack(side=TOP)
        listbox.pack()
        listbox.insert(END, "top")
        for item in Knowledge.remember("top"):
            listbox.insert(END, item)        
        listbox.bind('<ButtonRelease-1>', Cage.health)
        thatLogo = PhotoImage(width = 264, height = 100, file = 'pCanary/Commons/Images/pCanary.gif')
        label = Label(fram, image=thatLogo).pack(side=LEFT)
        root.mainloop()
