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
#define SELF nodetree_Element_Object*


SELF
nodetree_Element_Create (xmlNode* node) {
    SELF self;

    // Inherit base type
    self = (SELF) PyType_GenericNew(&nodetree_Element_Type, NULL, NULL);
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
tp_doc[] = ".. py:class:: Element(name)\n"
"\n"
"    Objects of this type represent an XML element containing zero or more\n"
"    child nodes which can be managed like a Python list::\n"
"\n"
"        >>> e = nodetree.Element('foo')\n"
"        >>> e.append('content ')\n"
"        >>> e.append(nodetree.Element('bar'))\n"
"        >>> e[1].append('data')\n"
"        >>> e\n"
"        <foo>content <bar>data</bar></foo>\n"
"        >>> e[0] = 'Updated Content '\n"
"        >>> e[1][0] = 'Expanded Data'\n"
"        >>> e\n"
"        <foo>Updated Content <bar>Expanded Data</bar></foo>\n"
"\n"
"    I haven't determined how to handle namespaces yet.\n"
"\n"
"    :param string name: element name\n"
"\n";


static SELF
tp_new (PyTypeObject* type, PyObject* args, PyObject* kwds) {
    char* name;
    xmlNode* node;
    SELF self;

    // Ensure no keywords were given
    if (!_PyArg_NoKeywords("Element", kwds))
        return NULL;

    // Parse just the name
    if (!PyArg_ParseTuple(args, "s:Element", &name))
        return NULL;

    // Create new XML node
    node = xmlNewNode(NULL, (xmlChar*) name);

    // Create new Python object, free node on failure
    self = nodetree_Element_Create(node);
    if (!self)
        xmlFreeNode(node);

    // Python will free name, just return self
    return self;
}


static void
tp_dealloc (SELF self) {
    nodetree_node* next = self->next;

    // Free our linked list
    while (next) {
        nodetree_node* this = next;
        next = next->next;
        PyMem_Free(this);
    }

    // Clear next pointer
    self->next = NULL;

    // Delink primary node from Python object
    self->node->_private = NULL;

    // Prune if primary node is an orphan
    if (!self->node->parent)
        nodetree_node_Prune(self->node);

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
// Sequence methods

static Py_ssize_t
sq_length (SELF self) {
    // Use child node counter
    return (Py_ssize_t) nodetree_node_Child_Count((xmlNode*) self->node);
}


static PyObject*
sq_item(SELF self, Py_ssize_t index) {
    // Use child node getter
    return nodetree_node_Child_Get(self->node, (int) index);
}


static int
sq_ass_item (SELF self, Py_ssize_t index, PyObject* value) {
    xmlNode* node = self->node;
    nodetree_node* next = self->next;

    // Add a copy of the child to every copy of our own node to keep in sync
    while (node) {
        /* Use child node setter.

            If this fails it should always fail on the first pass.
        */
        if (nodetree_node_Child_Set(node, (int) index, value) == -1)
            return -1;

        // Get next node
        if (next) {
            node = next->node;
            next = next->next;
        }
        else
            node = NULL;
    }

    return 0;
}


static int
sq_contains (SELF self, PyObject* value) {
    return 0;
}


///////////////////////////////////////////////////////////////////////////////
// Methods

static char
append_doc[] = ".. py:method:: Element.append(node)\n"
"\n"
"    This method adds a new XML node to an element. It works like the\n"
"    append method of Python lists but only supports types which can be\n"
"    legally added to an XML element::\n"
"\n"
"        >>> e = nodetree.Element('foo')\n"
"        >>> e.append(nodetree.Comment(' Start '))\n"
"        >>> e.append(nodetree.Element('bar'))\n"
"        >>> e[-1].append(1)\n"
"        Traceback (most recent call last):\n"
"            ...\n"
"        TypeError: Unsupported XML type\n"
"        >>> e[-1].append('1')\n"
"        >>> e\n"
"        <foo>\n"
"          <!-- Start -->\n"
"          <bar>1</bar>\n"
"        </foo>\n"
"\n"
"    :param node: node to be added to the element\n"
"\n";


static PyObject*
append_meth (SELF self, PyObject* args) {
    PyObject* item;
    xmlNode* child;
    xmlNode* node = self->node;
    nodetree_node* next = self->next;

    // Parse item as single argument
    if (!PyArg_ParseTuple(args, "O", &item)) {
        return NULL;
    }

    // Add a copy of the child to every copy of our own node to keep in sync
    while (node) {
        // Get new child node
        child = nodetree_node_Py2XML(item);

        // Return exception NULL was returned by nodetree_node_Py2XML
        if (!child)
            return NULL;

        // Add child to end of children list
        child = xmlAddChild(node, child);

        // Raise exception if this fails for some reason
        if (!child) {
            PyErr_SetString(PyExc_ValueError, "error appending child");
            return NULL;
        }

        // Get next node
        if (next) {
            node = next->node;
            next = next->next;
        }
        else
            node = NULL;
    }



    // Returns None on success
    Py_RETURN_NONE;
}


static char
pop_doc[] = ".. py:method:: Element.pop([index])\n"
"\n"
"    Remove and return child node by index. Will raise an exception if\n"
"    the specified child is currently being parsed in a Stream::\n"
"\n"
"        >>> s = nodetree.Stream('<stream:stream xmlns=\"jabber:client\"' +\n"
"        ...         ' xmlns:stream=\"http://etherx.jabber.org/streams\">')\n"
"        >>> s.send('<message><body>Hello, World!</body></message>')\n"
"        >>> s.root.pop(0)\n"
"        <message>\n"
"          <body>Hello, World!</body>\n"
"        </message>\n"
"        >>> s.send('<message><body>This works')\n"
"        >>> s.root.pop(0)\n"
"        Traceback (most recent call last):\n"
"          File \"<stdin>\", line 1, in <module>\n"
"        ValueError: incomplete branch\n"
"        >>> s.send(' well</body></message>')\n"
"        >>> s.root.pop(0)\n"
"        <message>\n"
"          <body>This works well</body>\n"
"        </message>\n"
"\n"
"    :param int index: index of target child (defaults to last)\n"
"    :raises: IndexError, ValueError\n"
"    :returns: removed child node\n"
"\n";

static PyObject*
pop_meth (SELF self, PyObject* args) {
    int index = -1;
    xmlNode* node = self->node;
    nodetree_node* next = self->next;
    xmlNode* item;
    PyObject* child;

    // Parse item as single argument
    if (!PyArg_ParseTuple(args, "|i", &index)) {
        return NULL;
    }

    // Ensure there's at least one child
    if (node->children == NULL) {
        PyErr_SetString(PyExc_IndexError, "pop from empty Element");
        return NULL;
    }

    // Get original node for this element
    while (next) {
        node = next->node;
        next = next->next;
    }

    // Get either last child node or child node by index
    if (index == -1)
        item = node->last;
    else
        item = nodetree_node_Child_Index(node, index);

    // Raise exception if child node wasn't found
    if (!item) {
        PyErr_SetString(PyExc_IndexError, "child index out of range");
        return NULL;
    }

    // Check if this element is part of an active stream
    if (node->doc &&
        node->doc->_private &&
        nodetree_Stream_Check(node->doc->_private) &&
        ((nodetree_Stream_Object*) node->doc->_private)->ctxt) {

        // We need to make sure the node being popped is not part of the
        // branch currently being parsed by the stream
        nodetree_Stream_Object* stream = node->doc->_private;
        xmlNode* current = stream->ctxt->node;

        // Walk up tree ensuring no ancestor of current node is our item
        while (current && current != (xmlNode*) node->doc) {
            if (current == item) {
                PyErr_SetString(PyExc_ValueError, "incomplete branch");
                return NULL;
            }
            current = current->parent;
        }

    }

    // Get child object for item
    child = nodetree_node_Create(item);

    // Prune child node for every copy
    node = self->node;
    next = self->next;
    while (node) {
        // Get either last child node or child node by index
        if (index == -1)
            item = node->last;
        else
            item = nodetree_node_Child_Index(node, index);

        nodetree_node_Prune(item);

        // Get next node
        if (next) {
            node = next->node;
            next = next->next;
        }
        else
            node = NULL;
    }

    // Return popped child
    return child;
}


///////////////////////////////////////////////////////////////////////////////
// Properties

static char
attributes_doc[] = ".. py:attribute:: Element.attributes\n"
"\n"
"    This is a mapping of XML attributes. It can be used like a Python\n"
"    dict to add, get, modify, and delete an element's attributes::\n"
"\n"
"        >>> e = nodetree.Element('foo')\n"
"        >>> e.attributes['bar'] = 'baz'\n"
"        >>> print(e.attributes['bar'])\n"
"        baz\n"
"        >>> e\n"
"        <foo bar=\"baz\"/>\n"
"        >>> del(e.attributes['bar'])\n"
"        >>> e\n"
"        <foo/>\n"
"\n";


static PyObject*
attributes_getter (SELF self, void* closure) {
    return (PyObject*) nodetree__Attributes_Create((PyObject*) self);
}


static char
name_doc[] = ".. py:attribute:: Element.name\n"
"\n"
"    This property allows you to get and change an element's name::\n"
"\n"
"        >>> e = nodetree.Element('foo')\n"
"        >>> print(e.name)\n"
"        foo\n"
"        >>> e.append('Value')\n"
"        >>> e.attributes['type'] = 'alpha'\n"
"        >>> e\n"
"        <foo type=\"alpha\">Value</foo>\n"
"        >>> e.name = 'bar'\n"
"        >>> e\n"
"        <bar type=\"alpha\">Value</bar>\n"
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
        PyErr_SetString(PyExc_AttributeError, "cannot delete name attribute");
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
        PyErr_SetString(PyExc_TypeError, "name attribute must be a string");
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

static PySequenceMethods tp_as_sequence = {
    (lenfunc) sq_length,                                   // sq_length
    0,                                                     // sq_concat
    0,                                                     // sq_repeat
    (ssizeargfunc) sq_item,                                // sq_item
    0,                                                     // was_sq_slice
    (ssizeobjargproc) sq_ass_item,                         // sq_ass_item
    0,                                                     // was_sq_ass_slice
    (objobjproc) sq_contains,                              // sq_contains
    0,                                                     // sq_inplace_concat
    0,                                                     // sq_inplace_repeat
};


static PyMethodDef tp_methods[] = {
    {"append",                                             // ml_name
     (PyCFunction) append_meth,                            // ml_meth
     METH_VARARGS,                                         // ml_flags
     append_doc},                                          // ml_doc
    {"pop",                                                // ml_name
     (PyCFunction) pop_meth,                               // ml_meth
     METH_VARARGS,                                         // ml_flags
     pop_doc},                                             // ml_doc
    {NULL},                                                // sentinel
};


static PyGetSetDef tp_getset[] = {
    {"attributes",
     (getter) attributes_getter,
     NULL,
     attributes_doc,
     NULL},
    {"name",
     (getter) name_getter,
     (setter) name_setter,
     name_doc,
     NULL},
    {NULL},                                                 // sentinel
};


PyTypeObject nodetree_Element_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "nodetree.Element",                                     // tp_name
    sizeof(nodetree_Element_Object),                        // tp_basicsize
    0,                                                      // tp_itemsize
    (destructor) tp_dealloc,                                // tp_dealloc
    0,                                                      // RESERVED
    (getattrfunc) 0,                                        // tp_getattr
    (setattrfunc) 0,                                        // tp_setattr
    0,                                                      // RESERVED
    (reprfunc) tp_repr,                                     // tp_repr
    0,                                                      // tp_as_number
    &tp_as_sequence,                                        // tp_as_sequence
    0,                                                      // tp_as_mapping
    0,                                                      // tp_hash
    0,                                                      // tp_call
    (reprfunc) tp_str,                                      // tp_str
    (getattrofunc) 0,                                       // tp_getattro
    (setattrofunc) 0,                                       // tp_setattro
    0,                                                      // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,               // tp_flags
    tp_doc,                                                 // tp_doc
    0,                                                      // tp_traverse
    0,                                                      // tp_clear
    0,                                                      // tp_richcompare
    0,                                                      // tp_weaklistoffset
    0,                                                      // tp_iter
    0,                                                      // tp_iternext
    tp_methods,                                             // tp_methods
    0,                                                      // tp_members
    tp_getset,                                              // tp_getset
    0,                                                      // tp_base
    0,                                                      // tp_dict
    0,                                                      // tp_descr_get
    0,                                                      // tp_descr_set
    0,                                                      // tp_dictoffset
    0,                                                      // tp_init
    0,                                                      // tp_alloc
    (newfunc) tp_new,                                       // tp_new
    0,                                                      // tp_free
    0,                                                      // tp_is_gc
};

