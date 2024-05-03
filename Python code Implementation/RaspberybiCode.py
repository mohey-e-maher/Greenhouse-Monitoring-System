from goto import *
import time
import resource
import spidev
import RPi.GPIO as GPIO
import pio
import Ports
# Peripheral Configuration Code (do not edit)
#---CONFIG_BEGIN---
import cpu
import FileStore
import VFP
import Ports

pio.uart=Ports.UART () # Define serial port

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

# to read from GPIO Pins
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Define GPIO to LCD
LCD_RS = 7
LCD_E  = 11
LCD_D4 = 12
LCD_D5 = 13
LCD_D6 = 15
LCD_D7 = 16

# Define GPIO to keypad
R1 = 29
R2 = 31
R3 = 32
R4 = 33
C1 = 36
C2 = 35
C3 = 38
C4 = 37

# Define Sensors
Rain_sensor = 18
flame_Sensor = 40
temp_channel  = 0

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005
inputstring = ""
hidekey=""
secretkey = "111"
delay = 1
check = 0

#define the write & earse to the screen
GPIO.setup(LCD_E, GPIO.OUT)  # E (Earse the screen)
GPIO.setup(LCD_RS, GPIO.OUT) # RS (write to the screen)
# the first 4 binary input
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7

#define the keypad buttons
GPIO.setup(R1, GPIO.OUT) # DB7
GPIO.setup(R2, GPIO.OUT) # DB7
GPIO.setup(R3, GPIO.OUT) # DB7
GPIO.setup(R4, GPIO.OUT) # DB7
GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#define sensors pins
GPIO.setup(Rain_sensor, GPIO.IN)
GPIO.setup(flame_Sensor, GPIO.IN)

# Define device screen constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line



# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
  
  
 
# How to calculate temperature from
# TMP36 data, rounded to specified
# number of decimal places.
  # ADC Value
  # (approx)  Temp  Volts
  #    0      -50    0.00
  #   78      -25    0.25
  #  155        0    0.50
  #  233       25    0.75
  #  310       50    1.00
  #  465      100    1.50
  #  775      200    2.50
  # 1023      280    3.30

  
#lcd_init() : this function is used to initialized lcd by sending the different commands
def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

#lcd_byte(bits ,mode):the main purpose of this function to convert the byte data into bit and send to lcd port
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()


# lcd_toggle_enable() :basically this is used to toggle Enable pin
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)



# lcd_string(message,line) :print the data on lcd 
def lcd_string(message,line):
  # Send string to display
 
  message = message.ljust(LCD_WIDTH," ")
 
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def readLine(line, characters):
    global inputstring
    global hidekey
    GPIO.output(line, GPIO.HIGH)
    time.sleep(0.02)
    if(GPIO.input(C1) == 1):
      inputstring = inputstring +characters[0]
      hidekey = hidekey +"*"
      lcd_string(hidekey,LCD_LINE_2)
    elif(GPIO.input(C2) == 1):
      inputstring = inputstring +characters[1]
      hidekey = hidekey +"*"
      lcd_string(hidekey,LCD_LINE_2)
    elif(GPIO.input(C3) == 1):
      inputstring = inputstring +characters[2]
      hidekey = hidekey +"*"
      lcd_string(hidekey,LCD_LINE_2)
    elif(GPIO.input(C4) == 1):
      if(characters[3] ==  "#"):
       if(inputstring == secretkey):             #>>valid person
        lcd_string("valid person ",LCD_LINE_2)	 
        time.sleep(1)
        lcd_byte(0x01,LCD_CMD)
        lcd_string("System Start ",LCD_LINE_1)
        lcd_string("Now ",LCD_LINE_2)
        time.sleep(1)
        lcd_byte(0x01,LCD_CMD) # 000001 Clear display
	######################################
        while 1 :
         #show the tempreture
         lcd_byte(0x01,LCD_CMD) # 000001 Clear display
         lcd_string("Temperature  ",LCD_LINE_1)
         temp = ReadChannel(temp_channel)
         ntemp = ((temp * 330)/float(1023))
         ntemp = round(ntemp,2)
         lcd_string(str(ntemp),LCD_LINE_2)
         time.sleep(0.5)
         #show Is it rain ?? <rain sensor>
         lcd_byte(0x01,LCD_CMD) # 000001 Clear display
         lcd_string("Rain Sensor: ",LCD_LINE_1)
         Raino = GPIO.input(Rain_sensor)
         if (Raino==True):
          lcd_string("It Rains",LCD_LINE_2)
          time.sleep(0.5)
          lcd_byte(0x01,LCD_CMD)
         else:
          lcd_string("No Rain",LCD_LINE_2)
          time.sleep(0.5)
         #there's flame ??
         lcd_byte(0x01,LCD_CMD)
         lcd_string("Flame Sensor:",LCD_LINE_1)
         flamo = GPIO.input(flame_Sensor)
         if (flamo==True):
          lcd_string("DAGEROUS! Fire",LCD_LINE_2)
          time.sleep(0.5)
          lcd_byte(0x01,LCD_CMD)
         else:
          lcd_string("Secured",LCD_LINE_2)
          time.sleep(0.5)
          lcd_byte(0x01,LCD_CMD)
         lcd_string("Camera ON",LCD_LINE_1)
         lcd_string("Put Leaf",LCD_LINE_2)
         try:
          Data=pio.uart.recv()
          if(Data == "y"):
            #show the color on the LCD
            lcd_string("Yellow color",LCD_LINE_1)
            lcd_string("Detected",LCD_LINE_2)
            time.sleep(0.5)
            lcd_byte(0x01,LCD_CMD) # 000001 Clear display
          elif(Data == "b"):
            lcd_string("Blue color",LCD_LINE_1)
            lcd_string("Detected",LCD_LINE_2)
            time.sleep(0.5)
            lcd_byte(0x01,LCD_CMD) # 000001 Clear display
          else:
             lcd_byte(0x01,LCD_CMD) # 000001 Clear display
             lcd_string("No color",LCD_LINE_1)
             lcd_string("Detected",LCD_LINE_2)
             time.sleep(0.5)
         except:
          p.stop()
          GPIO.cleanup()
         lcd_string("HOLD 0 To LOGOUT",LCD_LINE_1)
         time.sleep(1)
         if(GPIO.input(C2) == 1):
          lcd_string("BYE!",LCD_LINE_2)
          time.sleep(1)
          lcd_byte(0x01,LCD_CMD)
          break
	####################################
        lcd_string("Enter Password ",LCD_LINE_1)
        lcd_string("",LCD_LINE_2)
        inputstring = ""
        hidekey= ""
       else:
        lcd_string("Unknown Person",LCD_LINE_2)
        time.sleep(1)
        lcd_string("AGAIN",LCD_LINE_2)
        inputstring = ""
        hidekey= ""
      else:
       inputstring = inputstring +characters[3]
       hidekey = hidekey +"*"
       lcd_string(hidekey,LCD_LINE_2)
    GPIO.output(line, GPIO.LOW)
    time.sleep(0.02)



