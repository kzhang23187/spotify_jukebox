import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import signal

continue_reading = True

#Capture SIGINT for cleanup when script is aborted
def end_read(signal, frame):
    global continue_reading
    print("Ctrl+c captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

signal.signal(signal.SIGINT, end_read)

reader = MFRC522()

while (continue_reading):
    #Scan for cards
    (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)

    if status == reader.MI_OK:
        print("Card detected")
        
    # Get the UID of the card
    (status, uid) = reader.MFRC522_Anticoll()

    if status == reader.MI_OK:

        reader.MFRC522_SelectTag(uid)

        #Check authenticated
        if status == reader.MI_OK:
            data = []
            text_read = ''
            #[6,7,8,9,10,11,12]
            for block_num in [6,10,14]:
                block = reader.MFRC522_Read(block_num) 
                if block:
                    data += block
            if data:
                text_read = ''
                for i in data:
                    if chr(i) == 'þ':
                        break
                    text_read = text_read + chr(i)
                    #text_read = ''.join(chr(i) for i in data)
                 
            print(text_read[1:])

            reader.MFRC522_StopCrypto1()
        else:
            print("Authentication error")

    

