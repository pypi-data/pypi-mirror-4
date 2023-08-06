This package provides class to control the GPIO on Olinuxino IMX233.
Current release does no support any peripheral functions.

Example
=======

Typical usage::
    
    #!/usr/bin/env python

    import IMX233_GPIO as GPIO

    #init module
    GPIO.init()
    
    #configure module
    GPIO.setcfg(GPIO.PIN#, GPIO.OUT)
    GPIO.setcfg(GPIO.PIN#, GPIO.IN)
        
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

    This has been developed and tested on Olinuxino-Maxi IMX233, if used on any other
    board it's advised to verify if the configuration is compatible before using this
    module.
