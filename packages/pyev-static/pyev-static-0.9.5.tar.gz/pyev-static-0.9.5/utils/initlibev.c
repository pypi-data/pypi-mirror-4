/*
This file is from pyzmq-static by Brandon Craig-Rhodes,
and used under the BSD license

py3compat from http://wiki.python.org/moin/PortingExtensionModulesToPy3k

Provide the init function that Python expects
when we compile libev by pretending it is a Python extension.
*/

#if defined(LIBEV_EMBED)
#include "ev.c"
#else
#include "ev.h"
#endif

#include "Python.h"

static PyMethodDef Methods[] = {
    {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "libev",
        NULL,
        -1,
        Methods,
        NULL,
        NULL,
        NULL,
        NULL
};

PyMODINIT_FUNC
PyInit_libev(void)
{
    PyObject *module = PyModule_Create(&moduledef);
    return module;
}

#else // py2

PyMODINIT_FUNC
initlibev(void)
{
    (void) Py_InitModule("libev", Methods);
}

#endif
