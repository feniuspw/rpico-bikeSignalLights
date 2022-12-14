from machine import Pin, SPI, ADC
from time import sleep

from lib import max7219

# Constants
L_ARROW_STATUS = 0
R_ARROW_STATUS = 0
BRAKE_STATUS = 0
BRIGHTNESS_STATUS = [1,5,10,15]
BRIGHTNESS_LEVEL = 0
JOYSTICK_X_AXIS_PIN = 26
JOYSTICK_Y_AXIS_PIN = 27
JOYSTICK_Z_AXIS_PIN = 22
GROVE_BUTTON_LED_PIN = 21
GROVE_BUTTON_BTN_PIN = 20

# Grove button initialization
gbtnled = Pin(GROVE_BUTTON_LED_PIN, Pin.OUT)
gbtn = Pin(GROVE_BUTTON_BTN_PIN,Pin.IN, Pin.PULL_UP)

# KY-023 Joystick Module for testing purposes
xAxis = ADC(Pin(JOYSTICK_X_AXIS_PIN))
yAxis = ADC(Pin(JOYSTICK_Y_AXIS_PIN))
SW = Pin(JOYSTICK_Z_AXIS_PIN,Pin.IN, Pin.PULL_UP)

# setup LedMatrix 4x8x8
spi = SPI(0, baudrate=10000000, polarity=1, phase=0, sck=Pin(2), mosi=Pin(3))
ss = Pin(5, Pin.OUT)
display = max7219.Matrix8x8(spi, ss, 4)
display.brightness(1)   # adjust brightness 1 to 15

# clean screen
display.fill(0)
display.show()

def adjust_brightness(brightness):
    global display, gbtnled, BRIGHTNESS_STATUS
    brightness = (brightness+1)%4 
    display.brightness(BRIGHTNESS_STATUS[brightness])
    return brightness

def toggle_brake_light():
    global BRAKE_STATUS
    BRAKE_STATUS = 0 if BRAKE_STATUS else 1
    draw_brake_light(BRAKE_STATUS)

def draw_brake_light(color):
    global display
    display.fill_rect(10,1,12,6,color)
    display.hline(11,0,10,color)
    display.hline(11,7,10,color)

def toggle_arrow(side):
    global L_ARROW_STATUS, R_ARROW_STATUS
    if side == 'l':
        L_ARROW_STATUS = 0 if L_ARROW_STATUS else 1
        draw_arrow(L_ARROW_STATUS, side)
    else:
        R_ARROW_STATUS = 0 if R_ARROW_STATUS else 1
        draw_arrow(R_ARROW_STATUS, side)

def draw_arrow(color, side):
    global display
    if side == 'l':
        r = range(0,4)
        rect_x = 4
    else:
        r = reversed(range(28,32))
        rect_x = 23
    line_size = 2
    ypos = 3
    for xpos in r:
        display.vline(xpos,ypos,line_size,color)
        line_size +=2
        ypos -=1
    display.fill_rect(rect_x,2,5,4,color)


# Main loop
while True:
    xRef = xAxis.read_u16()
    yRef = yAxis.read_u16()
    brake_button = SW.value()
    
    # grove button
    if gbtn.value():
        gbtnled.value(0)
    else:
        gbtnled.value(1)
        BRIGHTNESS_LEVEL = adjust_brightness(BRIGHTNESS_LEVEL)
        
    # Signal lights
    if yRef < 20000:
        toggle_arrow('l')
        draw_arrow(0,'r') if R_ARROW_STATUS else None
    elif yRef > 50000:
        toggle_arrow('r')
        draw_arrow(0,'l') if L_ARROW_STATUS else None
    else:
        draw_arrow(0,'l')
        draw_arrow(0,'r')
        
    # brake (released button default value is 1)
    if not brake_button:
        draw_brake_light(1)
    else:
        draw_brake_light(0)
        
    display.show()
    sleep(0.4)
