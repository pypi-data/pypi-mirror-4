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
#define SELF nodetree_Stream_Object*


static char
tp_doc[] = ".. py:class:: Stream([xml])\n"
"\n"
"    This is a generator class which parses an XML stream into a nodetree\n"
"    :py:class:`Document` such that it can be processed as its being read.\n"
"\n"
"    Document children can be added with the append method and accessed or\n"
"    replaced as items::\n"
"\n"
"        >>> doc = nodetree.Document()\n"
"        >>> doc.append(nodetree.Comment(' Start '))\n"
"        >>> doc.append(nodetree.Element('data'))\n"
"        >>> doc.append(nodetree.Comment(' Fini '))\n"
"        >>> doc[0]\n"
"        <!-- Start -->\n"
"        >>> doc[-1] = nodetree.Comment(' End ')\n"
"        >>> doc\n"
"        <?xml version=\"1.0\"?>\n"
"        <!-- Start -->\n"
"        <data/>\n"
"        <!-- End -->\n"
"\n"
"    You may also parse an existing XML document by passing it as a string\n"
"    argument at instantation::\n"
"\n"
"        >>> doc = nodetree.Document('<!-- Start --><data/><!-- End -->')\n"
"        >>> doc\n"
"        <?xml version=\"1.0\"?>\n"
"        <!-- Start -->\n"
"        <data/>\n"
"        <!-- End -->\n"
"\n"
"    :param string xml: initial XML to be parsed\n"
"\n";


static PyObject*
tp_new (PyTypeObject* type, PyObject* args, PyObject* kwds) {
    SELF self;
    char* data = NULL;
    int size = 0;

    // Ensure no keywords were given
    if (!_PyArg_NoKeywords("Stream", kwds))
        return NULL;

    // Parse just the name
    if (!PyArg_ParseTuple(args, "|s#:Stream", &data, &size)) {
        return NULL;
    }

    // Inherit base type
    self = (SELF) PyType_GenericNew(type, args, kwds);
    if (!self)
      return NULL;

    // Set self->node initially to NULL
    self->node = NULL;

    // Create parser context
    self->ctxt = xmlCreatePushParserCtxt(NULL, NULL, NULL, 0, NULL);

    // Ensure at least 4 bytes are passed to the new parser
    if (size < 4)
        xmlParseChunk(self->ctxt, "    ", 4, 0);

    // Pass initial XML
    xmlParseChunk(self->ctxt, data, size, 0);

    // Link new XML document to this object
    self->node = self->ctxt->myDoc;
    self->node->_private = self;

    // Return self
    return (PyObject*) self;
}


static void
tp_dealloc (SELF self) {
    // If parser context exists, free it
    if (self->ctxt)
        xmlFreeParserCtxt(self->ctxt);

    // Free the XML document if it exists
    //if (self->node)
    //    xmlFreeDoc(self->node);

    // Dealloc base type
    PyObject_Del((PyObject*) self);
}


static PyObject*
tp_repr (SELF self) {
    xmlChar* string;
    int string_size = 1; // 1-1 = 0, see a few lines below
    PyObject* ret;

    // Dump XML for entire document to a string
    if (self->node)
        xmlDocDumpFormatMemory(self->node, &string, &string_size, 1);

    // Convert the returned XML string to a Python return string
    // We're chopping the last \n off the returned string with string_size - 1
    ret = PyUnicode_FromStringAndSize((char*) string, string_size - 1);

    // Free XML string and return the Python string
    xmlFree(string);
    return ret;
}


static PyObject*
tp_str (SELF self) {
    xmlChar* string;
    int string_size = 0;
    PyObject* ret;

    // Dump XML for entire document to a string
    if (self->node)
        xmlDocDumpMemory(self->node, &string, &string_size);

    // Convert the returned XML string to a Python return string
    ret = PyUnicode_FromStringAndSize((char*) string, string_size);

    // Free XML string and return the Python string
    xmlFree(string);
    return ret;
}


/////////////////////////////////////////////////////////////////////////////
// General Methods

static char
close_doc[] = ".. py:method:: Stream.close()\n"
"\n"
"    Close stream parsing.\n"
"\n";

static PyObject*
close_meth (SELF self, PyObject* noargs) {
    int error;

    // Ensure we only terminate the parser once
    if (self->ctxt) {
        // Mark parser for document termination
        error = xmlParseChunk(self->ctxt, NULL, 0, 1);

        // Free parser context
        xmlFreeParserCtxt(self->ctxt);
        self->ctxt = NULL;
    }

    // TODO handle error

    // Returns None on success
    Py_RETURN_NONE;
}


static char
send_doc[] = ".. py:method:: Stream.send(xml)\n"
"\n"
"    Parse additional XML data.\n"
"\n"
"    :param string xml: initial XML to be parsed\n"
"\n";

static PyObject*
send_meth (SELF self, PyObject* args) {
    char* data = NULL;
    int size;
    int error;

    // Parse just the name
    if (!PyArg_ParseTuple(args, "z#:send", &data, &size))
        return NULL;

    // Raise StopIteration if parser has been terminated
    if (!self->ctxt) {
        PyErr_SetString(PyExc_StopIteration, "Stream has been closed");
        return NULL;
    }

    // Pass string as new xml chunk
    error = xmlParseChunk(self->ctxt, data, size, 0);

    // TODO handle XML error

    // Returns None on success
    Py_RETURN_NONE;
}


/////////////////////////////////////////////////////////////////////////////
// Type structs

static PyMethodDef tp_methods[] = {
    {"close",                                              // ml_name
     (PyCFunction) close_meth,                             // ml_meth
     METH_NOARGS,                                          // ml_flags
     close_doc},                                           // ml_doc
    {"send",                                               // ml_name
     (PyCFunction) send_meth,                              // ml_meth
     METH_VARARGS,                                         // ml_flags
     send_doc},                                            // ml_doc
    {NULL},                                                // sentinel
};


PyTypeObject nodetree_Stream_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "nodetree.Stream",                                     // tp_name
    sizeof(nodetree_Stream_Object),                        // tp_basicsize
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
    0,                                                     // tp_getset
    &nodetree_Document_Type,                               // tp_base
    0,                                                     // tp_dict
    0,                                                     // tp_descr_get
    0,                                                     // tp_descr_set
    0,                                                     // tp_dictoffset
    0,                                                     // tp_init
    0,                                                     // tp_alloc
    tp_new,                                                // tp_new
    0,                                                     // tp_free
    0,                                                     // tp_is_gc
};

