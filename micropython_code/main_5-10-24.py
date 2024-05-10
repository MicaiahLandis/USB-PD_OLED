from machine import Pin, ADC, SoftI2C, lightsleep
from time import sleep
import ssd1306
import math

vdiv = ADC(Pin(26))
temp = ADC(4)
disp = Pin(16, Pin.OUT)
disp.value(1)

# dispay setup
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
display = ssd1306.SSD1306_I2C(128, 32, i2c)

R1 = 10000
R2 = 2200



##############

def main(volt, temp):
    display.fill(0)
    display.text(temp, 45, 20)
    #display.select_font('digits-30')
    display.text(volt, 45, 10)
    
# Battery symbol
def battery(volt):
    
    max_v = 10 # Maximum Voltage - Battery Max Voltage
    min_v = 3.3 # Minimum Voltage - Battery Min Voltage
    max_h = 25 # Rectangle height
    
    height = int(( (volt-min_v) / (max_v-min_v) )*max_h) # Ratio for voltage
    b_y = 32 - height
    b_h = height

    display.rect(0, 7, 10, max_h, 1) # Main Battery Rectangle (x, y, b, h, color)
    display.fill_rect(2, 4, 6, 4, 1) # Top of Battery image
    display.fill_rect(0, b_y, 10, b_h, 1) # Filled Zone of battery based on battery voltage

while True:

    # Get voltage value
    value = vdiv.read_u16() # read value, 0-65535 across voltage range 0.0v - 3.3v
    value += vdiv.read_u16()
    value += vdiv.read_u16()
    value += vdiv.read_u16()
    value += vdiv.read_u16()
    value = value/5 #averages 5 values for better accuracy
  
    volts = (value/65535)*3.3 # Ratio for conversion
  
    B_v = volts * ((R1+R2)/R2) # Voltage Divider
    B_v = round(B_v,2) # Rounds to two decimals for simpler view
    volt_o = str(B_v) + " V" 
    ###############
    # temperature
    t = temp.read_u16() * (3.3/(65535))
    t = round((27 - (t - 0.706)/0.001721), 2)
    t = str(t) + ' C'
    ###############
    
    # if V is less than 3.3 the display turns off to save power.
    # This will be used with current to go into a sleep mode
    # goal is to put entire rp2040 into a sleep mode
    if B_v < 3.0:
        print("turning off...")
        disp.value(0) # Turns off display
        lightsleep(5000) # sleeps rp2040 for x miliseconds
    else: # This part of the loop is for all scenarios when there is current draw

        if disp.value() == 1: # Reads if the display is on
            print("staying on...")
            main(volt_o, t) # Displays Voltage(Change to Wattage) & Temperature (Probably will remove this)
            battery(B_v) # Builds Battery image based on battery voltage
        elif disp.value() == 0: # Reads if the display is off so that it only resets if it was off. This avoids a flash
            print("turning on...")
            disp.value(1) # Turns on display after being off
            sleep(.1) # gives time for display to turn on
     
            # dispay setup
            i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
            display = ssd1306.SSD1306_I2C(128, 32, i2c)
            
            main(volt_o, t) # Displays Voltage(Change to Wattage) & Temperature (Probably will remove this)
            battery(B_v) # Builds Battery image based on battery voltage
            
        display.show() # Shows all info after everything has been written
        
    sleep(1) # Changes speed of entire loop
    
###########################
  
# Once current sensor exists the current can be the only sensor in the main loop
# all others can be in specific functions (maybe this would save power if sleep
# mode does not exist?)