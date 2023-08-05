/*
 * _EXTENSIONS.C
 * Python/C API extension module for the PLIB package
 * Copyright (C) 2008-2012 by Peter A. Donis
 *
 * Released under the GNU General Public License, Version 2
 * See the LICENSE and README files for more information
 *
 */

#include <Python.h>
#include <stdio.h>

static char msg[] =
"Argument x to cobject_compare() is not a CObject.";

void
make_message(int i)
{
    switch (i) {
        case 1:
            msg[9] = '1';
            break;
        case 2:
            msg[9] = '2';
            break;
        default:
            msg[9] = 'x';
    }
    PyErr_SetString(PyExc_TypeError, msg);
}

static PyObject *
_extensions_PyCObjectCompare(PyObject *self, PyObject *args)
{
    int int1, int2;
    void *void1, *void2;
    PyObject *cobj1, *cobj2;

    /* Unpack arguments */
    if (!PyArg_ParseTuple(args, "OO:cobject_compare", &cobj1, &cobj2))
        return NULL;

    /* Check for valid CObject pointer input */
    int1 = PyCObject_Check(cobj1);
    if (!int1) {
        make_message(1);
        return NULL;
    }
    int2 = PyCObject_Check(cobj2);
    if (!int2) {
        make_message(2);
        return NULL;
    }

    /* Check whether CObjects wrap same pointer */
    void1 = PyCObject_AsVoidPtr(cobj1);
    void2 = PyCObject_AsVoidPtr(cobj2);
    if (void1 == void2) {
        Py_INCREF(Py_True);
        return Py_True;
      }
    Py_INCREF(Py_False);
    return Py_False;
}

PyDoc_STRVAR(cobject_compare__doc__,
"cobject_compare(PyCObject, PyCObject) -> bool\n\n"
"See if two CObjects wrap the same C-level pointer.");

static PyMethodDef _extensions_Methods[] = {
    {"cobject_compare", _extensions_PyCObjectCompare, METH_VARARGS,
        cobject_compare__doc__},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

PyDoc_STRVAR(_extensions__doc__,
"Python/C API extension module for the PLIB package.");

PyMODINIT_FUNC
init_extensions(void)
{
    Py_InitModule3("_extensions", _extensions_Methods, _extensions__doc__);
}
