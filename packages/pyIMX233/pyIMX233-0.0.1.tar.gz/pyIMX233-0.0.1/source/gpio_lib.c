/*
 * gpio_lib.c
 *
 * Copyright 2013 LK <luv4rice@ymail.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 */


#include <ctype.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <time.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/select.h>
#include <pthread.h>
#include <unistd.h>
#include <sched.h>

#include "gpio_lib.h"

unsigned int GPIO_BASE = 0;
static volatile long int *gpio_map = NULL;

int imx233_gpio_init(void) {
    int fd;

    fd = open("/dev/mem", O_RDWR);
    if(fd < 0) {
        return SETUP_DEVMEM_FAIL;
    }

    gpio_map = (void *)mmap(0, 
        IMX233_PINCTRL_MAPSIZE, 
        PROT_READ|PROT_WRITE, 
        MAP_SHARED, 
        fd, 
        IMX233_PINCTRL_BASE);

    if(gpio_map == MAP_FAILED) {
        return SETUP_MMAP_FAIL;
    }

    GPIO_BASE = (unsigned int)gpio_map;

    close(fd);
    return SETUP_OK;
}

/*
** set input/output mode for GPIO pin
** val==0 : input, clear data output enable bit (DOE)
** val==1 : output, enable data output bit (DOE)
** return 0 on success, -1 on failure (when pin not configured as GPIO)
*/
int imx233_gpio_set_cfgpin(unsigned int pin, unsigned int val) {
    int result=0;

    if(GPIO_BASE == 0) {
        result=-1; // memory map not configure?
    } else {
        unsigned int bank = GPIO_BANK(pin);
        unsigned int num = GPIO_NUM(pin);
        unsigned int mode=val?MODE_SET:MODE_CLEAR;
        unsigned int *pio=(unsigned int *)GPIO_BASE;
        unsigned int dat=pio[GPIO_INDEX_2BIT(IMX233_OFFSET_MUXSEL,bank,num,MODE_READ)];
        unsigned int muxsel=GPIO_GET_VALUE_2BIT(num,dat);
    
        /*
        ** if muxsel==3 this is a GPIO pin, otherwise return MODE_NONE
        */
        if(muxsel==GPIO_MUXSEL_GPIO) {
            unsigned int mask=GPIO_PIN_MASK_1BIT(num);
    
            // write bit mask to _SET or _CLR register to set or clear the DOE mode
            pio[GPIO_INDEX_1BIT(IMX233_OFFSET_DOE,bank,mode)]=mask;
        } else {
           result=-1; // failed, cannot set config for none-GPIO pin
        }
    }
    return result;
}

int imx233_gpio_get_cfgpin(unsigned int pin) {
    int result;

    if(GPIO_BASE == 0)
    {
        result=-1; // memory map not configure?
    } else {
        unsigned int bank = GPIO_BANK(pin);
        unsigned int num = GPIO_NUM(pin);
        unsigned int *pio=(unsigned int *)GPIO_BASE;
        unsigned dat=pio[GPIO_INDEX_2BIT(IMX233_OFFSET_MUXSEL,bank,num,MODE_READ)];
        unsigned muxsel=GPIO_GET_VALUE_2BIT(num,dat);
    
        /*
        ** if muxsel==3 this is a GPIO pin, otherwise return MODE_NONE
        */
        if(muxsel==GPIO_MUXSEL_GPIO) {
            dat=pio[GPIO_INDEX_1BIT(IMX233_OFFSET_DOE,bank,MODE_READ)];
            result=GPIO_GET_VALUE_1BIT(num,dat); // 0=INPUT, 1=OUTPUT
        } else {
            result=GPIO_PIN_MODE_NOT_GPIO; // 2='not configured as GPIO'
        }
    }
    return result;
}
    
int imx233_gpio_output(unsigned int pin, unsigned int val) {
    int result=0;

    if(GPIO_BASE == 0)
    {
        result=-1; // memory map not configure?
    } else {
        unsigned int bank = GPIO_BANK(pin);
        unsigned int num = GPIO_NUM(pin);
        unsigned int *pio=(unsigned int *)GPIO_BASE;
        unsigned int dat=pio[GPIO_INDEX_2BIT(IMX233_OFFSET_MUXSEL,bank,num,MODE_READ)];
        unsigned int muxsel=GPIO_GET_VALUE_2BIT(num,dat);
    
        /*
        ** if muxsel==3 this is a GPIO pin, otherwise return MODE_NONE
        */
        if(muxsel==GPIO_MUXSEL_GPIO) {
            unsigned int mask=GPIO_PIN_MASK_1BIT(num);
            unsigned int mode=val?MODE_SET:MODE_CLEAR;
    
            // write bit mask to _SET or _CLR register to set or clear the I/O line
            pio[GPIO_INDEX_1BIT(IMX233_OFFSET_DOUT,bank,mode)]=mask;
        } else {
            result=-1; // failure, pin is nog GPIO
        }
    }
    return result;
}


/*
** read input pin
*/
int imx233_gpio_input(unsigned int pin) {
    int result=0;
    if(GPIO_BASE == 0)
    {
        result=-1; // memory map not configure?
    } else {
        unsigned int dat;
        unsigned int bank = GPIO_BANK(pin);
        unsigned int num = GPIO_NUM(pin);
        unsigned int *pio=(unsigned int *)GPIO_BASE;

        dat=pio[GPIO_INDEX_1BIT(IMX233_OFFSET_DIN,bank,MODE_READ)];
        result=GPIO_GET_VALUE_1BIT(num,dat);
    }
    return result;
}

/*
** unmap the previously mapped memor area
*/
void imx233_gpio_cleanup(void)
{
    if (gpio_map == NULL)
        return;

    munmap((void*)gpio_map, IMX233_PINCTRL_MAPSIZE);
}

