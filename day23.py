from IntcodeStepper import IntcodeStepper, REQUEST_INPUT, RECEIVED_INPUT, GAME_OVER
from collections import defaultdict

with open('day23.in') as f:
    network_prog = [int(v) for v in f.read().strip().split(',')]

NO_PACKET = object()

def boot_system(network_addr):
    system = IntcodeStepper(network_prog, patient = True)
    line = ''
    while True:
        next_result = system.next()
        if next_result == REQUEST_INPUT:
            value = system.next(network_addr)
            assert(value == RECEIVED_INPUT)
            return(system)
        elif next_result == GAME_OVER:
            print("system terminated itself")
            raise RuntimeError("Startup sequence self-terminated")
        else:
            if next_result == 10:
                line = ''
            else:
                line = line + chr(next_result)



obj_to_name = {REQUEST_INPUT:"Request input", RECEIVED_INPUT:'Received input', GAME_OVER:'Game over'}

def part1():
    N_NETWORK = 50
    network = [boot_system(i) for i in range(N_NETWORK)]
    packets = [[] for _ in range(N_NETWORK)]

    running = True
    while running:
        for this_addr, (this_prog, queue) in enumerate(zip(network, packets)):
            try:
                input_packet = queue.pop()
            except IndexError:
                input_packet = NO_PACKET

            next_result = this_prog.next()
            try:
                print(obj_to_name[next_result])
            except KeyError:
                pass

            if next_result == RECEIVED_INPUT:
                raise RuntimeError("Program should not return RECEIVED_INPUT at top level")
            if next_result == REQUEST_INPUT:
                if input_packet == NO_PACKET:
                    next_result = this_prog.next(-1)
                    assert(next_result == RECEIVED_INPUT)
                else:
                    ## Input a full packet of two values
                    next_result = this_prog.next(input_packet[0])
                    assert(next_result == RECEIVED_INPUT)
                    next_result = this_prog.next(input_packet[1])
                    assert(next_result == RECEIVED_INPUT)
                next_result = this_prog.next()
            
            if next_result == GAME_OVER:
                running = False
                break

            elif next_result != REQUEST_INPUT:
                ## Output a full packet of address + two values
                address = next_result
                packet = tuple(this_prog.next() for _ in range(2))
                print(f"Looking to send {packet} to address {address} from computer {this_addr}")
                if (address == 255):
                    print(f"Found packet {packet} going to address 255")
                    running = False
                    break
                try:
                    packets[address].append(packet)
                except IndexError:
                    print(f"Packet address invalid")
                    raise



def part2():
    N_NETWORK = 50
    network = [boot_system(i) for i in range(N_NETWORK)]
    packets = [[] for _ in range(N_NETWORK)]
    NAT = None
    last_nat_delivery_y = None

    running = True
    while running:
        who_is_waiting = []
        for this_addr, (this_prog, queue) in enumerate(zip(network, packets)):
            try:
                input_packet = queue.pop()
            except IndexError:
                input_packet = NO_PACKET

            next_result = this_prog.next()

            if next_result == RECEIVED_INPUT:
                raise RuntimeError("Program should not return RECEIVED_INPUT at top level")
            if next_result == REQUEST_INPUT:
                if input_packet == NO_PACKET:
                    next_result = this_prog.next(-1)
                    assert(next_result == RECEIVED_INPUT)
                else:
                    ## Input a full packet of two values
                    next_result = this_prog.next(input_packet[0])
                    assert(next_result == RECEIVED_INPUT)
                    next_result = this_prog.next(input_packet[1])
                    assert(next_result == RECEIVED_INPUT)
                next_result = this_prog.next()
            
            this_waiting = (input_packet == NO_PACKET) and (next_result == REQUEST_INPUT)
            who_is_waiting.append(this_waiting)

            if next_result == GAME_OVER:
                running = False
                raise ValueError("One system shut down; exiting network")
                break


            elif next_result != REQUEST_INPUT:
                ## Output a full packet of address + two values
                address = next_result
                packet = tuple(this_prog.next() for _ in range(2))
                if address == 255:
                    ## print(f"Found packet {packet} going to NAT")
                    NAT = packet
                else:
                    ## print(f"Looking to send {packet} to address {address} from computer {this_addr}")
                    try:
                        packets[address].append(packet)
                    except IndexError:
                        print(f"Packet address invalid")
                        raise

        if all(who_is_waiting):
            print(f"Sending {NAT} from NAT to computer 0")
            new_y = NAT[1]
            if new_y == last_nat_delivery_y:
                return(new_y)
            last_nat_delivery_y = new_y
            packets[0].append(NAT)


if __name__ == "__main__":
    # boot_system(1)
    # part1()
    print(part2())
