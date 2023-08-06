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

static int module_setup(void){
    int result;
    
    result = sunxi_gpio_init();
    if(result == SETUP_DEVMEM_FAIL){
        PyErr_SetString(SetupException, "No access to /dev/mem. Try running as root!");
        return SETUP_DEVMEM_FAIL;
    }
    else if(result == SETUP_MALLOC_FAIL){
        PyErr_NoMemory();
        return SETUP_MALLOC_FAIL;
    }
    else if(result == SETUP_MMAP_FAIL){
        PyErr_SetString(SetupException, "Mmap failed on module import");
        return SETUP_MMAP_FAIL;
    }
    else{
        return SETUP_OK;
    }
    
    return SETUP_OK;
}



static PyObject* py_cleanup(PyObject* self, PyObject* args)
{    
    
    
    sunxi_gpio_cleanup();
    
    Py_RETURN_NONE;   
}


PyMethodDef module_methods[] = {
    {"cleanup", py_cleanup, METH_NOARGS, "munmap /dev/map."},
    {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    "A13 module",
    NULL,
    -1,
    module_methods
};
#endif


PyMODINIT_FUNC initA13_GPIO(void)
{
    PyObject* module = NULL;    
    
    
#if PY_MAJOR_VERSION >= 3
    module = PyModule_Create(&module_methods);
#else
    module = Py_InitModule("A13_GPIO", module_methods);
#endif


    if(module == NULL)
#if PY_MAJOR_VERSION >= 3
        return module;
#else
        return;
#endif
    
    SetupException = PyErr_NewException("PyA13.SetupException", NULL, NULL);
    PyModule_AddObject(module, "SetupException", SetupException);
    
    printf("Init module...");
    if(module_setup() != SETUP_OK){
#if PY_MAJOR_VERSION >= 3
        return NULL;
#else
        return;
#endif
    }
    

    
    


}

