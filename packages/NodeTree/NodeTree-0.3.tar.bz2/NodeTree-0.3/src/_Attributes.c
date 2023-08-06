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
#define SELF nodetree__Attributes_Object*
#define ELEMENT ((nodetree_Element_Object*) self->element)


static char
tp_doc[] = ".. py:class:: _Attributes(node)\n"
"\n"
"    This is a mapping of attributes names to string value.\n"
"\n"
"    :param node: parent node\n"
"\n";


SELF
nodetree__Attributes_Create (PyObject* node) {
    SELF self;
    nodetree_Element_Object* element = (nodetree_Element_Object*) node;

    // node type check
    if (!nodetree_Element_Check(node)) {
        PyErr_SetString(PyExc_TypeError,
           "Must provide a nodetree object that supports attributes");
        return NULL;
    }

    // Return existing attributes object if available
    if (element->attributes) {
        Py_INCREF(element->attributes);
        return element->attributes;
    }

    // Inherit base type
    self = (SELF)
           PyType_GenericNew(&nodetree__Attributes_Type, NULL, NULL);

    if (!self)
      return NULL;

    // Store the element
    Py_INCREF(node);
    self->element = node;
    element->attributes = self;
    return self;
}


static SELF
tp_new (PyTypeObject* type, PyObject* args, PyObject* kwds) {
    SELF self;
    PyObject* node;

    // Ensure no keywords were given
    if (!_PyArg_NoKeywords("_Attributes", kwds))
        return NULL;

    // Parse just the name
    if (!PyArg_ParseTuple(args, "O:_Attributes", &node))
        return NULL;

    // Return self
    return nodetree__Attributes_Create(node);
}


static void
tp_dealloc (SELF self) {
    // Clear reference from element
    ELEMENT->attributes = NULL;

    // Decref element
    Py_DECREF(self->element);

    // Dealloc base type
    PyObject_Del((PyObject*) self);
}


///////////////////////////////////////////////////////////////////////////////
// Sequence methods

static Py_ssize_t
sq_length (SELF self) {
    Py_ssize_t length = 0;
    xmlAttribute* attr = ((xmlElement*) ELEMENT->node)->attributes;

    // Walk attribute list to determine its length
    while (attr) {
        attr = (xmlAttribute*) attr->next;
        length++;
    }

    return length;
}


static int
sq_contains (SELF self, PyObject* value) {
    PyObject* name;
    xmlAttr* attr;

    // Require value to be either a bytes or unicode object
    if (PyBytes_Check(value)) {
        // Use a bytes string verbatim as UTF-8 name
        Py_INCREF(value);
        name = value;
    }
    else if (PyUnicode_Check(value)) {
        // Encode unicode string as UTF-8 bytes object
        name = PyUnicode_AsUTF8String(value);
    }
    else {
        // Raise exception
        PyErr_SetString(PyExc_TypeError, "attribute must be a string");
        return -1;
    }

    // attr will be NULL if not found
    attr = xmlHasProp(ELEMENT->node, (xmlChar*) PyBytes_AsString(name));

    Py_DECREF(name);
    return (attr != NULL);
}


///////////////////////////////////////////////////////////////////////////////
// Mapping methods

static PyObject*
mp_subscript (SELF self, PyObject* key) {
    PyObject* name;
    PyObject* value;
    char* attr;

    // Require key to be either a bytes or unicode object
    if (PyBytes_Check(key)) {
        // Use a bytes string verbatim as UTF-8 name
        Py_INCREF(key);
        name = key;
    }
    else if (PyUnicode_Check(key)) {
        // Encode unicode string as UTF-8 bytes object
        name = PyUnicode_AsUTF8String(key);
    }
    else {
        // Raise exception
        PyErr_SetString(PyExc_TypeError, "attribute name must be a string");
        return NULL;
    }

    // attr will be NULL if not found
    attr = xmlGetProp(ELEMENT->node, (xmlChar*) PyBytes_AsString(name));
    Py_DECREF(name);

    // Raise exception if not found
    if (!attr) {
        PyErr_SetString(PyExc_KeyError, "attribute not found");
        return NULL;
    }

    // Return value after freeing the return value from xmlGetProp
    value = PyUnicode_FromString(attr);
    xmlFree(attr);
    return value;
}


