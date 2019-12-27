from IntcodeStepper import IntcodeStepper, REQUEST_INPUT, RECEIVED_INPUT, GAME_OVER
from collections import defaultdict
import re
import numpy as np
import string
from itertools import combinations

with open('day25.in') as f:
    zork_prog = [int(v) for v in f.read().strip().split(',')]

def reset_zork():
    return IntcodeStepper(zork_prog, patient = True)


room_item_lookup = {}
room_door_lookup = {}
directions = {'west': 'east', 'north':'south'}
directions = {**directions, **{v:k for k,v in directions.items()}}
undo_dir = {k[0]:v[0] for k,v in directions.items()}
direction_expand = {k[0]:k for k in directions.keys()}


interactive = False
if interactive:
    zork = reset_zork()
    display_buffer = ''
    room_description = ''
    room_description_buffer = ''
    path_stack = []
    read_room_description = True
    command = None

    while True:
        next_result = zork.next()
        while next_result == REQUEST_INPUT:
            ## Populate previous command
            if command is None or command in directions or command == 'take':
                read_room_description = False
                if "You can't go that way." in room_description_buffer or (room_description != '' and room_description in room_description_buffer):
                    ## Undo the top level of the path stack
                    path_stack.pop()
                    ## Do not update the rooms if our direction was invalid
                    pass
                else:
                    room_description = room_description_buffer
                    if len(path_stack) >= 2:
                        if path_stack[-2] == undo_dir[path_stack[-1]]:
                            path_stack = path_stack[:-2]
    
                    print(f"Current location: {''.join(path_stack)}")
                    serial_path_stack = tuple(path_stack)
                    if 'Doors here lead:' in room_description:
                        doors = room_description.split('Doors here lead:')[1].split('Command?')[0].split('Items here')[0]
                        room_door_lookup[serial_path_stack] = doors.strip().split('\n')
    
                    if serial_path_stack in room_item_lookup:
                        del room_item_lookup[serial_path_stack]
                    
                    if 'Items here:' in room_description:
                        items = room_description.split('Items here:')[1].split('Command?')[0]
                        room_item_lookup[serial_path_stack] = items.strip().split('\n')
    
            command = input("(<dir>, take, drop, inv, map, reset): ").strip()
            if command == 'reset':
                print("Received reset!")
                break
            elif command == 'map':
                print(room_description)
                for k in room_door_lookup:
                    print("".join(k).ljust(15), room_door_lookup[k])
                    if k in room_item_lookup:
                        print("items:".rjust(20), room_item_lookup[k])
                continue
            ## Collect room information if we have just moved
            elif command in directions:
                path_stack.append(command[0])
                room_description_buffer = ''
                read_room_description = True
            
            for c in command:
                ## Input a full packet of two values
                next_result = zork.next(ord(c))
                assert(next_result == RECEIVED_INPUT)
            next_result = zork.next(ord('\n'))
            assert(next_result == RECEIVED_INPUT)
            next_result = zork.next()
    
    
        if next_result == GAME_OVER:
            print("Encountered GAME OVER!")
            command = 'reset'
    
        if command == 'reset':
            print("Resetting to factory...")
            zork = reset_zork()
            display_buffer = ''
            room_description = ''
            room_description_buffer = ''
            path_stack = []
            read_room_description = True
            command = None
            continue
        
        elif next_result != REQUEST_INPUT:
            if next_result == 10:
                print(display_buffer)
                if read_room_description:
                    room_description_buffer = room_description_buffer + '\n' + display_buffer
                display_buffer = ""
            else:
                display_buffer = display_buffer + chr(next_result)




room_item_lookup = {}
room_door_lookup = {}
directions = {'west': 'east', 'north':'south'}
directions = {**directions, **{v:k for k,v in directions.items()}}
undo_dir = {k[0]:v[0] for k,v in directions.items()}
direction_expand = {k[0]:k for k in directions.keys()}

zork = reset_zork()



all_items = {
        'wwww': 'dark matter',
        'wwws': 'fixed point',
        'wwwsw':'food ration',
        'wws':'astronaut ice cream',
        'wwss':'polygon',
        'wwsse':'easter egg',
        'wwssee':'weather machine',
        'wsss':'asterisk'
}
weighing_room = 'wwsseen'


display_buffer = ""
    
command_queue = []
for location, name in all_items.items():
    command_queue += [direction_expand[l[0]] for l in location]
    command_queue += [f'take {name}']
    command_queue += [direction_expand[undo_dir[l]] for l in reversed(location)]
command_queue += [direction_expand[l[0]] for l in weighing_room]
command_queue.append('inv')

for named_item in all_items.values():
    command_queue.append(f'drop {named_item}')

for r in range(4, len(all_items)):
    this_combo = combinations(all_items.values(), r)
    for combo in this_combo:
        for elem in combo:
            command_queue.append(f'take {elem}')
        command_queue.append("north")
        for elem in combo:
            command_queue.append(f'drop {elem}')

print(command_queue)


while len(command_queue) > 0:
    next_result = zork.next()
    if next_result == REQUEST_INPUT:
        command = command_queue.pop(0)
        print(command)
        for c in command:
            ## Input a full packet of two values
            next_result = zork.next(ord(c))
            assert(next_result == RECEIVED_INPUT)
        next_result = zork.next(ord('\n'))
        assert(next_result == RECEIVED_INPUT)
        next_result = zork.next()


    if next_result == GAME_OVER:
        print("Encountered GAME OVER!")
        raise RuntimeError("Reached Game Over!")

    elif next_result != REQUEST_INPUT:
        if next_result == 10:
            print(display_buffer)
            display_buffer = ""
        else:
            display_buffer = display_buffer + chr(next_result)
    

