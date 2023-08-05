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

import sys

class Knowledge():
    def remember(something):
        notfound = {'not-found':1}
        top = {'blocks':1,'dye':1,'enchbrew':1,'food':1}
        blocks = {'bookshelf':1,'brickblock':1,'brickslab':1,'brickstairs':1,'clayblock':1,'cobbleslab':1,'cobblestairs':1,'gemblock':1,'goldblock':1,'ironblock':1,'lantem':1,'lightstone':1,'sandslab':1,'sandstone':1,'snowblock':1,'stonebrick':1,'stonebrickslab':1,'stonebrickstairs':1,'stoneslab':1,'tnt':1}
        dye = {'blackwool':1,'bluewool':1,'bonemeals':1,'brownwool':1,'cyan':1,'cyanwool':1,'gray':1,'graywool':1,'green':1,'greenwool':1,'lightblue':1,'lightbluewool':1,'lightgray':1,'lightgraywool':1,'limewool':1,'magenta':1,'magentawool':1,'orange':1,'orangewooll':1,'pink':1,'pinkwool':1,'purple':1,'purplewool':1,'redwool':1,'rose':1}
        enchbrew = {'blazepowder':1,'brewingstand':1,'cauldron':1,'enchantmenttable':1,'fermentedspidereye':1,'glassbottle':1,'glisteringmelon':1,'goldnugget':1,'magmacream':1}
        food = {'bowls':1,'bread':1,'cake':1,'cookie':1,'golden_apple':1,'melonblock':1,'melonseeds':1,'mushroom_stew':1,'pumpkinseeds':1,'sugar':1}
        general = {'chest':1,'furnance':1,'sticks':1,'torch':1,'wood':1,'workbench':1}
        mech = {}
        misc = {}
        mobs = {}
        root = {}
        smelting = {}
        tools = {}
        transport = {}
        weapons = {}
        if something.lower() == "blocks":
            return blocks
        elif something.lower() == "dye":
            return dye
        elif something.lower() == "enchbrew":
            return enchbrew
        elif something.lower() == "food":
            return food
        elif something.lower() == "general":
            return general
        elif something.lower() == "mech":
            return mech
        elif something.lower() == "misc":
            return misc
        elif something.lower() == "mobs":
            return mobs
        elif something.lower() == "root":
            return root
        elif something.lower() == "smelting":
            return smelting
        elif something.lower() == "tools":
            return tools
        elif something.lower() == "transport":
            return transport
        elif something.lower() == "weapons":
            return weapons
        elif something.lower() == "top":
            return top
        return notfound
