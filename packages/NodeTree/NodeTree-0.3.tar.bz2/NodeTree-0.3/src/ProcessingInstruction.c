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
#define SELF nodetree_ProcessingInstruction_Object*


SELF
nodetree_ProcessingInstruction_Create (xmlNode* node) {
    SELF self;

    // Inherit base type
    self = (SELF) PyType_GenericNew(&nodetree_ProcessingInstruction_Type,
                                    NULL, NULL);
    if (!self)
      return NULL;

    // Link XML node to this object
    self->node = node;
    self->next = NULL;

    // Link new object to XML node
    self->node->_private = self;

    return self;
}


static char
tp_doc[] = ".. py:class:: ProcessingInstruction(name[, content])\n"
"\n"
"    Processing Instructions are node types which carry instructions\n"
"    intended for XML applications::\n"
"\n"
"        >>> pi = nodetree.ProcessingInstruction('target', 'content')\n"
"        >>> pi\n"
"        <?target content?>\n"
"\n"
"    :param string name: processing instruction target name\n"
"    :param string content: processing instruction content\n"
"\n";


static SELF
tp_new (PyTypeObject* type, PyObject* args, PyObject* kwds) {
    xmlChar* name;
    xmlChar* content = NULL;
    xmlNode* node;
    SELF self;

    // Ensure no keywords were given
    if (!_PyArg_NoKeywords("ProcessingInstruction", kwds))
        return NULL;

    // Parse just the name
    if (!PyArg_ParseTuple(args, "s|z:ProcessingInstruction", &name, &content))
        return NULL;

    // Create new XML node
    node = xmlNewPI(name, content);

    // Create new Python object, free node on failure
    self = nodetree_ProcessingInstruction_Create(node);
    if (!self)
        xmlFreeNode(node);

    // Python will free name, just return self
    return self;
}


static void
tp_dealloc (SELF self) {
    nodetree_node* next = self->next;

    // Prune each in linked list
    while (next) {
        // Prune node if orphan
        if (self->next->node->parent) {

        }
        else {
            // Prune node if orphan
            nodetree_node_Prune(self->next->node);
        }
    }

    // Delink primary node from Python object
    self->node->_private = NULL;

    // Prune if primary node is an orphan
    if (!self->node->parent)
        nodetree_node_Prune(self->node);

    //
    // Dealloc base type
    PyObject_Del((PyObject*) self);
}


static PyObject*
tp_repr (SELF self) {
    xmlBuffer* buffer;
    PyObject* ret;

    // Create new XML buffer
    buffer = xmlBufferCreate();

    // Dump XML for element to a string
    xmlNodeDump(buffer, NULL, self->node, 0, 1);

    // Convert the returned XML string to a Python return string
    ret = PyUnicode_FromStringAndSize((char*) buffer->content, buffer->use);

    // Free buffer and return string
    xmlBufferFree(buffer);
    return ret;
}


static PyObject*
tp_str (SELF self) {
    xmlBuffer* buffer;
    PyObject* ret;

    // Create new XML buffer
    buffer = xmlBufferCreate();

    // Dump XML for element to a string
    xmlNodeDump(buffer, NULL, self->node, 0, 0);

    // Convert the returned XML string to a Python return string
    ret = PyUnicode_FromStringAndSize((char*) buffer->content, buffer->use);

    // Free buffer and return string
    xmlBufferFree(buffer);
    return ret;
}


///////////////////////////////////////////////////////////////////////////////
// Properties

static char
content_doc[] = ".. py:attribute:: ProcessingInstruction.content\n"
"\n"
"    This is the processing instruction's content::\n"
"\n"
"        >>> pi = nodetree.ProcessingInstruction('xml-stylesheet')\n"
"        >>> pi.content = 'href=\"style.xsl\" type=\"text/xsl\"'\n"
"        >>> print(pi.content)\n"
"        href=\"style.xsl\" type=\"text/xsl\"\n"
"        >>> pi\n"
"        <?xml-stylesheet href=\"style.xsl\" type=\"text/xsl\"?>\n"
"        >>> del(pi.content)\n"
"        >>> pi\n"
"        <?xml-stylesheet?>\n"
"\n";


static PyObject*
content_getter (SELF self, void* closure) {
    if (!self->node->content)
        Py_RETURN_NONE;
    return PyUnicode_FromString(self->node->content);
}


