ip_address = 'localhost' # Enter your IP Address here
project_identifier = 'P3B' # Enter the project identifier i.e. P3A or P3B

# SERVO TABLE CONFIGURATION
short_tower_angle = 315 # enter the value in degrees for the identification tower 
tall_tower_angle = 0 # enter the value in degrees for the classification tower
drop_tube_angle = 180 # enter the value in degrees for the drop tube. clockwise rotation from zero degrees

# QBOT CONFIGURATION
bot_camera_angle = -21.5

# BIN CONFIGURATION
# Configuration for the colors for the bins and the lines leading to those bins.
# Note: The line leading up to the bin will be the same color as the bin 

bin1_offset = 0.15 # offset in meters
bin1_color = [1,0,0] # e.g. [1,0,0] for red
bin1_metallic = False

bin2_offset = 0.15
bin2_color = [0,1,0]
bin2_metallic = False

bin3_offset = 0.15
bin3_color = [0,0,1]
bin3_metallic = False

bin4_offset = 0.15
bin4_color = [0,0,0]
bin4_metallic = False
#--------------------------------------------------------------------------------
import sys
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
if project_identifier == 'P3A':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    configuration_information = [table_configuration, None] # Configuring just the table
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
else:
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    bin_configuration = [[bin1_offset,bin2_offset,bin3_offset,bin4_offset],[bin1_color,bin2_color,bin3_color,bin4_color],[bin1_metallic,bin2_metallic, bin3_metallic,bin4_metallic]]
    configuration_information = [table_configuration, bin_configuration]
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    bot = qbot(0.1,ip_address,QLabs,project_identifier,hardware)
#--------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------

import random
import time

def spawn(): 
    id_list = [1,2,3,4,5,6] 
    random.shuffle(id_list)

    container_attributes = table.dispense_container(2, True) 
    return container_attributes

def load(count):
    pick_up_coords = [0.644, 0.0, 0.273] 
    drop_off_coords = [[0.02, -0.555, 0.596], [-0.055,-0.59, 0.55], [0.12, -0.60, 0.55]]

    arm.move_arm(*pick_up_coords)
    time.sleep(2)
    arm.control_gripper(35)
    time.sleep(2)
    arm.move_arm(*drop_off_coords[count])
    time.sleep(2)
    arm.control_gripper(-30)
    time.sleep(2)
    arm.home()

def spawn_n_load():
    count = 0
    weight = 0
    main_container = spawn()
    while True:
        if count == 0:
            load(count)
        else:
            if main_container[2] == new_container[2] and count < 3 and weight <=90:
                load(count)
            else:
                break
            
        count += 1
        new_container = spawn()
    
    return main_container

def transfer(bin_id):  
    bot.activate_line_following_sensor() 
    bot.activate_color_sensor() 
    bot.activate_ultrasonic_sensor() 
  
    current_bin = 0
    line_lost = False  
    while current_bin != bin_id:  

        if bot.line_following_sensors() == [1, 1]:  
            bot.stop()
            bot.set_wheel_speed([0.05,0.05])  
        elif bot.line_following_sensors() == [0, 1]:
            bot.stop()
            bot.set_wheel_speed([0.03, 0.01])
        elif bot.line_following_sensors() == [1, 0]:
            bot.stop()
            bot.set_wheel_speed ([0.01, 0.03]) 

        current_bin_reading = bot.read_color_sensor()[0]
        current_bin_distance = bot.read_ultrasonic_sensor()
        if current_bin_distance < 0.1: 
            if current_bin_reading == [1,0,0]: 
                current_bin = 1 
            elif current_bin_reading == [0,1,0]: 
                current_bin = 2 
            elif current_bin_reading == [0,0,1]: 
                current_bin = 3 
            elif current_bin_reading == [0,0,0]: 
                current_bin = 4
    bot.forward_time(2)
    bot.stop() 
    bot.deactivate_color_sensor() 
    bot.deactivate_ultrasonic_sensor() 

def deposit():
    bot.activate_stepper_motor()
    bot.rotate_hopper(50)
    time.sleep(2)
    bot.deactivate_stepper_motor()

def return_home():
    bot.activate_line_following_sensor()
    
    while not (1.46 <= bot.position()[0] <= 1.49) or not(-0.2 <= bot.position()[1] <= 0):
        print(bot.position())
        if bot.line_following_sensors() == [1, 1]:  
            bot.stop()
            bot.set_wheel_speed([0.05,0.05])  
        elif bot.line_following_sensors() == [0, 1]:
            bot.stop()
            bot.set_wheel_speed([0.03, 0.01])
        elif bot.line_following_sensors() == [1, 0]:
            bot.stop()
            bot.set_wheel_speed ([0.01, 0.03]) 

    bot.stop()
    bot.deactivate_line_following_sensor()

def main():
    properties = spawn_n_load()
    transfer(int(properties[2][-1])) 
    deposit() 
    return_home()

# main()

#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
    

    

