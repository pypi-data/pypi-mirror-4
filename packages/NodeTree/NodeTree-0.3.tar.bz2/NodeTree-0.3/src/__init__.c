/*
 *  NodeTree - Pythonic XML Data Binding Package
 *  Copyright (C) 2010,2011,2012,2013 Arc Riley
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU Lesser General Public License as published
 *  by the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Lesser General Public License for more details.
 *
 *  You should have received a copy of the GNU Lesser General Public License
 *  along with this program; if not, see http://www.gnu.org/licenses
 *
 */

#include "nodetree.h"

static char
nodetree_doc[] = ".. py:module:: nodetree\n"
"\n"
"    NodeTree provides a clean, modern API for working with XML in Python.\n"
"\n";

static char
nodetree_credits[] = "Copyright (C) 2010,2011,2012,2013 Arc Riley\n"
"\n"
"This program is free software; you can redistribute it and/or modify\n"
"it under the terms of the GNU Lesser General Public License as published\n"
"by the Free Software Foundation, either version 3 of the License, or\n"
"(at your option) any later version.\n"
"\n"
"This program is distributed in the hope that it will be useful,\n"
"but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
"MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"
"GNU Lesser General Public License for more details.\n"
"\n"
"You should have received a copy of the GNU Lesser General Public License\n"
"along with this program; if not, see http://www.gnu.org/licenses\n"
"\n";


static PyMethodDef nodetree_methods[] = {
    {NULL, NULL}
};

#if PY_MAJOR_VERSION == 3
static struct PyModuleDef nodetree_module = {
    PyModuleDef_HEAD_INIT,
    "nodetree",                        /*m_name*/
    nodetree_doc,                      /*m_doc*/
    0,                                 /*m_size*/
    nodetree_methods,                  /*m_methods*/
    NULL,                              /*m_reload*/
    NULL,                              /*m_traverse*/
    NULL,                              /*m_clear*/
    NULL                               /*m_free*/
};

PyMODINIT_FUNC
PyInit_nodetree(void) {

# else // Python 2.x
void
initnodetree(void)
{
#endif

    PyObject *module;

    /* Initialize all types prior to module creation

        int PyType_Ready(PyTypeObject*)
          Finalize a type object. This should be called on all type objects to
          finish their initialization. This function is responsible for adding
          inherited slots from a type's base class.
          Return 0 on success, or return -1 and sets an exception on error.
    */
    if ((PyType_Ready(&nodetree__Attributes_Type) < 0) ||
        (PyType_Ready(&nodetree_Comment_Type) < 0) ||
        (PyType_Ready(&nodetree_Document_Type) < 0) ||
        (PyType_Ready(&nodetree_Element_Type) < 0) ||
        (PyType_Ready(&nodetree_ProcessingInstruction_Type) < 0) ||
        (PyType_Ready(&nodetree_Stream_Type) < 0))

#if PY_MAJOR_VERSION == 3
        return NULL;

    module = PyModule_Create(&nodetree_module);

#else // Legacy Python init module, must also set __doc__ manually
        return;

    module = Py_InitModule3("nodetree", nodetree_methods, nodetree_doc);

#endif

    // Add additional pydoc strings
    PyModule_AddStringConstant(module, "__credits__", nodetree_credits);
    PyModule_AddStringConstant(module, "__version__", NODETREE_VERSION);

    // Add _Attributes type
    Py_INCREF(&nodetree__Attributes_Type);
    PyModule_AddObject(module, "_Attributes",
                       (PyObject*) &nodetree__Attributes_Type);

    // Add Comment type
    Py_INCREF(&nodetree_Comment_Type);
    PyModule_AddObject(module, "Comment", (PyObject*) &nodetree_Comment_Type);

    // Add Document type
    Py_INCREF(&nodetree_Document_Type);
    PyModule_AddObject(module, "Document",
                       (PyObject*) &nodetree_Document_Type);

    // Add Element type
    Py_INCREF(&nodetree_Element_Type);
    PyModule_AddObject(module, "Element", (PyObject*) &nodetree_Element_Type);

    // Add ProcessingInstruction type
    Py_INCREF(&nodetree_ProcessingInstruction_Type);
    PyModule_AddObject(module, "ProcessingInstruction",
                       (PyObject*) &nodetree_ProcessingInstruction_Type);

    // Add Stream type
    Py_INCREF(&nodetree_Stream_Type);
    PyModule_AddObject(module, "Stream", (PyObject*) &nodetree_Stream_Type);

    if (PyErr_Occurred()) {
        PyErr_SetString(PyExc_ImportError, "nodetree: init failed");

#if PY_MAJOR_VERSION == 3
        return NULL;
    }
    return module;

#else // Legacy Python
    }
    return;
#endif
}

