// Copyright (C) 2008-2012 Luis Pedro Coelho <luis@luispedro.org>
// Carnegie Mellon University
// 
// License: MIT (see COPYING file)

#include "utils.hpp"

extern "C" {
    #include <Python.h>
    #include <numpy/ndarrayobject.h>
}
namespace {

template<typename BaseType>
void compute_histogram(BaseType* data, int N, unsigned int* histogram) {
    for (int i = 0; i != N; ++i) {
        ++histogram[*data];
        ++data;
    }
}

PyObject* py_histogram(PyObject* self, PyObject* args) {
    PyArrayObject* array;
    PyArrayObject* histogram;
    if (!PyArg_ParseTuple(args, "OO", &array, &histogram) ||
            !PyArray_Check(array) ||
            !PyArray_Check(histogram) ||
            !PyArray_ISCARRAY(array) ||
            !PyArray_ISCARRAY(histogram) ||
            PyArray_TYPE(histogram) != NPY_UINT
            ) {
        PyErr_SetString(PyExc_RuntimeError, "Bad arguments to internal function.");
        return NULL;
    }
    unsigned int* histogram_data = static_cast<unsigned int*>(PyArray_DATA(histogram));
    const unsigned N = PyArray_SIZE(array);
    switch (PyArray_TYPE(array)) {
        case NPY_UBYTE:
            compute_histogram(static_cast<unsigned char*>(PyArray_DATA(array)), N, histogram_data);
            break;
        case NPY_USHORT:
            compute_histogram(static_cast<unsigned short*>(PyArray_DATA(array)), N, histogram_data);
            break;
        case NPY_UINT:
            compute_histogram(static_cast<unsigned int*>(PyArray_DATA(array)), N, histogram_data);
            break;
        case NPY_ULONG:
            compute_histogram(static_cast<npy_ulong*>(PyArray_DATA(array)), N, histogram_data);
            break;
        case NPY_ULONGLONG:
            compute_histogram(static_cast<npy_ulonglong*>(PyArray_DATA(array)), N, histogram_data);
            break;
        default:
            PyErr_SetString(PyExc_RuntimeError, "Cannot handle type.");
            return NULL;
    }
    Py_RETURN_NONE;
}
    


PyMethodDef methods[] = {
  {"histogram", (PyCFunction)py_histogram, METH_VARARGS, "Internal function. DO NOT CALL DIRECTLY!"},
  {NULL, NULL,0,NULL},
};
}

DECLARE_MODULE(_histogram)


