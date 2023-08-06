This package provides class to control the GPIO on Olinuxino A10S.
Current release does no support any peripheral functions.

Example
=======

Typical usage::
    
    #!/usr/bin/env python

    import A10S_GPIO as GPIO

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
    A10S schematic. 