static int
content_setter (SELF self, PyObject* value, void* closure) {
    PyObject* bytes;
    xmlChar* string;
    xmlNode* node = self->node;
    nodetree_node* next = self->next;

    // Check for deletion
    if (!value) {
        bytes = NULL;
        string = NULL;
    }

    // Require key to be either a bytes or unicode object
    else if (PyBytes_Check(value)) {
        // Use a bytes string verbatim as UTF-8 name
        Py_INCREF(value);
        bytes = value;
        string = PyBytes_AsString(bytes);
    }
    else if (PyUnicode_Check(value)) {
        // Encode unicode string as UTF-8 bytes object
        bytes = PyUnicode_AsUTF8String(value);
        string = PyBytes_AsString(bytes);
    }
    else {
        // Raise exception
        PyErr_SetString(PyExc_TypeError, "content must be a string");
        return -1;
    }


    /* Update name of each node

        Remember, Element nodes may belong to many parents and for each there's
        a copy of itself held in a linked list.  Each must be updated.
    */
    while (1) {
        // libxml2 will do the right thing
        xmlNodeSetContent(node, string);

        // End loop if this is the last node
        if (!next)
            break;

        // Get next node
        node = next->node;
        next = next->next;
    }

    // Free up bytes and return success
    if (bytes)
        Py_DECREF(bytes);
    return 0;
}


static char
name_doc[] = ".. py:attribute:: ProcessingInstruction.name\n"
"\n"
"    This is the processing instruction's target name::\n"
"\n"
"        >>> pi = nodetree.ProcessingInstruction('foo')\n"
"        >>> print(pi.name)\n"
"        foo\n"
"        >>> pi.content = 'alpha'\n"
"        >>> pi\n"
"        <?foo alpha?>\n"
"        >>> pi.name = 'bar'\n"
"        >>> pi\n"
"        <?bar alpha?>\n"
"\n";


static PyObject*
name_getter (SELF self, void* closure) {
    return PyUnicode_FromString((char*) self->node->name);
}


static int
name_setter (SELF self, PyObject* value, void* closure) {
    PyObject* bytes;
    xmlChar* string;
    xmlNode* node = self->node;
    nodetree_node* next = self->next;

    if (value == NULL) {
        PyErr_SetString(PyExc_AttributeError, "cannot delete name property");
        return -1;
    }

    // Require key to be either a bytes or unicode object
    if (PyBytes_Check(value)) {
        // Use a bytes string verbatim as UTF-8 name
        Py_INCREF(value);
        bytes = value;
    }
    else if (PyUnicode_Check(value)) {
        // Encode unicode string as UTF-8 bytes object
        bytes = PyUnicode_AsUTF8String(value);
    }
    else {
        // Raise exception
        PyErr_SetString(PyExc_TypeError, "name property must be a string");
        return -1;
    }

    // Get char* from bytes object
    string = PyBytes_AsString(bytes);

    /* Update name of each node

        Remember, Element nodes may belong to many parents and for each there's
        a copy of itself held in a linked list.  Each must be updated.
    */
    while (1) {
        // libxml2 will do the right thing
        xmlNodeSetName(node, string);

        // End loop if this is the last node
        if (!next)
            break;

        // Get next node
        node = next->node;
        next = next->next;
    }

    // Free up bytes and return success
    Py_DECREF(bytes);
    return 0;
}


///////////////////////////////////////////////////////////////////////////////
// Type structs

static PyMethodDef tp_methods[] = {
    {NULL},                                                // sentinel
};


static PyGetSetDef tp_getset[] = {
    {"content",
     (getter) content_getter,
     (setter) content_setter,
     content_doc,
     NULL},
    {"name",
     (getter) name_getter,
     (setter) name_setter,
     name_doc,
     NULL},
    {NULL},                                                // sentinel
};


PyTypeObject nodetree_ProcessingInstruction_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "nodetree.ProcessingInstruction",                      // tp_name
    sizeof(nodetree_ProcessingInstruction_Object),         // tp_basicsize
    0,                                                     // tp_itemsize
    (destructor) tp_dealloc,                               // tp_dealloc
    0,                                                     // RESERVED
    (getattrfunc) 0,                                       // tp_getattr
    (setattrfunc) 0,                                       // tp_setattr
    0,                                                     // RESERVED
    (reprfunc) tp_repr,                                    // tp_repr
    0,                                                     // tp_as_number
    0,                                                     // tp_as_sequence
    0,                                                     // tp_as_mapping
    0,                                                     // tp_hash
    0,                                                     // tp_call
    (reprfunc) tp_str,                                     // tp_str
    (getattrofunc) 0,                                      // tp_getattro
    (setattrofunc) 0,                                      // tp_setattro
    0,                                                     // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,              // tp_flags
    tp_doc,                                                // tp_doc
    0,                                                     // tp_traverse
    0,                                                     // tp_clear
    0,                                                     // tp_richcompare
    0,                                                     // tp_weaklistoffset
    0,                                                     // tp_iter
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

