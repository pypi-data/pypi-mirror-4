/*
 * pyA13.c
 *
 * Copyright 2013 Stefan Mavrodiev <support@olimex.com>
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

//GPIO 1
#define PIN40	SUNXI_GPG(9)
#define PIN41	SUNXI_GPG(10)
#define PIN10	SUNXI_GPB(15)
#define PIN11	SUNXI_GPB(16)
#define PIN42	SUNXI_GPB(5)
#define PIN43	SUNXI_GPB(6)
#define PIN44	SUNXI_GPB(7)
#define PIN45	SUNXI_GPB(8)


//GPIO 2
#define PIN4		SUNXI_GPB(0)
#define PIN5		SUNXI_GPB(1)
#define PIN6		SUNXI_GPB(2)
#define PIN7		SUNXI_GPB(3)
#define PIN8		SUNXI_GPB(4)
#define PIN9		SUNXI_GPC(17)
#define PIN12	SUNXI_GPC(0)
#define PIN13	SUNXI_GPC(1)
#define PIN14	SUNXI_GPC(2)
#define PIN15	SUNXI_GPC(3)
#define PIN16	SUNXI_GPC(4)
#define PIN17	SUNXI_GPC(5)
#define PIN18	SUNXI_GPC(6)
#define PIN19	SUNXI_GPC(7)
#define PIN20	SUNXI_GPC(8)
#define PIN21	SUNXI_GPC(9)
#define PIN22	SUNXI_GPC(10)
#define PIN23	SUNXI_GPC(11)
#define PIN24	SUNXI_GPC(12)
#define PIN25	SUNXI_GPC(13)
#define PIN26	SUNXI_GPC(14)
#define PIN27	SUNXI_GPC(15)
#define PIN28	SUNXI_GPC(16)
#define PIN29	SUNXI_GPE(4)
#define PIN30	SUNXI_GPE(5)
#define PIN31	SUNXI_GPE(6)
#define PIN32	SUNXI_GPE(7)
#define PIN33	SUNXI_GPE(8)
#define PIN34	SUNXI_GPE(9)
#define PIN35	SUNXI_GPE(10)
#define PIN36	SUNXI_GPE(11)
#define PIN37	SUNXI_GPE(3)
#define PIN38	SUNXI_GPE(2)
#define PIN39	SUNXI_GPE(1)

//GPIO 3
#define PIN3	SUNXI_GPE(0)

static int module_setup(void) {
    int result;

    result = sunxi_gpio_init();
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

    if(sunxi_gpio_get_cfgpin(gpio) != SUNXI_GPIO_OUTPUT) {
        PyErr_SetString(OutputException, "GPIO is no an output");
        return NULL;
    }
    sunxi_gpio_output(gpio, value);

    Py_RETURN_NONE;
}
static PyObject* py_input(PyObject* self, PyObject* args) {
    int gpio;
    int result;

    if(!PyArg_ParseTuple(args, "i", &gpio))
        return NULL;

    if(sunxi_gpio_get_cfgpin(gpio) != SUNXI_GPIO_INPUT) {
        PyErr_SetString(InputException, "GPIO is not an input");
        return NULL;
    }
    result = sunxi_gpio_input(gpio);

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
    sunxi_gpio_set_cfgpin(gpio, direction);

    Py_RETURN_NONE;
}
static PyObject* py_getcfg(PyObject* self, PyObject* args) {
    int gpio;
    int result;


    if(!PyArg_ParseTuple(args, "i", &gpio))
        return NULL;

    result = sunxi_gpio_get_cfgpin(gpio);


    return Py_BuildValue("i", result);


}
static PyObject* py_init(PyObject* self, PyObject* args) {

    module_setup();

    Py_RETURN_NONE;
}
static PyObject* py_cleanup(PyObject* self, PyObject* args) {

    sunxi_gpio_cleanup();
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
    "A10S module",
    NULL,
    -1,
    module_methods
};
#endif
PyMODINIT_FUNC initA10S_GPIO(void) {
    PyObject* module = NULL;


#if PY_MAJOR_VERSION >= 3
    module = PyModule_Create(&module_methods);
#else
    module = Py_InitModule("A10S_GPIO", module_methods);
#endif


    if(module == NULL)
#if PY_MAJOR_VERSION >= 3
        return module;
#else
        return;
#endif



    SetupException = PyErr_NewException("PyA10S.SetupException", NULL, NULL);
    PyModule_AddObject(module, "SetupException", SetupException);
    OutputException = PyErr_NewException("PyA10S.OutputException", NULL, NULL);
    PyModule_AddObject(module, "OutputException", OutputException);
    InputException = PyErr_NewException("PyA10S.InputException", NULL, NULL);
    PyModule_AddObject(module, "InputException", InputException);



    high = Py_BuildValue("i", HIGH);
    PyModule_AddObject(module, "HIGH", high);

    low = Py_BuildValue("i", LOW);
    PyModule_AddObject(module, "LOW", low);

    inp = Py_BuildValue("i", INPUT);
    PyModule_AddObject(module, "INPUT", inp);

    out = Py_BuildValue("i", OUTPUT);
    PyModule_AddObject(module, "OUTPUT", out);

    per = Py_BuildValue("i", PER);
    PyModule_AddObject(module, "PER", per);




// GPIO-1
    PyModule_AddObject(module, "PIN40", Py_BuildValue("i", PIN40));
	PyModule_AddObject(module, "PIN41", Py_BuildValue("i", PIN41));
	PyModule_AddObject(module, "PIN10", Py_BuildValue("i", PIN10));
	PyModule_AddObject(module, "PIN11", Py_BuildValue("i", PIN11));
	PyModule_AddObject(module, "PIN42", Py_BuildValue("i", PIN42));
	PyModule_AddObject(module, "PIN43", Py_BuildValue("i", PIN43));
	PyModule_AddObject(module, "PIN44", Py_BuildValue("i", PIN44));
	PyModule_AddObject(module, "PIN45", Py_BuildValue("i", PIN45));
	
// GPIO-2
    PyModule_AddObject(module, "PIN4", Py_BuildValue("i", PIN4));
	PyModule_AddObject(module, "PIN5", Py_BuildValue("i", PIN5));
	PyModule_AddObject(module, "PIN6", Py_BuildValue("i", PIN6));
	PyModule_AddObject(module, "PIN7", Py_BuildValue("i", PIN7));
	PyModule_AddObject(module, "PIN8", Py_BuildValue("i", PIN8));
	PyModule_AddObject(module, "PIN9", Py_BuildValue("i", PIN9));
	PyModule_AddObject(module, "PIN12", Py_BuildValue("i", PIN12));
	PyModule_AddObject(module, "PIN13", Py_BuildValue("i", PIN13));
	PyModule_AddObject(module, "PIN14", Py_BuildValue("i", PIN14));
	PyModule_AddObject(module, "PIN15", Py_BuildValue("i", PIN15));
	PyModule_AddObject(module, "PIN16", Py_BuildValue("i", PIN16));
	PyModule_AddObject(module, "PIN17", Py_BuildValue("i", PIN17));
	PyModule_AddObject(module, "PIN18", Py_BuildValue("i", PIN18));
	PyModule_AddObject(module, "PIN19", Py_BuildValue("i", PIN19));
	PyModule_AddObject(module, "PIN20", Py_BuildValue("i", PIN20));
	PyModule_AddObject(module, "PIN21", Py_BuildValue("i", PIN21));
	PyModule_AddObject(module, "PIN22", Py_BuildValue("i", PIN22));
	PyModule_AddObject(module, "PIN23", Py_BuildValue("i", PIN23));
	PyModule_AddObject(module, "PIN24", Py_BuildValue("i", PIN24));
	PyModule_AddObject(module, "PIN25", Py_BuildValue("i", PIN25));
	PyModule_AddObject(module, "PIN26", Py_BuildValue("i", PIN26));
	PyModule_AddObject(module, "PIN27", Py_BuildValue("i", PIN27));
	PyModule_AddObject(module, "PIN28", Py_BuildValue("i", PIN28));
	PyModule_AddObject(module, "PIN29", Py_BuildValue("i", PIN29));
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
	PyModule_AddObject(module, "PIN3", Py_BuildValue("i", PIN3));
	
	
    
    if(Py_AtExit(sunxi_gpio_cleanup) != 0){
        
        sunxi_gpio_cleanup();
        
#if PY_MAJOR_VERSION >= 3
        return NULL;
#else
        return;
#endif
    }



}