static int
mp_ass_subscript (SELF self, PyObject* key, PyObject* v) {
    PyObject* name;
    PyObject* value;
    xmlAttr* attr;
    xmlNode* node = ELEMENT->node;
    nodetree_node* next = ELEMENT->next;

    // Require key to be either a bytes or unicode object
    if (PyBytes_Check(key)) {
        // Use a bytes string verbatim as UTF-8 name
        Py_INCREF(key);
        name = key;
    }
    else if (PyUnicode_Check(key)) {
        // Encode unicode string as UTF-8 bytes object
        name = PyUnicode_AsUTF8String(key);
    }
    else {
        // Raise exception
        PyErr_SetString(PyExc_TypeError, "attribute name must be a string");
        return -1;
    }

    // If v == NULL then delete attribute
    if (!v) {
        /* Delete attribute from each of Element's nodes

            Element may have multiple copies of itself due to being added to
            multiple parents.  As a result, each copy will have its own
            attributes list, so we need to perform this deletion on each.
        */
        while (node) {
            // attr will be NULL if not found
            attr = xmlHasProp(node, (xmlChar*) PyBytes_AsString(name));

            // Ensure key exists
            if (!attr) {
                Py_DECREF(name);
                PyErr_SetString(PyExc_KeyError, "attribute not found");
                return -1;
            }

            // Try to remove it, return error if raised by libxml
            if (xmlRemoveProp(attr) == -1) {
                Py_DECREF(name);
                PyErr_SetString(PyExc_KeyError, "error deleting attribute");
                return -1;
            }

            // Get next node
            if (next) {
                node = next->node;
                next = next->next;
            }
            else
                node = NULL;
        }

        // Successfully deleted attribute
        Py_DECREF(name);
        return 0;
    }

    // Require value to be either a bytes or unicode object
    if (PyBytes_Check(v)) {
        // Use a bytes string verbatim as UTF-8 name
        Py_INCREF(v);
        value = v;
    }
    else if (PyUnicode_Check(v)) {
        // Encode unicode string as UTF-8 bytes object
        value = PyUnicode_AsUTF8String(v);
    }
    else {
        // Raise exception
        Py_DECREF(name);
        PyErr_SetString(PyExc_TypeError, "attribute value must be a string");
        return -1;
    }

    /* Change attribute from each of Element's nodes

        Element may have multiple copies of itself due to being added to
        multiple parents.  As a result, each copy will have its own
        attributes list, so we need to change each of their attributes.
    */
    while (node) {
        // Tell libxml to set the attribute
        attr = xmlSetProp(node, (xmlChar*) PyBytes_AsString(name),
                          (xmlChar*) PyBytes_AsString(value));

        // Return error if raised by libxml
        if (!attr) {
            Py_DECREF(name);
            Py_DECREF(value);
            PyErr_SetString(PyExc_ValueError, "invalid XML attribute");
            return -1;
        }

        // Get next node
        if (next) {
            node = next->node;
            next = next->next;
        }
        else
            node = NULL;
    }

    // Successfully assigned new value
    Py_DECREF(name);
    Py_DECREF(value);
    return 0;
}


///////////////////////////////////////////////////////////////////////////////
// Iterator Subtype

static PyTypeObject tp_iter_Type;
typedef struct {
    PyObject_HEAD
    SELF self;
} tp_iter_Object;


static tp_iter_Object*
tp_iter (SELF self) {
    tp_iter_Object* iter;

    // Ensure the iter type is initialized, this could be done better
    PyType_Ready(&tp_iter_Type);

    // Inherit base type
    iter = (tp_iter_Object*)
           PyType_GenericNew(&tp_iter_Type, NULL, NULL);

    if (!iter)
      return NULL;

    // Store "self" in iter object struct
    Py_INCREF(self);
    iter->self = self;

    // Return new iterator object
    return iter;
}


static void
tp_iter_dealloc (tp_iter_Object* iter) {
    // Decref self
    Py_DECREF(iter->self);

    // Dealloc base type
    PyObject_Del((PyObject*) iter);
}