# Define delay between readings
delay = 5
lcd_init()
lcd_string("Welcome ",LCD_LINE_1)
time.sleep(1)
lcd_string("Enter Password ",LCD_LINE_1)
while 1:
   readLine(R1, ["7","8","9","/"])
   readLine(R2, ["4","5","6","*"])
   readLine(R3, ["1","2","3","-"])
   readLine(R4, ["C","0","=","#"])

from goto import *
import time
import resource
import spidev
import RPi.GPIO as GPIO
import pio
import Ports
# Peripheral Configuration Code (do not edit)
#---CONFIG_BEGIN---
import cpu
import FileStore
import VFP
import Ports

pio.uart=Ports.UART () # Define serial port

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

# to read from GPIO Pins
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Define GPIO to LCD
LCD_RS = 7
LCD_E  = 11
LCD_D4 = 12
LCD_D5 = 13
LCD_D6 = 15
LCD_D7 = 16

# Define GPIO to keypad
R1 = 29
R2 = 31
R3 = 32
R4 = 33
C1 = 36
C2 = 35
C3 = 38
C4 = 37

# Define Sensors
Rain_sensor = 18
flame_Sensor = 40
temp_channel  = 0

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005
inputstring = ""
hidekey=""
secretkey = "111"
delay = 1
check = 0

#define the write & earse to the screen
GPIO.setup(LCD_E, GPIO.OUT)  # E (Earse the screen)
GPIO.setup(LCD_RS, GPIO.OUT) # RS (write to the screen)
# the first 4 binary input
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7

#define the keypad buttons
GPIO.setup(R1, GPIO.OUT) # DB7
GPIO.setup(R2, GPIO.OUT) # DB7
GPIO.setup(R3, GPIO.OUT) # DB7
GPIO.setup(R4, GPIO.OUT) # DB7
GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#define sensors pins
GPIO.setup(Rain_sensor, GPIO.IN)
GPIO.setup(flame_Sensor, GPIO.IN)

# Define device screen constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line


# How to calculate temperature from
# TMP36 data, rounded to specified
# number of decimal places.
  # ADC Value
  # (approx)  Temp  Volts
  #    0      -50    0.00
  #   78      -25    0.25
  #  155        0    0.50
  #  233       25    0.75
  #  310       50    1.00
  #  465      100    1.50
  #  775      200    2.50
  # 1023      280    3.30

  
#lcd_init() : this function is used to initialized lcd by sending the different commands
def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

#lcd_byte(bits ,mode):the main purpose of this function to convert the byte data into bit and send to lcd port
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()


# lcd_toggle_enable() :basically this is used to toggle Enable pin
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)



