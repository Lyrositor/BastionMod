/**
 * BastionMod - Dxt
 * Decodes and encodes DXT data.
 *
 * Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
 * This work is free. You can redistribute it and/or modify it under the terms
 * of the Do What The Fuck You Want To Public License, Version 2, as published
 * by Sam Hocevar. See the COPYING file for more details.
 */

#include <Python.h>
#include <squish.h>

using namespace squish;

// Converts DXT data to RGBA data.
static PyObject* BM_Dxt_ToRgba(PyObject* self, PyObject* args)
{
    unsigned int version;
    unsigned int width;
    unsigned int height;
    const char* inData;
    unsigned int inLen;

    if (!PyArg_ParseTuple(args, "LLLy#",
        &version, &width, &height, &inData, &inLen))
        return NULL;

    unsigned int outLen = 4 * width * height;
    unsigned char* outData = new unsigned char[outLen];
    int flags = version & (kDxt1 | kDxt3 | kDxt5);

    DecompressImage(outData, width, height, inData, flags);
    return Py_BuildValue("y#", outData, outLen);
}

// Converts RGBA data to DXT data.
static PyObject* BM_Dxt_FromRgba(PyObject* self, PyObject* args)
{
    Py_RETURN_NONE;
}

// DXT module methods.
static PyMethodDef BM_DxtMethods[] = {
    {"to_rgba", BM_Dxt_ToRgba, METH_VARARGS,
        "Converts DXT data to RGBA data."},
    {"from_rgba", BM_Dxt_FromRgba, METH_VARARGS,
        "Converts RGBA data to DXT data."},

    {NULL, NULL, 0, NULL}
};

// DXT module definition.
static struct PyModuleDef BM_DxtModule = {
   PyModuleDef_HEAD_INIT,
   "bm_dxt",
   "DXT conversion library",
   -1,
   BM_DxtMethods
};

// DXT module initialization.
PyMODINIT_FUNC PyInit_bm_dxt(void)
{
    return PyModule_Create(&BM_DxtModule);
}
