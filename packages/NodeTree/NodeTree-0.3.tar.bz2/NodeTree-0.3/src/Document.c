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
#define SELF nodetree_Document_Object*


static int
root_setter (SELF self, PyObject* value, void* closure);


static char
tp_doc[] = ".. py:class:: Document([xml])\n"
"\n"
"    Documents are XML streams which contain one root :py:class:`Element`\n"
"    node and may contain one or more :py:class:`Comment` nodes,\n"
"    :py:class:`ProcessingInstruction` nodes, and other XML nodes types.\n"
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
"    :param string xml: XML to be parsed into new document\n"
"\n";


static PyObject*
tp_new (PyTypeObject* type, PyObject* args, PyObject* kwds) {
    SELF self;
    char* data = NULL;
    int size = 0;

    // Ensure no keywords were given
    if (!_PyArg_NoKeywords("Document", kwds))
        return NULL;

    // Parse the string
    if (!PyArg_ParseTuple(args, "|z#:Document", &data, &size))
        return NULL;

    // Inherit base type
    self = (SELF) PyType_GenericNew(type, args, kwds);
    if (!self)
      return NULL;

    // Set self->node initially to NULL
    self->node = NULL;

    // Parse string if provided
    if (size) {
        xmlParserCtxt* ctxt;

        // Create parser for provided XML string
        ctxt = xmlCreatePushParserCtxt(NULL, NULL, data, size, NULL);

        // Mark parser for document termination
        xmlParseChunk(ctxt, NULL, 0, 1);

        // Link new XML document to this object if it exists
        if (ctxt->myDoc)
            self->node = ctxt->myDoc;

        // Free parser context
        xmlFreeParserCtxt(ctxt);
    }

    // Create empty document if parser didn't create it already
    if (!self->node)
        self->node = xmlNewDoc((xmlChar*) "1.0");

    // Link new XML document to this object
    self->node->_private = self;

    // Return self
    return (PyObject*) self;
}