# lcd_string(message,line) :print the data on lcd 
def lcd_string(message,line):
  # Send string to display
 
  message = message.ljust(LCD_WIDTH," ")
 
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def readLine(line, characters):
    global inputstring
    global hidekey
    GPIO.output(line, GPIO.HIGH)
    time.sleep(0.02)
    if(GPIO.input(C1) == 1):
      inputstring = inputstring +characters[0]
      hidekey = hidekey +"*"
      lcd_string(hidekey,LCD_LINE_2)
    elif(GPIO.input(C2) == 1):
      inputstring = inputstring +characters[1]
      hidekey = hidekey +"*"
      lcd_string(hidekey,LCD_LINE_2)
    elif(GPIO.input(C3) == 1):
      inputstring = inputstring +characters[2]
      hidekey = hidekey +"*"
      lcd_string(hidekey,LCD_LINE_2)
    elif(GPIO.input(C4) == 1):
      if(characters[3] ==  "#"):
       if(inputstring == secretkey):             #>>valid person
        lcd_string("valid person ",LCD_LINE_2)	 
        time.sleep(1)
        lcd_byte(0x01,LCD_CMD)
        lcd_string("System Start ",LCD_LINE_1)
        lcd_string("Now ",LCD_LINE_2)
        time.sleep(1)
        lcd_byte(0x01,LCD_CMD) # 000001 Clear display
	######################################
        while 1 :
         #show the tempreture
         lcd_byte(0x01,LCD_CMD) # 000001 Clear display
         lcd_string("Temperature  ",LCD_LINE_1)
         temp = ReadChannel(temp_channel)
         ntemp = ((temp * 330)/float(1023))
         ntemp = round(ntemp,2)
         lcd_string(str(ntemp),LCD_LINE_2)
         time.sleep(0.5)
         #show Is it rain ?? <rain sensor>
         lcd_byte(0x01,LCD_CMD) # 000001 Clear display
         lcd_string("Rain Sensor: ",LCD_LINE_1)
         Raino = GPIO.input(Rain_sensor)
         if (Raino==True):
          lcd_string("It Rains",LCD_LINE_2)
          time.sleep(0.5)
          lcd_byte(0x01,LCD_CMD)
         else:
          lcd_string("No Rain",LCD_LINE_2)
          time.sleep(0.5)
         #there's flame ??
         lcd_byte(0x01,LCD_CMD)
         lcd_string("Flame Sensor:",LCD_LINE_1)
         flamo = GPIO.input(flame_Sensor)
         if (flamo==True):
          lcd_string("DAGEROUS! Fire",LCD_LINE_2)
          time.sleep(0.5)
          lcd_byte(0x01,LCD_CMD)
         else:
          lcd_string("Secured",LCD_LINE_2)
          time.sleep(0.5)
          lcd_byte(0x01,LCD_CMD)
         lcd_string("HOLD 0 To LOGOUT",LCD_LINE_1)
         time.sleep(1)
         if(GPIO.input(C2) == 1):
          lcd_string("BYE!",LCD_LINE_2)
          time.sleep(1)
          lcd_byte(0x01,LCD_CMD)
          break
         try:
          Data=pio.uart.recv()
          if(Data == "y"):
            #show the color on the LCD
            lcd_string("Yellow color",LCD_LINE_1)
            lcd_string("Detected",LCD_LINE_2)
            time.sleep(0.5)
            lcd_byte(0x01,LCD_CMD) # 000001 Clear display
          elif(Data == "b"):
            lcd_string("Blue color",LCD_LINE_1)
            lcd_string("Detected",LCD_LINE_2)
            time.sleep(0.5)
            lcd_byte(0x01,LCD_CMD) # 000001 Clear display
          else:
             lcd_byte(0x01,LCD_CMD) # 000001 Clear display
             lcd_string("No color",LCD_LINE_1)
             lcd_string("Detected",LCD_LINE_2)
             time.sleep(0.5)
         except:
          p.stop()
          GPIO.cleanup()
	####################################
        lcd_string("Enter Password ",LCD_LINE_1)
        lcd_string("",LCD_LINE_2)
        inputstring = ""
        hidekey= ""
       else:
        lcd_string("Unknown Person",LCD_LINE_2)
        time.sleep(1)
        lcd_string("AGAIN",LCD_LINE_2)
        inputstring = ""
        hidekey= ""
      else:
       inputstring = inputstring +characters[3]
       hidekey = hidekey +"*"
       lcd_string(hidekey,LCD_LINE_2)
    GPIO.output(line, GPIO.LOW)
    time.sleep(0.02)



# Define delay between readings
delay = 5
lcd_init()
lcd_string("Welcome ",LCD_LINE_1)
time.sleep(1)
lcd_string("Enter Password ",LCD_LINE_1)
while 1:
   readLine(R1, ["7","8","9","/"])
   readLine(R2, ["4","5","6","*"])
   readLine(R3, ["1","2","3","-"])
   readLine(R4, ["C","0","=","#"])

