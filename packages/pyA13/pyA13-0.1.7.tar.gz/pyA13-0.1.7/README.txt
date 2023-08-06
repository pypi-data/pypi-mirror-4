This package provides class to control the GPIO on Olinuxino A13.
Current release does no support any peripheral functions.

Example
=======

Typical usage::
    
    #!/usr/bin/env python

    import A13_GPIO as GPIO

    #init module
    GPIO.init()
    
    #configure module
    GPIO.setcfg(GPIO.PIN#, GPIO.OUTPUT)
    GPIO.setcfg(GPIO.PIN#, GPIO.INPUT)
        
    #read the current GPIO configuration
    config = GPIO.getcfg(GPIO.PIN#)
    
    #set GPIO high
    GPIO.output(GPIO.PIN#, GPIO.HIGH)
    
    #set GPIO low
    GPIO.output(GPIO.PIN#, GPIO.LOW)
    
    #read input
    state = GPIO.input(GPIO.PIN#)
    
    #cleanup 
    GPIO.cleanup()
    

Warning
=======

    Before using this tool it is HIGHLY RECOMENDED to check Olinuxino 
    A13 schematic. If you're using the "big" A13 (not MICRO) notice that 
    some pins are multiplexed with the RTC and the NAND Flash. One workaround is 
    to clear CE and use the rest of the pins.
    

Thanks also to: bianchina3

