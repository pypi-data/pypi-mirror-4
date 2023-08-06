/*
 * pyIMX233.c
 *
 * Copyright 2013 LH <luv4rice@ymail.com>
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


#include "Python.h"
#include "gpio_lib.h"


static PyObject *SetupException;
static PyObject *OutputException;
static PyObject *InputException;
static PyObject *inp;
static PyObject *out;
static PyObject *per;
static PyObject *high;
static PyObject *low;

#define PIN0 0
#define PIN1 1
#define PIN2 2
#define PIN3 3
#define PIN4 4
#define PIN5 5
#define PIN6 6
#define PIN7 7

#define PIN16 16
#define PIN17 17

#define PIN19 19
#define PIN20 20

#define PIN23 23
#define PIN24 24
#define PIN25 25

#define PIN30 30
#define PIN31 31

#define PIN32 32
#define PIN33 33
#define PIN34 34
#define PIN35 35
#define PIN36 36
#define PIN37 37
#define PIN38 38
#define PIN39 39

#define PIN50 50
#define PIN51 51
#define PIN52 52
#define PIN53 53
#define PIN54 54
#define PIN55 55
#define PIN56 56
#define PIN57 57
#define PIN58 58
#define PIN59 59
#define PIN60 60

#define PIN64 64
#define PIN65 65
#define PIN66 66
#define PIN67 67
#define PIN68 68
#define PIN69 69
#define PIN70 70

#define PIN73 73
#define PIN74 74
#define PIN75 75
#define PIN76 76
#define PIN77 77
#define PIN78 78
#define PIN79 79
#define PIN80 80
#define PIN81 81
#define PIN82 82
#define PIN83 83
#define PIN84 84

#define PIN86 86
#define PIN87 87
#define PIN88 88
#define PIN89 89

#define PIN91 91
#define PIN92 92
#define PIN93 93
#define PIN94 94
#define PIN95 95

static int module_setup(void) {
    int result;

    result = imx233_gpio_init();
    if(result == SETUP_DEVMEM_FAIL) {
        PyErr_SetString(SetupException, "No access to /dev/mem. Try running as root!");
        return SETUP_DEVMEM_FAIL;
    }
    else if(result == SETUP_MALLOC_FAIL) {
        PyErr_NoMemory();
        return SETUP_MALLOC_FAIL;
    }
    else if(result == SETUP_MMAP_FAIL) {
        PyErr_SetString(SetupException, "Mmap failed on module import");
        return SETUP_MMAP_FAIL;
    }
    else {
        return SETUP_OK;
    }

    return SETUP_OK;
}


static PyObject* py_output(PyObject* self, PyObject* args) {
    int gpio;
    int value;

    if(!PyArg_ParseTuple(args, "ii", &gpio, &value))
        return NULL;

    if(value != 0 && value != 1) {
        PyErr_SetString(OutputException, "Invalid output state");
        return NULL;
    }

    if(imx233_gpio_get_cfgpin(gpio) != GPIO_PIN_MODE_OUTPUT) {
        PyErr_SetString(OutputException, "GPIO pin is not configured as output");
        return NULL;
    }
    imx233_gpio_output(gpio, value);

    Py_RETURN_NONE;
}

static PyObject* py_input(PyObject* self, PyObject* args) {
    int gpio;
    int result;

    if(!PyArg_ParseTuple(args, "i", &gpio))
        return NULL;

    if(imx233_gpio_get_cfgpin(gpio) != GPIO_PIN_MODE_INPUT) {
        PyErr_SetString(InputException, "GPIO is not configured as input");
        return NULL;
    }
    result = imx233_gpio_input(gpio);

    if(result == -1) {
        PyErr_SetString(InputException, "Reading pin failed");
        return NULL;
    }


    return Py_BuildValue("i", result);
}

static PyObject* py_setcfg(PyObject* self, PyObject* args) {
    int gpio;
    int direction;

    if(!PyArg_ParseTuple(args, "ii", &gpio, &direction))
        return NULL;

    if(direction != 0 && direction != 1 && direction != 2) {
        PyErr_SetString(SetupException, "Invalid direction");
        return NULL;
    }
    imx233_gpio_set_cfgpin(gpio, direction);

    Py_RETURN_NONE;
}

static PyObject* py_getcfg(PyObject* self, PyObject* args) {
    int gpio;
    int result;


    if(!PyArg_ParseTuple(args, "i", &gpio))
        return NULL;

    result = imx233_gpio_get_cfgpin(gpio);


    return Py_BuildValue("i", result);


}
static PyObject* py_init(PyObject* self, PyObject* args) {

    module_setup();

    Py_RETURN_NONE;
}
static PyObject* py_cleanup(PyObject* self, PyObject* args) {

    imx233_gpio_cleanup();
    Py_RETURN_NONE;
}


PyMethodDef module_methods[] = {
    {"init", py_init, METH_NOARGS, "Initialize module"},
    {"cleanup", py_cleanup, METH_NOARGS, "munmap /dev/map."},
    {"setcfg", py_setcfg, METH_VARARGS, "Set direction."},
    {"getcfg", py_getcfg, METH_VARARGS, "Get direction."},
    {"output", py_output, METH_VARARGS, "Set output state"},
    {"input", py_input, METH_VARARGS, "Get input state"},
    {NULL, NULL, 0, NULL}
};
#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    "IMX233 module",
    NULL,
    -1,
    module_methods
};
#endif
PyMODINIT_FUNC initIMX233_GPIO(void) {
    PyObject* module = NULL;


#if PY_MAJOR_VERSION >= 3
    module = PyModule_Create(&module_methods);
#else
    module = Py_InitModule("IMX233_GPIO", module_methods);
#endif


    if(module == NULL)
#if PY_MAJOR_VERSION >= 3
        return module;
#else
        return;
#endif

    SetupException = PyErr_NewException("PyIMX233.SetupException", NULL, NULL);
    PyModule_AddObject(module, "SetupException", SetupException);
    OutputException = PyErr_NewException("PyIMX233.OutputException", NULL, NULL);
    PyModule_AddObject(module, "OutputException", OutputException);
    InputException = PyErr_NewException("PyIMX233.InputException", NULL, NULL);
    PyModule_AddObject(module, "InputException", InputException);

    high = Py_BuildValue("i", HIGH);
    PyModule_AddObject(module, "HIGH", high);

    low = Py_BuildValue("i", LOW);
    PyModule_AddObject(module, "LOW", low);

    inp = Py_BuildValue("i", GPIO_PIN_MODE_INPUT);
    PyModule_AddObject(module, "INP", inp);

    out = Py_BuildValue("i", GPIO_PIN_MODE_OUTPUT);
    PyModule_AddObject(module, "OUT", out);

    per = Py_BuildValue("i", GPIO_PIN_MODE_NOT_GPIO);
    PyModule_AddObject(module, "PER", per);

    PyModule_AddObject(module, "PIN0", Py_BuildValue("i", PIN0));
    PyModule_AddObject(module, "PIN1", Py_BuildValue("i", PIN1));
    PyModule_AddObject(module, "PIN2", Py_BuildValue("i", PIN2));
    PyModule_AddObject(module, "PIN3", Py_BuildValue("i", PIN3));
    PyModule_AddObject(module, "PIN4", Py_BuildValue("i", PIN4));
    PyModule_AddObject(module, "PIN5", Py_BuildValue("i", PIN5));
    PyModule_AddObject(module, "PIN6", Py_BuildValue("i", PIN6));
    PyModule_AddObject(module, "PIN7", Py_BuildValue("i", PIN7));
    PyModule_AddObject(module, "PIN16", Py_BuildValue("i", PIN16));
    PyModule_AddObject(module, "PIN17", Py_BuildValue("i", PIN17));
    PyModule_AddObject(module, "PIN19", Py_BuildValue("i", PIN19));
    PyModule_AddObject(module, "PIN20", Py_BuildValue("i", PIN20));
    PyModule_AddObject(module, "PIN23", Py_BuildValue("i", PIN23));
    PyModule_AddObject(module, "PIN24", Py_BuildValue("i", PIN24));
    PyModule_AddObject(module, "PIN25", Py_BuildValue("i", PIN25));
    PyModule_AddObject(module, "PIN30", Py_BuildValue("i", PIN30));
    PyModule_AddObject(module, "PIN31", Py_BuildValue("i", PIN31));
    PyModule_AddObject(module, "PIN32", Py_BuildValue("i", PIN32));
    PyModule_AddObject(module, "PIN33", Py_BuildValue("i", PIN33));
    PyModule_AddObject(module, "PIN34", Py_BuildValue("i", PIN34));
    PyModule_AddObject(module, "PIN35", Py_BuildValue("i", PIN35));
    PyModule_AddObject(module, "PIN36", Py_BuildValue("i", PIN36));
    PyModule_AddObject(module, "PIN37", Py_BuildValue("i", PIN37));
    PyModule_AddObject(module, "PIN38", Py_BuildValue("i", PIN38));
    PyModule_AddObject(module, "PIN39", Py_BuildValue("i", PIN39));
    PyModule_AddObject(module, "PIN50", Py_BuildValue("i", PIN50));
    PyModule_AddObject(module, "PIN51", Py_BuildValue("i", PIN51));
    PyModule_AddObject(module, "PIN52", Py_BuildValue("i", PIN52));
    PyModule_AddObject(module, "PIN53", Py_BuildValue("i", PIN53));
    PyModule_AddObject(module, "PIN54", Py_BuildValue("i", PIN54));
    PyModule_AddObject(module, "PIN55", Py_BuildValue("i", PIN55));
    PyModule_AddObject(module, "PIN56", Py_BuildValue("i", PIN56));
    PyModule_AddObject(module, "PIN57", Py_BuildValue("i", PIN57));
    PyModule_AddObject(module, "PIN58", Py_BuildValue("i", PIN58));
    PyModule_AddObject(module, "PIN59", Py_BuildValue("i", PIN59));
    PyModule_AddObject(module, "PIN60", Py_BuildValue("i", PIN60));
    PyModule_AddObject(module, "PIN64", Py_BuildValue("i", PIN64));
    PyModule_AddObject(module, "PIN65", Py_BuildValue("i", PIN65));
    PyModule_AddObject(module, "PIN66", Py_BuildValue("i", PIN66));
    PyModule_AddObject(module, "PIN67", Py_BuildValue("i", PIN67));
    PyModule_AddObject(module, "PIN68", Py_BuildValue("i", PIN68));
    PyModule_AddObject(module, "PIN69", Py_BuildValue("i", PIN69));
    PyModule_AddObject(module, "PIN70", Py_BuildValue("i", PIN70));
    PyModule_AddObject(module, "PIN73", Py_BuildValue("i", PIN73));
    PyModule_AddObject(module, "PIN74", Py_BuildValue("i", PIN74));
    PyModule_AddObject(module, "PIN75", Py_BuildValue("i", PIN75));
    PyModule_AddObject(module, "PIN76", Py_BuildValue("i", PIN76));
    PyModule_AddObject(module, "PIN77", Py_BuildValue("i", PIN77));
    PyModule_AddObject(module, "PIN78", Py_BuildValue("i", PIN78));
    PyModule_AddObject(module, "PIN79", Py_BuildValue("i", PIN79));
    PyModule_AddObject(module, "PIN80", Py_BuildValue("i", PIN80));
    PyModule_AddObject(module, "PIN81", Py_BuildValue("i", PIN81));
    PyModule_AddObject(module, "PIN82", Py_BuildValue("i", PIN82));
    PyModule_AddObject(module, "PIN83", Py_BuildValue("i", PIN83));
    PyModule_AddObject(module, "PIN84", Py_BuildValue("i", PIN84));
    PyModule_AddObject(module, "PIN86", Py_BuildValue("i", PIN86));
    PyModule_AddObject(module, "PIN87", Py_BuildValue("i", PIN87));
    PyModule_AddObject(module, "PIN88", Py_BuildValue("i", PIN88));
    PyModule_AddObject(module, "PIN89", Py_BuildValue("i", PIN89));
    PyModule_AddObject(module, "PIN91", Py_BuildValue("i", PIN91));
    PyModule_AddObject(module, "PIN92", Py_BuildValue("i", PIN92));
    PyModule_AddObject(module, "PIN93", Py_BuildValue("i", PIN93));
    PyModule_AddObject(module, "PIN94", Py_BuildValue("i", PIN94));
    PyModule_AddObject(module, "PIN95", Py_BuildValue("i", PIN95));

    if(Py_AtExit(imx233_gpio_cleanup) != 0){
        
        imx233_gpio_cleanup();
        
#if PY_MAJOR_VERSION >= 3
        return NULL;
#else
        return;
#endif
    }



}

