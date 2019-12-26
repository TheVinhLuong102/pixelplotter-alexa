#!/usr/bin/python3
# -*- coding: utf-8 -*-
#import python packages
#Pixel Plotter v2.0
#install --> (sudo) apt-get install python3-pip  --> (sudo) pip3 install pillow python-ev3dev
#running --> run (sudo) python -c "import printer; printer.printer('filename.jpg')" (jpg will work along with others types)

from PIL import Image, ImageFilter
import ev3dev.ev3 as ev3
import time
import os
import sys
from termcolor import colored


# paper resolution
horiz_deg = 2050; #degress max move
horiz_width = 5; #inches
horiz_res = horiz_deg/horiz_width; # degrees per inch
vertical_deg = 24000; #degress max move
vertical_width = 7.5; #inches
vertical_res = vertical_deg/vertical_width; # degrees per inch
vert_move = 130;
horiz_move = vert_move*horiz_res/vertical_res;
#horiz_move = 7;
res = horiz_deg/horiz_move/1.1;

# Python2 compatibility variables
false = 0
true = 1

#function to ensure the motor has stopped before moving on
def waitformotor(motor):
    xxx = 0
    while motor.state != ['holding'] and motor.state != []:
        #print(motor.state)
        xxx = 0
    #print(motor.state)

# define motors and use brake/hold mode
col = ev3.ColorSensor()
paper = ev3.MediumMotor('outA')
pen1 = ev3.LargeMotor('outB')
pen2 = ""
head = ev3.MediumMotor('outC')

head.reset()
pen1.reset()
paper.reset()

pen1.stop_action = "hold"
head.stop_action = "hold"
paper.stop_action = "hold"


# initialize motors
pen1.run_to_rel_pos(speed_sp=400, position_sp=19)
waitformotor(pen1)
time.sleep(.2)
pen1.reset()

pen1.stop_action = "hold"
paper.run_to_abs_pos(position_sp=0, speed_sp=1000)

print("Init printer motors")
print("Pixel Plotter v2.0 code v4.0")

def resetMotors():
    # function to move motors back to "home"
    paper.run_to_abs_pos(position_sp=0, speed_sp=1000)
    head.run_to_abs_pos(position_sp=0, speed_sp=1000)
    waitformotor(paper)
    waitformotor(head)

#make a function to make a dot on the page
def makedot(pen,dir):
    pen.run_to_rel_pos(speed_sp=-400*dir, position_sp=-45*dir, stop_action="coast")
    waitformotor(pen) #double check if motor is stopped before raising pen
    pen.run_to_rel_pos(speed_sp=400*dir, position_sp=20*dir, stop_action="hold")
    waitformotor(pen) #double check if motor is stopped before raising pen

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
                        e4col = true
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
    return (r_array,g_array,b_array,bl_array,e4col,lastRow) # return arrays to caller

# printing function
def runPrinter(array1,width,height):
    initial = time.time()
    
    xd = 0
    yd = 0
    xda = 0 
    while yd < height:
        while xd < width:
            if array1[yd][xd] == 0: #is pixel black/colored?
                print("D", end="") #print block if black/colored pixel
                head.run_to_abs_pos(position_sp=horiz_move*xd, speed_sp=400, ramp_down_sp=500) # move pen to dot's location
                waitformotor(head)
                # lower and raise pen
                makedot(pen1,1) # print the dot
                # move pen left	
            else:
                print(" ", end="")

            xd = xd + 1
            xda = xda + 1

        print(" PCT: "+str(int(100*xda/(width*height)))+"% ; Time Remaining: "+str(int((100-100*xda/(width*height))*(time.time()-initial)/(100*xda/(width*height))))+"s") # algorithm to determine percent of print complete and estimate remaining time
        yd = yd + 1
        xd = 0
        # move paper forward
        paper.run_to_abs_pos(position_sp=vert_move*(yd), speed_sp=250,ramp_down_sp=500)
        # reset pen location
        waitformotor(paper)


def printer(filename):
    # move paper into feeder
    while col.value() < 50:
        paper.run_forever(speed_sp=1000)
    paper.run_to_rel_pos(position_sp=-7500, speed_sp=-1000, ramp_down_sp=500)
    waitformotor(paper)
    paper.stop()
    paper.reset()
        
    img1 = Image.open(filename) #open image using python imaging library (PIL)
    img2=img1.convert("RGBA")
    img = img2.transpose(Image.FLIP_LEFT_RIGHT)
    width, height = img.size # get image size

    print(width," x ",height)

    r_array, g_array, b_array, bl_array, e4col, lastRow = processPic(img, width, height) # process the picture into arrays

    runPrinter(bl_array, width, lastRow+1) # print from array
    resetMotors()
    

    if e4col == true: # if the picture contains colored pixels, repeat with the colored arrays in the order red --> green --> blue
        runPrinter(r_array, width, height)
        resetMotors()
        runPrinter(g_array, width, height)
        resetMotors()
        runPrinter(b_array, width, height)
        resetMotors()
    