static void
tp_dealloc (SELF self) {
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
// Sequence Methods

static Py_ssize_t
sq_length (SELF self) {
    // If document node doesn't exist yet, return 0
    if (!self->node)
        return 0;

    // Use child node counter
    return (Py_ssize_t) nodetree_node_Child_Count((xmlNode*) self->node);
}


static PyObject*
sq_item (SELF self, Py_ssize_t index) {
    // Raise error if document node doesn't exist yet
    if (!self->node) {
        PyErr_SetString(PyExc_IndexError, "Child index out of range");
        return NULL;
    }

    // Use child node getter
    return nodetree_node_Child_Get((xmlNode*) self->node, (int) index);
}


static int
sq_ass_item (SELF self, Py_ssize_t index,
             PyObject* value) {
    int i = 0;
    xmlNode* child;
    xmlNode* oldroot;

    // TODO ensure document node exists before trying to use it

    /* Element node handling

        We need to handle Element children specially because only one is
        permitted in a Document (the root node), though comments and other
        types of nodes may also be in a Document.

        libxml also has special handling of root nodes so we get this out of
        the way before handling any other kind of node.

        Note that we must check that value != NULL for del() operations.
    */

    if (value && nodetree_Element_Check(value)) {
        /* Check current root vs new element

            We want to ensure that if there's already a root element, the new
            one will only replace it if its being set to the same position.
            Ie, the behavior is identical to using the Document.root property.

            To not allow this may make some functions more complex than they
            need to be.  Code complexity is better here to keep the API simple.
        */

        oldroot = xmlDocGetRootElement(self->node);
        if (oldroot) {
            // Get first child
            child = self->node->children;

            // Search for oldroot's index in the children list
            while (child) {
                if (child == oldroot)
                    break;
                i++;
                child = child->next;
            }

            // Ensure the new root and old root are at the same index
            if (i != index) {
                PyErr_SetString(PyExc_ValueError,
                                "Document already contains a root Element");
                return -1;
            }
        }

        /* Same position

            The new root node is destined for the same position as the old root
            so its safe to let this fall through and be processed normally.
        */
    }

    /* Filter disallowed node types

        Besides only permitting one root element, certain types of nodes are
        strictly not permitted in a document root.  These need to raise an
        exception instead of being processed as they would being added to an
        Element node.

        After this any remaining node can be processed by nodetree_node_Py2XML.

        Note that we must check that value != NULL for del() operations.
    */

    // Ensure value is not a bytes/string or unicode type (aka text node)
    if (value && (PyUnicode_Check(value) || PyBytes_Check(value))) {
        PyErr_SetString(PyExc_TypeError,
                        "Text nodes can only be added to an Element node.");
        return -1;
    }

    // Use child node setter
    return nodetree_node_Child_Set((xmlNode*) self->node, (int) index, value);
}


static int
sq_contains (SELF self, PyObject* value) {
    xmlNode* child;
    nodetree_node* next;

    // False if document node doesn't exist yet
    if (!self->node)
        return 0;

    // Documents only have one root Element, so this is easy to check
    if (nodetree_Element_Check(value)) {
        child = xmlDocGetRootElement(self->node);

        // Check first node
        child = ((nodetree_Element_Object*) value)->node;
        if (child)
            return 1;

        // Then search node list for a match
        next = ((nodetree_Element_Object*) value)->next;
        while (next) {
            child = next->node;
            if (child)
                return 1;
            next = (nodetree_node*) next->next;
        }

        // Element was not found
        return 0;
    }

    // TODO Check for other types of nodes

    // Unrecognized value types are never contained in a NodeTree Document
    return 0;
}


/////////////////////////////////////////////////////////////////////////////
// General Methods

static char
append_doc[] = ".. py:method:: Document.append(node)\n"
"\n"
"    This method can be used to add a child node to the document.\n"
"\n"
"    While an XML document may only have one root :py:class:`Element`\n"
"    node, :py:class:`Comment` and :py:class:`ProcessingInstruction`\n"
"    nodes may be added before and/or after the root element.\n"
"\n"
"    Attempting to append a node which would break XML specification\n"
"    will raise an exception::\n"
"\n"
"        >>> doc = nodetree.Document()\n"
"        >>> doc.append(nodetree.Comment(' Before '))\n"
"        >>> doc.append(nodetree.Element('library')) # Root element\n"
"        >>> doc.append(nodetree.Comment(' After '))\n"
"        >>> doc.append('text node')\n"
"        Traceback (most recent call last):\n"
"            ...\n"
"        TypeError: Text nodes can only be added to an Element node.\n"
"        >>> doc.append(nodetree.Element('collection'))\n"
"        Traceback (most recent call last):\n"
"            ...\n"
"        ValueError: Document already contains a root Element\n"
"        >>> doc\n"
"        <?xml version=\"1.0\"?>\n"
"        <!-- Before -->\n"
"        <library/>\n"
"        <!-- After -->\n"
"\n"
"    :param node: node to be added to the document\n"
"\n";


static PyObject*
append_meth (SELF self, PyObject* args) {
    PyObject* item;
    xmlNode* child;

    // Parse argument tuple for single item
    if (!PyArg_ParseTuple(args, "O", &item)) {
        return NULL;
    }

    /* Element node handling

        We need to handle Element children specially because only one is
        permitted in a Document (the root node), though comments and other
        types of nodes may also be in a Document.

        libxml also has special handling of root nodes so we get this out of
        the way before handling any other kind of node.
    */

    if (nodetree_Element_Check(item)) {
        /* Root node replacement not allowed with Document.append

            We do not allow appending an element when there's already a root
            node in a document because doing so would "magically" remove the
            old root from its location changing the ordering in a non-intuitive
            manner.  Ie, appending should always increase the length of a
            sequence, and allowing this would make that not the case.

            "Explicit is better than implicit."

            The Document.root property is provided for this reason.
        */

        if (xmlDocGetRootElement(self->node)) {
            PyErr_SetString(PyExc_ValueError,
                            "Document already contains a root Element");
            return NULL;
        }

        // If there is not already a root node, this behaves exactly like using
        // the Document.root property, so we just call that code directly.
        if (root_setter(self, item, NULL) == -1)
            return NULL;

        // Returns None on success
        Py_RETURN_NONE;
    }

    /* Filter disallowed node types

        Besides only permitting one root element, certain types of nodes are
        strictly not permitted in a document root.  These need to raise an
        exception instead of being processed as they would being added to an
        Element node.

        After this any remaining node can be processed by nodetree_node_Py2XML.
    */

    // Ensure value is not a bytes/string or unicode type (aka text node)
    if (PyUnicode_Check(item) || PyBytes_Check(item)) {
        PyErr_SetString(PyExc_TypeError,
                        "Text nodes can only be added to an Element node.");
        return NULL;
    }

    // Get new child node
    child = nodetree_node_Py2XML(item);

    // Return exception NULL was returned by nodetree_node_Py2XML
    if (!child)
        return NULL;

    // Add child to end of children list
    child = xmlAddChild((xmlNode*) self->node, child);

    // Raise exception if this fails for some reason
    if (!child) {
        PyErr_SetString(PyExc_ValueError, "error appending child");
        return NULL;
    }

    // Returns None on success
    Py_RETURN_NONE;
}


static char
pop_doc[] = ".. py:method:: Document.pop([index])\n"
"\n"
"    Remove child node by index.\n"
"\n"
"    :param int index: index of target child (defaults to last)\n"
"    :returns: removed child node\n"
"\n";

static PyObject*
pop_meth (SELF self, PyObject* args) {
    int index = -1;
    xmlNode* item;
    PyObject* child;

    // Parse item as single argument
    if (!PyArg_ParseTuple(args, "|i", &index)) {
        return NULL;
    }

    // Ensure there's at least one child
    if (self->node->children == NULL) {
        PyErr_SetString(PyExc_IndexError, "pop from empty Document");
        return NULL;
    }

    // Get either last child node or child node by index
    if (index == -1)
        item = self->node->last;
    else
        item = nodetree_node_Child_Index((xmlNode*) self->node, index);

    // Raise exception if child node wasn't found
    if (!item) {
        PyErr_SetString(PyExc_IndexError, "child index out of range");
        return NULL;
    }

    // Check if this is an active stream
    if (nodetree_Stream_Check(self) &&
        ((nodetree_Stream_Object*) self)->ctxt) {
        // We need to make sure the node being popped is not part of the
        // branch currently being parsed by the stream
        xmlNode* current = ((nodetree_Stream_Object*) self)->ctxt->node;

        // Walk up tree ensuring no ancestor of current node is our item
        while (current && current != (xmlNode*) self->node) {
            if (current == item) {
                PyErr_SetString(PyExc_ValueError, "incomplete branch");
                return NULL;
            }
            current = current->parent;
        }

    }

    // Get child object for item
    child = nodetree_node_Create(item);

    // Prune child
    nodetree_node_Prune(item);

    // Return popped child
    return child;
}


/////////////////////////////////////////////////////////////////////////////
// Properties

static char
root_doc[] = ".. py:attribute:: Document.root\n"
"\n"
"    While XML requires only one root :py:class:`Element` per document,\n"
"    it is not guarenteed to be the first child node of a document.\n"
"\n"
"    This property provides easy access to the root element regardless\n"
"    of its position in the document.\n"
"\n"
"    This property may be used to replace the root element in-place or\n"
"    delete the old root before adding a new root element::\n"
"\n"
"        >>> doc = nodetree.Document()\n"
"        >>> doc.append(nodetree.Comment(' Start '))\n"
"        >>> doc.append(nodetree.Element('catalog'))\n"
"        >>> doc.append(nodetree.Comment(' End '))\n"
"        >>> doc.root\n"
"        <catalog/>\n"
"        >>> doc.root = nodetree.Element('library')\n"
"        >>> doc\n"
"        <?xml version=\"1.0\"?>\n"
"        <!-- Start -->\n"
"        <library/>\n"
"        <!-- End -->\n"
"        >>> del(doc.root)\n"
"        >>> doc.root = nodetree.Element('collection')\n"
"        >>> doc\n"
"        <?xml version=\"1.0\"?>\n"
"        <!-- Start -->\n"
"        <!-- End -->\n"
"        <collection/>\n"
"\n";


static PyObject*
root_getter (SELF self, void* closure) {
    xmlNode* root;

    // Get root element from libxml2
    root = xmlDocGetRootElement(self->node);

    // Return None if there isn't one
    if (!root)
        Py_RETURN_NONE;

    // Incref existing Element object if there is one
    if (root->_private)
        return Py_INCREF(root->_private), root->_private;

    // Create a new Element object to wrap the node for Python
    return (PyObject*) nodetree_Element_Create(root);
}


static int
root_setter (SELF self, PyObject* value, void* closure) {
    nodetree_Element_Object* element = (void*) value; // for code simplicity
    xmlNode* root;

    // Handle del(document.root) and document.root = None calls
    if (!value || value == Py_None) {
        root = xmlDocGetRootElement(self->node);

        // Prune oldroot if currently set
        if (root)
            nodetree_node_Prune(root);

        // Always succeeds
        return 0;
    }

    // Ensure value is an Element
    if (!nodetree_Element_Check(value)) {
        PyErr_SetString(PyExc_TypeError, "root attribute must be an Element");
        return -1;
    }

    // Check to see if Element's primary node is in use
    if (element->node->parent)
        nodetree_node_Copy(element->node);

    // This function returns the old root element (or NULL if none)
    root = xmlDocSetRootElement(self->node, element->node);

    // Clean up old root if necessary
    if (root)
        nodetree_node_Prune(root);

    // Return success
    return 0;
}


/////////////////////////////////////////////////////////////////////////////
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
    {"root",
     (getter) root_getter,
     (setter) root_setter,
     root_doc,
     NULL},
    {NULL},                                                // sentinel
};


PyTypeObject nodetree_Document_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "nodetree.Document",                                   // tp_name
    sizeof(nodetree_Document_Object),                      // tp_basicsize
    0,                                                     // tp_itemsize
    (destructor) tp_dealloc,                               // tp_dealloc
    0,                                                     // RESERVED
    (getattrfunc) 0,                                       // tp_getattr
    (setattrfunc) 0,                                       // tp_setattr
    0,                                                     // RESERVED
    (reprfunc) tp_repr,                                    // tp_repr
    0,                                                     // tp_as_number
    &tp_as_sequence,                                       // tp_as_sequence
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
    tp_new,                                                // tp_new
    0,                                                     // tp_free
    0,                                                     // tp_is_gc
};

