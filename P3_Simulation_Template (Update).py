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

bin1_offset = 0.20 # offset in meters
bin1_color = [1,0,0] # e.g. [1,0,0] for red
bin1_metallic = False

bin2_offset = 0.20
bin2_color = [0,1,0]
bin2_metallic = False

bin3_offset = 0.20
bin3_color = [0,0,1]
bin3_metallic = False

bin4_offset = 0.20
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

#This function spawns a container onto the servo table
def spawn(): 
    id_list = [1,2,3,4,5,6] 
    random.shuffle(id_list)
    container_attributes = table.dispense_container(id_list[0], True) 
    return container_attributes

#This function takes in the number of containers currently on the Qbot as parameter and loads the remaining container to the appropriate position
def load(count):
    pick_up_coords = [0.644, 0.0, 0.273] 
    drop_off_coords = [[0.02, -0.59, 0.590], [0.02, -0.50, 0.596], [0.02, -0.43, 0.596]] #The three drop off coordinates based on the number of containers on the Qbot

    arm.move_arm(*pick_up_coords)
    time.sleep(2)
    arm.control_gripper(35)
    time.sleep(2)
    arm.move_arm(*drop_off_coords[count])
    time.sleep(2)
    arm.control_gripper(-30)
    time.sleep(2)
    arm.home()

'''This function combines the spawn() and load() function to create an integrated system that loads the appropriate type
and number of containers onto the Qbot based on the loading criteria'''
def spawn_n_load(count, container_on_table):
    weight = 0
    main_container = spawn()
    if container_on_table != None and count > 0:
        new_container = main_container
        main_container = container_on_table 
        weight += container_on_table[1]
    while True:
        if count == 0:
            load(count)
            weight += main_container[1]
        else:
            if main_container[2] == new_container[2] and count < 3 and weight <=90:
                load(count)
                weight += new_container[1]
            else:
                break
            
        count += 1
        new_container = spawn()
    
    return main_container, new_container

#This function has main task of following the yellow line and returns the last direction the yellow line was in i.e. either to the left or right of the qbot
def follow_line(last_direction):
    if bot.line_following_sensors() == [1, 1]:  
        bot.stop()
        bot.set_wheel_speed([0.05, 0.05])
    elif bot.line_following_sensors() == [0, 1]:
        bot.stop()
        bot.set_wheel_speed([0.03, 0.01])
        last_direction = 'r'
    elif bot.line_following_sensors() == [1, 0]:
        bot.stop()
        bot.set_wheel_speed ([0.01, 0.03])
        last_direction = 'l'
    else:
        if last_direction == 'l':
            while bot.line_following_sensors() != [1,1] and bot.line_following_sensors() != [1,0]:
                bot.set_wheel_speed([0.01, 0.03])
        else:
            while bot.line_following_sensors() != [1,1] and bot.line_following_sensors() != [0,1]:
                bot.set_wheel_speed([0.03, 0.01])
    return last_direction
        

def transfer(bin_id):  
    bot.activate_line_following_sensor() 
    bot.activate_color_sensor() 
    bot.activate_ultrasonic_sensor()
    last_direction = ''
    current_bin = 0
    iteration = 1
    #The while loop runs until the bot reaches the correct bin i.e. current_bin == bin_id
    while current_bin != bin_id:
        time.sleep(1)
        last_direction = follow_line(last_direction)
        print(iteration)
        try:
            current_bin_reading = bot.read_color_sensor()[0]
            print('Bin color reading:', current_bin_reading)
        except:
            time.sleep(0.1)
            continue
        try:
            current_bin_distance = bot.read_ultrasonic_sensor()
            print('Ultrasonic sensor distance reading:', current_bin_distance)
        except:
            time.sleep(0.1)
            continue
        #Color readings are only taken for objects within 0.1 m of the Qbot so that it does mistake another coloured object for a bin
        if current_bin_distance != None and current_bin_distance < 0.3:
            #bin id of the bin near the Qbot is determined through the colour of the bin
            if current_bin_reading[0] == 1: 
                current_bin = 1 
            elif current_bin_reading[1] == 1: 
                current_bin = 2 
            elif current_bin_reading[2] === 1: 
                current_bin = 3 
            elif current_bin_reading == [0,0,0]: 
                current_bin = 4
        iteration += 1
                
    bot.forward_time(0.5)
    bot.stop() 
    bot.deactivate_color_sensor() 
    bot.deactivate_ultrasonic_sensor() 

#This function user the stepper motor to deposit the containers once the Qbot has reached the correct bin 
def deposit():
    bot.activate_stepper_motor()
    for i in range(5):
        bot.rotate_hopper(10 + 10*i)
        time.sleep(1)
    bot.deactivate_stepper_motor()

    
def return_home():
    bot.activate_line_following_sensor()
    last_direction = ''
    #The while loop keeps running until the bot reaches its home position whithin an acceptable uncertainty of coordinates
    while not (1.465 <= bot.position()[0] <= 1.49) or not(-0.2 <= bot.position()[1] <= 0.2):
       last_direction = follow_line(last_direction)

    bot.stop()
    bot.rotate(-5) #Minor adjustment in bot position to make sure the contianer loaded next does not fall
    time.sleep(1)
    bot.deactivate_line_following_sensor()

def main():
    user_input = 'y'
    servo_table_empty = True
    container_count = 0
    iteration = 0
    #The program runs until the user decided to quit
    while user_input == 'y':
        if iteration == 0:
            properties, container_on_table = spawn_n_load(0, None) #The properties of the container type currently loaded on the Qbot and the container left on the servo table are saved for later use
        else:
            load(0)
            properties, container_on_table = spawn_n_load(1, container_on_table)
        transfer(int(properties[2][-1]))#the transfer function is called with the bin_id passed along as an integer 
        deposit() 
        return_home()
        user_input = input('Do you wish to run another iteration?(y/n)')#Ask the user if they wish to continue
        iteration = 1
    print('Thank you for recycling')

main()

#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
    

    

