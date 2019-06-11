from microbit import *
import random
import radio

#
# Microbit-Dice
#
# Shake to roll the dice.
# Images for the 6 sides of a dice are shown as the dice rolls.
# The dice can only roll onto neighbouring sides - so can't jump
# from one side to the side opposite in one step.
# The time taken and number of sides that the dice rolls over
# before setting on the final value varies randomly.
#
# Dice ID can be adjusted by pressing the A & B buttons.

display.show('-')
radio.config(channel=79)
radio.on()
dice_value = 0
sequence = 0
MIN_ID = 1
MAX_ID = 9
my_id = 1

side1 = Image("00000:"
              "00000:"
              "00900:"
              "00000:"
              "00000")

side2 = Image("90000:"
              "00000:"
              "00000:"
              "00000:"
              "00009")

side3 = Image("90000:"
              "00000:"
              "00900:"
              "00000:"
              "00009")

side4 = Image("90009:"
              "00000:"
              "00000:"
              "00000:"
              "90009")

side5 = Image("90009:"
              "00000:"
              "00900:"
              "00000:"
              "90009")

side6 = Image("90009:"
              "00000:"
              "90009:"
              "00000:"
              "90009")

rx    = Image("90009:"
              "08000:"
              "00779:"
              "08000:"
              "90009")

all_sides = [side1, side2, side3, side4, side5, side6]
# some turns during rolling are not allowed - i.e. you can't go from one side to the opposite and you can't stay the same.
# Hence once we have an initial value we only have 4 options

# Function to transmit the dice data:
#  ID, Sequence, Value
def send_dice(id, seq, msg):
    id_bytes = id.to_bytes(1, 'little')
    seq_bytes = seq.to_bytes(1, 'little')
    msg_bytes = msg.to_bytes(1, 'little')
    raw_bytes = (id_bytes + seq_bytes + msg_bytes)
    radio.send_bytes(raw_bytes)

# Main loop
while True:
    # Adjust the Dice ID using the A & B buttons
    if button_a.was_pressed():
        my_id = my_id + 1
        if (MAX_ID < my_id):
            my_id = MAX_ID
        display.show(my_id)
        sleep(1000)
    if button_b.was_pressed():
        my_id = my_id - 1
        if (MIN_ID > my_id):
            my_id = MIN_ID
        display.show(my_id)
        sleep(1000)

    # If the dice is held face down it behaves as a receiver
    # TODO - split this off as a seperate version of code...
    if accelerometer.is_gesture('face down'):
        # Read any incoming messages.
        dice_value = 0
        display.clear()
        display.show(rx)
        details = radio.receive_full()
        if details:
            msg, rssi, timestamp = details
            uart.write(msg)
            #rx_id = msg[0]
            #rx_seq = msg[1]
            #rx_dice = msg[2]

    # Shake the Dice to start rolling...
    if accelerometer.is_gesture('shake'):
        display.clear()
        while accelerometer.is_gesture('shake'):
            sleep(10)
        sleep(300)
        # Now that shaking has stopped we are rolling...
        turns = random.randint(4,8)                         # number of sides to roll over
        dice_value = random.randint(1,6)                    # initial dice value to show
        display.show(all_sides[dice_value-1])
        # Loop over the number of sides to roll over...
        for turn in range(turns):
            sleep(200+ 50*turn + random.randint(0,100))     # time that each side is shown increases as the rolling slows down, with a random element
            dice_value = dice_value + random.randint(1, 4)  # random change in dice value - i.e. which way it rolls
            dice_value = 1 + ((dice_value-1) % 6)           # wrap values back onto the allowed range 1-6
            display.show(all_sides[dice_value-1])
        # Dice has finished rolling so now send the final value by radio
        sequence = sequence + 1                             # increase sequence number to identify this as a new value
        send_dice(my_id, sequence, dice_value)
        sleep(1000)

    # repeat dice radio message transmission at least once - will continue until rolled again
    if 0 < dice_value:
        send_dice(my_id, sequence, dice_value)
        sleep(200)                                          # sleep to limit rate at which messages are sent
    sleep(10)