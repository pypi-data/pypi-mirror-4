/*
 TextIndexNG V 3                
 The next generation TextIndex for Zope

 This software is governed by a license. See
 LICENSE.txt for the terms of this license.
*/

#include "Python.h"
#include <stdlib.h>


static PyObject *
stopwordfilter(PyObject *modinfo, PyObject *args)
{
    PyObject *stopwords, *words, *list;
    int i, len;

    list = PyList_New(0);

    if (! (PyArg_ParseTuple(args,"OO",&words,&stopwords)))
        return NULL;

    words = PySequence_Fast(words, "1st argument must be a sequence");
    len = PyObject_Length(words);

    for (i=0; i<len; i++) {
        PyObject *item  = PySequence_Fast_GET_ITEM(words, i);

        if (PyDict_GetItem(stopwords, item) == NULL)
            PyList_Append(list,item);
    }

    Py_XDECREF(words);

    return list;
}


static struct PyMethodDef support_module_methods[] =
    {
        { "stopwordfilter", (PyCFunction) stopwordfilter, METH_VARARGS,
            "stopwordfilter(wordslist,stopword dict') " "-- filters words from wordslist that are stopwords"
        },
        { NULL, NULL }
    };


void
initsupport(void)
{
    PyObject *m, *d;
    char *rev="$Revision: 2068 $";

    /* Create the module and add the functions */
    m = Py_InitModule3("support", support_module_methods,
                        "TextIndexNG support module"); 

    /* Add some symbolic constants to the module */
    d = PyModule_GetDict(m);
    PyDict_SetItemString(d, "__version__",
                         PyString_FromStringAndSize(rev+11,strlen(rev+11)-2));
    if (PyErr_Occurred())
        Py_FatalError("can't initialize module support");
}

