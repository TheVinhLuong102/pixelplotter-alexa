#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import python packages
#Pixel Plotter v3.1
#install --> (sudo) apt-get install python-pip --> (sudo) pip install pillow python-ev3dev
#running --> run (sudo) python pythonfilename.py imagefilename.png (jpg will work along with others types) -->
#            you will be given a dialogue --> just type "" and return/enter to continue

from PIL import Image, ImageFilter
import ev3dev.ev3 as ev3
import time
import os
import sys
from termcolor import colored


# paper resolution
vert_move = 15;
horiz_move = 15;

# Python2 compatibility variables
false = 0
true = 1

#function to ensure the motor has stopped before moving on


def waitformotor(motor):
    xxx = 0
    while motor.state != []:
        xxx = 0
# define motors and use brake mode

paper = ev3.MediumMotor('outA')
pen1 = ev3.MediumMotor('outB')
pen2 = ev3.MediumMotor('outD')
head = ev3.MediumMotor('outC')

pen1.stop_action = "brake"
pen2.stop_action = "brake"
head.stop_action = "brake"
paper.stop_action = "brake"
head.reset()
pen1.reset()
pen2.reset()
paper.reset()


#move paper until color sensor recieves >50 reading

#paper.speed_regulation_enabled=u'on'
pen1.run_to_rel_pos(speed_sp=-400, position_sp=-53)
pen2.run_to_rel_pos(speed_sp=400, position_sp=53)
waitformotor(pen1)
waitformotor(pen2)
pen1.reset()
pen2.reset()
print("Init printer motors")
print("Pixel Plotter v3.1 code v4.0 alexa")


def resetMotors():
    paper.run_to_abs_pos(position_sp=0, speed_sp=1000)
    head.run_to_abs_pos(position_sp=0, speed_sp=1000)
#    pen1.run_to_abs_pos(position_sp=0, speed_sp=1000)
#    pen2.run_to_abs_pos(position_sp=0, speed_sp=1000)
    waitformotor(paper)
    waitformotor(head)
#    waitformotor(pen1)
#    waitformotor(pen2)

#make a function to make a dot on the page
def makedot(pen,dir):
    pen.run_to_abs_pos(speed_sp=400*dir, position_sp=55*dir)
    waitformotor(pen) #double check if motor is stopped before raising pen
    pen.run_to_abs_pos(speed_sp=-400*dir, position_sp=-54*dir)
    waitformotor(pen) #double check if motor is stopped before raising pen

#resize and flip image
#filename = sys.argv[1]

def processPic(img,width,height):
    r_array = []
    g_array = []
    b_array = []
    bl_array = []
    e4col = false
    lastRow = 0
    w = width-1
    h = 0
    while h != height:
            r_array.append([255]*width)
            g_array.append([255]*width)
            b_array.append([255]*width)
            bl_array.append([255]*width)
            while w >= 0:
                    r,g,b,a = img.getpixel((w, h)) #get rgba of each pixel
                    #check if red, green, or blue is greatest in rgb values --- check if black or white also --> then append array differently for each switch case
                    if r > g and r > b :
                        e4col = true
                        r_array[h][w] = 0
                        lastRow = h
                        print("R", end="")
                    elif g > r and g > b :
                        e4col = true
                        g_array[h][w] = 0
                        lastRow = h
                        print("G", end="")
                    elif b > r and b > g :
                        b_array[h][w] = 0
                        lastRow = h
                        print("B", end="")
                    elif b < 50 and r < 50 and g < 50 :
                        bl_array[h][w] = 0
                        lastRow = h
                        print("D", end="")
                    else:
                        print(" ", end="")
                    w = w-1 #move to next pixel -- use -1 to flip image -> make images not backward when printed
            print(" "+str(h))
            w = width-1 #reset width counter
            h = h+1 #move to next row
    return (r_array,g_array,b_array,bl_array,e4col,lastRow)


def runPrinter(array1,array2,width,height):
    initial = time.time()
    
    xd = 0
    yd = 0
    xda = 0 
    while yd < height:
        while xd < width:
            if array1[yd][xd] == 0: #is pixel black?
                print("D", end="") #print block if black pixel
                head.run_to_abs_pos(position_sp=horiz_move*xd, speed_sp=400, ramp_down_sp=500)
                waitformotor(head)
                # lower and raise pen
                makedot(pen1,1)
                # move pen left	
            elif array2[yd][xd] == 0:
                print("B", end="") #print block if red pixel
                #head.run_to_abs_pos(position_sp=(horiz_move*xd), speed_sp=400, ramp_down_sp=500)
                #waitformotor(head)
                # lower and raise pen
                #makedot(pen2,1)
            else:
                print(" ", end="")
                #move pen left
            if array2[yd][max([0,(xd-18)])] == 0:
                #print("B", end="") #print block if red pixel
                head.run_to_abs_pos(position_sp=(horiz_move*xd), speed_sp=400, ramp_down_sp=500)
                waitformotor(head)
                # lower and raise pen
                makedot(pen2,-1)
            xd = xd + 1
            xda = xda + 1

        print(" PCT: "+str(int(100*xda/(width*height)))+"% ; Time Remaining: "+str(int((100-100*xda/(width*height))*(time.time()-initial)/(100*xda/(width*height))))+"s")
        yd = yd + 1
        xd = 0
        # move paper forward
        paper.run_to_abs_pos(position_sp=vert_move*(yd), speed_sp=250,ramp_down_sp=500)
        # reset pen location
        waitformotor(paper)


def printer(filename):
    img1 = Image.open(filename) #open image
    img2=img1.convert("RGBA")
    img = img2.transpose(Image.FLIP_LEFT_RIGHT)
    width, height = img.size # get image size

    print(width," x ",height)

    r_array, g_array, b_array, bl_array, e4col, lastRow = processPic(img, width, height)

    #x = input('Is this picture ok? Press enter to print black/blue...') #wait for dialogue to be answered then start printing

    time.sleep(1)

    runPrinter(bl_array, b_array, width, lastRow+1)
    resetMotors()
    

    if e4col == true:
        #x = input('Ready to print red/green? Press enter to continue...') #wait for dialogue to be answered then start printing
        runPrinter(r_array, g_array, width, height)
        resetMotors()
    
