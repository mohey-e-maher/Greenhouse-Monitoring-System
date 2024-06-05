import cv2
import numpy as np
import time
import serial

# to connect to the serial port
s = serial.Serial(port='COM1', baudrate=9600)
# to detect the camera the index be :(0 : when it's integrated camera / 1-more:usb camera )
#cap = cv2.VideoCapture(0)

# start detect the color for 1 frame 
cb=0
cg = 330000
if(cb>4000):
    print ("blue")
    flag = "blue"
    s.write(b'b')
elif(cg>32000):
    print ('green')
    flag = "green"
    s.write(b'g')
elif(cr>8000):
    print ('yellow')
    flag = "yellow"
    s.write(b'y')      
else:
    flag = "no"
    print("no color detected")
while True:
    cr=0
    cb=0
    cg=0
    #ret,im = cap.read() #READ FRAMES from Camera
 #   hsv = cv2.cvtColor(im,cv2.COLOR_BGR2HSV) #CONVERT FRAMES FROM COLOR TO HSV

 
cv2.waitKey()
cap.release()
cv2.destroyAllWindows()