static PyObject*
tp_iter_iternext (tp_iter_Object* iter) {
    // TODO
    return NULL;
}


static PyTypeObject tp_iter_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "nodetree._Attributes.__iter__",                       // tp_name
    sizeof(tp_iter_Object),                                // tp_basicsize
    0,                                                     // tp_itemsize
    (destructor) tp_iter_dealloc,                          // tp_dealloc
    0,                                                     // RESERVED
    (getattrfunc) 0,                                       // tp_getattr
    (setattrfunc) 0,                                       // tp_setattr
    0,                                                     // RESERVED
    0,                                                     // tp_repr
    0,                                                     // tp_as_number
    0,                                                     // tp_as_sequence
    0,                                                     // tp_as_mapping
    0,                                                     // tp_hash
    0,                                                     // tp_call
    0,                                                     // tp_str
    PyObject_GenericGetAttr,                               // tp_getattro
    (setattrofunc) 0,                                      // tp_setattro
    0,                                                     // tp_as_buffer
    Py_TPFLAGS_DEFAULT,                                    // tp_flags
    0,                                                     // tp_doc
    0,                                                     // tp_traverse
    0,                                                     // tp_clear
    0,                                                     // tp_richcompare
    0,                                                     // tp_weaklistoffset
    PyObject_SelfIter,                                     // tp_iter
    (iternextfunc) tp_iter_iternext,                       // tp_iternext
};


///////////////////////////////////////////////////////////////////////////////
// Type structs

static PySequenceMethods tp_as_sequence = {
    (lenfunc) sq_length,                                   // sq_length
    0,                                                     // sq_concat
    0,                                                     // sq_repeat
    0,                                                     // sq_item
    0,                                                     // was_sq_slice
    0,                                                     // sq_ass_item
    0,                                                     // was_sq_ass_slice
    (objobjproc) sq_contains,                              // sq_contains
    0,                                                     // sq_inplace_concat
    0,                                                     // sq_inplace_repeat
};


static PyMappingMethods tp_as_mapping = {
    0,                                                     // mp_length
    (binaryfunc) mp_subscript,                             // mp_subscript
    (objobjargproc) mp_ass_subscript,                      // mp_ass_subscript
};


static PyMethodDef tp_methods[] = {
    {NULL},                                                // sentinel
};


static PyGetSetDef tp_getset[] = {
    {NULL},                                                // sentinel
};


PyTypeObject nodetree__Attributes_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "nodetree._Attributes",                                // tp_name
    sizeof(nodetree__Attributes_Object),                   // tp_basicsize
    0,                                                     // tp_itemsize
    (destructor) tp_dealloc,                               // tp_dealloc
    0,                                                     // RESERVED
    (getattrfunc) 0,                                       // tp_getattr
    (setattrfunc) 0,                                       // tp_setattr
    0,                                                     // RESERVED
    0,                                                     // tp_repr
    0,                                                     // tp_as_number
    &tp_as_sequence,                                       // tp_as_sequence
    &tp_as_mapping,                                        // tp_as_mapping
    0,                                                     // tp_hash
    0,                                                     // tp_call
    0,                                                     // tp_str
    (getattrofunc) 0,                                      // tp_getattro
    (setattrofunc) 0,                                      // tp_setattro
    0,                                                     // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,              // tp_flags
    tp_doc,                                                // tp_doc
    0,                                                     // tp_traverse
    0,                                                     // tp_clear
    0,                                                     // tp_richcompare
    0,                                                     // tp_weaklistoffset
    (getiterfunc) tp_iter,                                 // tp_iter
    0,                                                     // tp_iternext
    tp_methods,                                            // tp_methods
    0,                                                     // tp_members
    tp_getset,                                             // tp_getset
    0,                                                     // tp_base
    0,                                                     // tp_dict
    0,                                                     // tp_descr_get
    0,                                                     // tp_descr_set
    0,                                                     // tp_dictoffset
    0,                                                     // tp_init
    0,                                                     // tp_alloc
    (newfunc) tp_new,                                      // tp_new
    0,                                                     // tp_free
    0,                                                     // tp_is_gc
};

