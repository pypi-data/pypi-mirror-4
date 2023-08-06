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
#define SELF nodetree_Comment_Object*


static char
tp_doc[] = ".. py:class:: Comment(comment)\n"
"\n"
"    Comment nodes contain information useful to a human reading an XML\n"
"    document but are not generally intended for processing.\n"
"\n"
"    They have no methods or properties, their content is set on creation\n"
"    and can be retreived by repr() or str() like any other node::\n"
"\n"
"        >>> credit = nodetree.Comment(' Template by Peter ')\n"
"        >>> credit  # this runs repr()\n"
"        <!-- Template by Peter -->\n"
"        >>> str(credit)\n"
"        '<!-- Template by Peter -->'\n"
"\n"
"    :param string text: text content of comment node\n"
"\n";


PyObject*
nodetree_Comment_Create (xmlNode* node) {
    SELF self;

    // Inherit base type
    self = (SELF) PyType_GenericNew(&nodetree_Comment_Type, NULL, NULL);
    if (!self)
      return NULL;

    // Link XML node to this object
    self->node = node;
    self->next = NULL;

    // Link new object to XML node
    self->node->_private = self;

    return (PyObject*) self;
}


static PyObject*
tp_new (PyTypeObject* type, PyObject* args, PyObject* kwds) {
    PyObject* self;
    char* content;
    xmlNode* node;

    // Ensure no keywords were given
    if (!_PyArg_NoKeywords("Comment", kwds))
        return NULL;

    // Parse just the content
    if (!PyArg_ParseTuple(args, "s:Comment", &content))
        return NULL;

    // Create new XML node
    node = xmlNewComment((xmlChar*) content);

    // Create new Python object, free node on failure
    self = nodetree_Comment_Create(node);
    if (!self)
        xmlFreeNode(node);

    // Python will free name, just return self
    return self;
}


static void
tp_dealloc (SELF self) {
    xmlNode* node;
    nodetree_node* next;

    /* Comments contain no children so cleanup is fairly straightforward;

       If the primary node is orphaned (no parent) just free it since nothing
       in either object system references it anymore.  There should never be
       copies of an orphaned node so we're finished.

       If the primary node has a parent then clear its _private field, then
       walk through any additional nodes and do the same to them while freeing
       the nodetree_node structs once we're finished with each one.
    */

    self->node->_private = NULL;

    // Free primary node if orphan
    if (!self->node->parent) {
        // Node isn't linked to anything so doesn't need to be unlinked
        xmlFreeNode(self->node);
    }

    // Walk through node copies clearing pointers to this object
    else {
        node = self->node;
        next = self->next;

        while (1) {
            // Reset _private field where pointers to this object are stored
            node->_private = NULL;

            // Exit while loop if we've reached the end
            if (!next)
                break;

            // Grab values for next loop
            node = next->node;
            next = next->next;

            // Clean up the next structs as these belong to this Object
            PyMem_Free(next);
        }
    }

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

    // Dump XML for Comment to a string
    xmlNodeDump(buffer, NULL, self->node, 0, 0);

    // Convert the returned XML string to a Python return string
    ret = PyUnicode_FromStringAndSize((char*) buffer->content, buffer->use);

    // Free buffer and return string
    xmlBufferFree(buffer);
    return ret;
}


///////////////////////////////////////////////////////////////////////////////
// Type structs

PyTypeObject nodetree_Comment_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "nodetree.Comment",                                    // tp_name
    sizeof(nodetree_Comment_Object),                       // tp_basicsize
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
    0,                                                     // tp_methods
    0,                                                     // tp_members
    0,                                                     // tp_getset
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

