# DE_CLI - use DE_Connecxtion to send and receive commands
# to the data engine using the DE_Connection object.
#
# Currently awaiting the MR and MW functions to allow reading and 
# writing the module SPI and I2C registers.

from DE_Connection import DE_LH
import sys


if __name__ == "__main__":
    
    test = DE_LH('')		# Open discovery and provisioning channels
    
    if not test:
        sys.exit("Could not find / open a target Data Engine")


    quit = False
    while(not quit):

        print ("--------------------")
        print ("      Format: Module Read (module/slot/address). Example: MR 0x0001 0x0005 0x0AC2")
        print ("              Module Write (module/slot/address/data). Example: MW 0x0001 0x0005 0x0AC2 0xA5")
        print ("              Yn (turn on  DevKit LED n  (0..3)")
        print ("              Xn (turn off DevKit LED n  (0..3)")
        print ("")
        print ("Commands:")
        print ("P - Send a command on the Provisioning Channel and read response (timeout if none)")
        print ("R - Read any dangling responses from Provisioning Channel (timeout if none)")
        print ("Q - Quit")
        print ("")
 
        CLI = input ("Enter Command: ")

        if CLI  =='Q':
            quit = True
            continue
            
        if CLI == 'P':
            command = input ("Enter provisioning command: ")
            test.SendChan(test.ProvChan, command)
            response = test.RecvChan(test.ProvChan)
            print ("Response: ", response)
            continue

        if CLI == 'R':
            response = test.RecvChan(test.ProvChan)
            print ("Response: ", response)
            continue
            
        print ("Unknown command: ", CLI)
        
    sys.exit("Quiting DE_CLI")
    
