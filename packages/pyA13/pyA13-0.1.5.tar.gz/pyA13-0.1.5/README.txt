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
    GPIO.setcfg(NUMBER, VALUE)
        
    #read the current GPIO configuration
    config = GPIO.getcfg(NUMBER)
    
    #set GPIO high
    GPIO.output(NUMBER, HIGH)
    
    #set GPIO low
    GPIO.output(NUMBER, LOW)
    
    #cleanup 
    GPIO.cleanup()
    
Where:
    
    * NUMBER - is the GPIO number (0, 1, 2, 3 ...)
    
    * VALUE - can be:
    
        * INPUT
        * OUTPUT
        * PER (Not fully working)


Thanks also to: bianchina3

