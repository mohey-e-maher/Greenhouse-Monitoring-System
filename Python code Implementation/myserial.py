import cv2
import numpy as np
import time
import serial

# to connect to the serial port
s = serial.Serial(port='COM1', baudrate=9600)
# to detect the camera the index be :(0 : when it's integrated camera / 1-more:usb camera )
cap = cv2.VideoCapture(0)

# start detect the color for 1 frame 
flag = ""
cr=0
cb=0
cg=0
ret,im = cap.read()
hsv = cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
#yellow
lowyellow=np.array([20,50,100],dtype=np.uint8) #Lower Limit of Yetllow color
highyellow=np.array([42,255,255],dtype=np.uint8) #Upper LIMIT of Yellow Color 
mask = cv2.inRange(hsv, lowyellow,highyellow) #Count Total number of pixel in lower and higher limit range correspond to Yellow color
#blue
lowblue=np.array([110,130,50],dtype=np.uint8)
highblue=np.array([130,255,255],dtype=np.uint8)
maskb = cv2.inRange(hsv, lowblue,highblue)
#green
lowgreen=np.array([44,54,63],dtype=np.uint8)
highgreen=np.array([90,255,255],dtype=np.uint8)
maskg = cv2.inRange(hsv, lowgreen,highgreen)

cv2.imshow("",im)   # show your video output on windows )
cr=cv2.countNonZero(mask) #count the total number of non-zero pixel from mask for yellow color
cb=cv2.countNonZero(maskb) #count the total number of non-zero pixel from mask for blue color
cg=cv2.countNonZero(maskg)  #count the total number of non-zero pixel from mask for blue green
'''
Depending upon pixel limit print color name on output window
'''
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
    s.write(b'n')
    flag = "no"
    print("no color detected")
while True:
    cr=0
    cb=0
    cg=0
    ret,im = cap.read() #READ FRAMES from Camera
    hsv = cv2.cvtColor(im,cv2.COLOR_BGR2HSV) #CONVERT FRAMES FROM COLOR TO HSV

    #yellow
    lowyellow=np.array([20,50,100],dtype=np.uint8) #Lower Limit of Yetllow color
    highyellow=np.array([42,255,255],dtype=np.uint8) #Upper LIMIT of Yellow Color 
    mask = cv2.inRange(hsv, lowyellow,highyellow) #Count Total number of pixel in lower and higher limit range correspond to Yellow color
    #blue
    lowblue=np.array([110,130,50],dtype=np.uint8)
    highblue=np.array([130,255,255],dtype=np.uint8)
    maskb = cv2.inRange(hsv, lowblue,highblue)
    #green
    lowgreen=np.array([44,54,63],dtype=np.uint8)
    highgreen=np.array([90,255,255],dtype=np.uint8)
    maskg = cv2.inRange(hsv, lowgreen,highgreen)
    
    cv2.imshow("",im)   # show your video output on windows )
    cr=cv2.countNonZero(mask) #count the total number of non-zero pixel from mask for yellow color
    cb=cv2.countNonZero(maskb) #count the total number of non-zero pixel from mask for blue color
    cg=cv2.countNonZero(maskg)  #count the total number of non-zero pixel from mask for blue green
    '''
    Depending upon pixel limit print color name on output window
    '''
    if(cb>4000):
        if(flag!="blue"):
            print ('blue')
            flag = "blue"
            s.write(b'b')
    elif(cg>32000):
        if(flag!="green"):
            print ('green')
            flag = "green"
            s.write(b'g')
    elif(cr>8000):
        if(flag !="yellow"):
            print ('yellow')
            flag = "yellow"
            s.write(b'y')      
    else:
        if(flag !="no"):
            flag = "no"
            s.write(b'n')
            print("no color detected")
    if cv2.waitKey(1) & 0xff==ord('q'):      
        break    
cv2.waitKey()
cap.release()
cv2.destroyAllWindows()
