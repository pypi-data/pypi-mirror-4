#ifndef _GPIO_LIB_H_
#define _GPIO_LIB_H_


#define IMX233_PINCTRL_BASE    0x80018000
#define IMX233_PINCTRL_MAPSIZE     0x1000
#define IMX233_OFFSET_MUXSEL        0x100
#define IMX233_OFFSET_DOUT          0x500
#define IMX233_OFFSET_DIN           0x600
#define IMX233_OFFSET_DOE           0x700

#define GPIO_BANK(pin)	((pin) >> 5)
#define GPIO_NUM(pin)	((pin) & 0x1F)

#define GPIO_PIN_MODE_INPUT      0
#define GPIO_PIN_MODE_OUTPUT     1
#define GPIO_PIN_MODE_NOT_GPIO   2

#define LOW  0
#define HIGH 1

#define GPIO_MUXSEL_GPIO 3

#define MODE_READ   0
#define MODE_SET    1
#define MODE_CLEAR  2
#define MODE_TOGGLE 3

#define GPIO_INDEX_1BIT(offset,bank,mode) (((offset)>>2)+((bank)<<2)+((mode)&3))
#define GPIO_INDEX_2BIT(offset,bank,pin,mode) (((offset)>>2)+((bank)<<3)+(((pin)&0x10)>>2)+((mode)&3))

#define GPIO_PIN_MASK_1BIT(pin) (1<<(pin))
#define GPIO_PIN_MASK_2BIT(pin,value) (((value)&3)<<(((pin)&0xf)<<1))

#define GPIO_GET_VALUE_1BIT(pin,word) ( ( (word) >> (pin) ) & 1 )
#define GPIO_GET_VALUE_2BIT(pin,word) ( ( (word) >> (((pin) & 0xf) << 1) ) & 3 )

#define SETUP_OK            0
#define SETUP_DEVMEM_FAIL   1
#define SETUP_MALLOC_FAIL   2
#define SETUP_MMAP_FAIL     3

extern int imx233_gpio_input(unsigned int pin);
extern int imx233_gpio_init(void);
extern int imx233_gpio_set_cfgpin(unsigned int pin, unsigned int val);
extern int imx233_gpio_get_cfgpin(unsigned int pin);
extern int imx233_gpio_output(unsigned int pin, unsigned int val);
extern void imx233_gpio_cleanup(void);

extern unsigned int GPIO_BASE;
#endif
