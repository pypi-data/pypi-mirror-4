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


/* Create a new NodeTree node object

    This creates a new Python object to wrap a given XML node based on its type
*/
PyObject*
nodetree_node_Create (xmlNode* node) {
    // Return existing node if available
    if (node->_private)
        return Py_INCREF(node->_private), node->_private;

    // Otherwise create a new node object
    switch (node->type) {
        case XML_ELEMENT_NODE :
            return (PyObject*) nodetree_Element_Create(node);

        case XML_TEXT_NODE :
            return PyUnicode_FromString((char*) node->content);

        case XML_COMMENT_NODE :
            return nodetree_Comment_Create(node);

        case XML_PI_NODE :
            return (PyObject*) nodetree_ProcessingInstruction_Create(node);

        default :
            Py_RETURN_NONE;
    }
}


/* Copy a node, keeping associated Python objects in sync

    Whenever a linked (has a parent/siblings) node is added to a new parent a
    copy of the XML node needs to be made and the node list updated.

    This can be used on any NodeTree Python Object which can be added to a
    parent node, not just Element, as these all use the same object struct.
*/
xmlNode*
nodetree_node_Copy (xmlNode* node) {
    nodetree_Element_Object* self = (void*) node->_private;
    nodetree_node* next;
    xmlNode* copy;
    xmlNode* child;
    xmlNode* ccopy;

    // Copy node - its not quite this easy, but this is a start
    copy = xmlCopyNode(node, 2);

    // If there's an associated Python object, update the linked list
    if (self) {
        // Allocate and populate a new Node struct
        // We're prepending node list so we can use the new primary node next
        next = PyMem_Malloc(sizeof(nodetree_node));
        next->node = self->node;
        next->next = self->next;

        // Copy current primary node as new primary node, store next struct
        self->node = copy;
        self->next = next;
    }

    // All magic has a price, this one owes its first born
    child = node->children;

    // Copy each child recursively
    while (child) {
        ccopy = nodetree_node_Copy(child);

        // Link child to new node
        xmlAddChild(copy, ccopy);

        // Get the next child to be cloned
        child = child->next;
    }

    // Return the copy, used recursively for linking
    return copy;
}


/* PyObject to XML
    This function takes a Python object and returns an xmlNode for it based
    on its type.
*/
xmlNode*
nodetree_node_Py2XML (PyObject* item) {
    xmlNode* ret = NULL;

    // First step processing for unicode items
    if (PyUnicode_Check(item)) {
        // Encode unicode string as UTF-8 bytes object
        item = PyUnicode_AsUTF8String(item);
    } else if (PyBytes_Check(item)) {
        // If string/bytes was originally passed in, incref for decref below
        Py_INCREF(item);
    }

    // Handle text nodes
    if (PyBytes_Check(item)) {
        ret = xmlNewTextLen((xmlChar*) PyBytes_AsString(item), PyBytes_Size(item));
        Py_DECREF(item);  // We're done with this

        if (!ret) {
            PyErr_SetString(PyExc_ValueError, "error creating text node");
            return NULL;
        }
    }

    // Handle element nodes
    else if (nodetree_Element_Check(item)) {
        // Check to see if Element's primary node is in use
        if (((nodetree_Element_Object*) item)->node->parent) {
            // It is, so make a copy of it which becomes the new primary node
            nodetree_node_Copy(((nodetree_Element_Object*) item)->node);
        }

        // Use the child's primary node
        ret = ((nodetree_Element_Object*) item)->node;
    }

    // Handle comment nodes
    else if (nodetree_Comment_Check(item)) {
        // Check to see if Element's primary node is in use
        if (((nodetree_Comment_Object*) item)->node->parent) {
            // It is, so make a copy of it which becomes the new primary node
            nodetree_node_Copy(((nodetree_Comment_Object*) item)->node);
        }

        // Use the child's primary node
        ret = ((nodetree_Comment_Object*) item)->node;
    }

    // Handle processing instruction nodes
    else if (nodetree_ProcessingInstruction_Check(item)) {
        // Check to see if ProcessingInstruction's primary node is in use
        if (((nodetree_ProcessingInstruction_Object*) item)->node->parent) {
            // It is, so make a copy of it which becomes the new primary node
            nodetree_node_Copy(((nodetree_ProcessingInstruction_Object*) item)
                               ->node);
        }

        // Use the child's primary node
        ret = ((nodetree_ProcessingInstruction_Object*) item)->node;
    }
    // Unrecognized type
    else
        PyErr_SetString(PyExc_TypeError, "Unsupported XML type");

    // Return node
    return ret;
}


/* Prune an XML branch

    This function frees a node and all of its children which do not have Python
    objects holding them.  If a Python object does hold the child node and its
    the only one its unlinked from its parent and kept for data storage, if a
    child node is held by a Python object but is redundant its removed from the
    Python object's list of nodes and freed along with its children.
*/
void
nodetree_node_Prune (xmlNode* node) {
    nodetree_Element_Object* self;
    nodetree_node* next;
    nodetree_node* after;
    xmlNode* child = NULL;

    // If the node is held by a Python object
    if (node->_private) {
        // This works for all Python nodes, not just Element
        self = (nodetree_Element_Object*) node->_private;

        // This three-part conditional removes the specified node from the
        // Python object's list of nodes.  Copies of the node held by other
        // Python objects will be maintained.

        // If this is the primary node
        if (node == self->node) {
            // If there's more, bump the next into the primary slot and free it
            if (self->next) {
                next = self->next;
                self->node = next->node;
                self->next = next->next;
                PyMem_Free(next);
            }
        }

        // If this is the secondary node
        else if (node == self->next->node) {
            // Bump 2nd non-primary into first non-primary slot, free it
            next = self->next;
            self->next = next->next;
            PyMem_Free(next);
        }

        // Else this needs to be searched for in the self->next node chain
        else {
            next = self->next;
            while (next->next) {
                // We're actually looking at "after"
                after = next->next;

                // When we find it, bump what's after it forward and free
                if (node == after->node) {
                    next->next = after->next;
                    PyMem_Free(after);
                    break;
                }

                // Not found, continue to next in chain
                next = after;
            }
        }

        // Unlink the specified node from its parents and siblings
        xmlUnlinkNode(node);

        // If there's a copy of the node, free it
        if (node != self->node) {
            // Walk through the children, unlinking those with Python objects
            child = node->children;
            while (child) {
                nodetree_node_Prune(child);
                child = child->next;
            }

            // We can now safely free this node
            xmlFreeNode(node);
        }
    }

    // This node is not held by a Python object, recursively unlink/free it
    else {
        // Unlink the specified node from its parents and siblings
        xmlUnlinkNode(node);

        // Walk through children, unlinking those with Python objects
        child = node->children;
        while (child) {
            nodetree_node_Prune(child);
            child = child->next;
        }

        // Now free this node
        xmlFreeNode(node);
    }
}


/* Count child nodes

    This returns the number of children a specified node contains.
*/
int
nodetree_node_Child_Count (xmlNode* node) {
    int length = 0;
    xmlNode* child = node->children;  // Get first child node

    // Walk node list to determine its length
    while (child) {
        child = child->next;
        length++;
    }

    return length;
}


/* Get child node by index

    This function returns the xmlNode for a specified child offset or NULL.
*/
xmlNode*
nodetree_node_Child_Index (xmlNode* node, int index) {
    int i = 0;
    xmlNode* child = node->children;

    // Iterate over list of children, breaking if an index match is found
    while (child) {
        // Check against index
        if (i == index)
            // This will cause child != NULL below
            break;
        child = child->next;
        i++;
    }

    // Return child if index is in range, otherwise NULL
    return child;
}


/* Get Python object representing a child node

    Returns either an existing Python object wrapping a specified XML node
    or creates a new one.
*/
PyObject*
nodetree_node_Child_Get (xmlNode* node, int index) {
    xmlNode* child;
    PyObject* ret = NULL;

    // Get child by index
    child = nodetree_node_Child_Index(node, index);

    // If the index was in range
    if (child) {
        // Create a new PyObject based on the type of node to return
        ret = nodetree_node_Create(child);
    }
    else {
        // Set exception if index wasn't found
        PyErr_SetString(PyExc_IndexError, "Child index out of range");
    }

    // Return Python object or NULL
    return ret;
}


int
nodetree_node_Child_Set(xmlNode* node, int index, PyObject* value) {
    int i = 0;
    xmlNode* child;
    xmlNode* newchild;

    // Get first child
    child = node->children;

    // Iterate over list of children, breaking if an index match is found
    while (child) {
        // Check against index
        if (i == index)
            // This will cause child != NULL below
            break;
        child = child->next;
        i++;
    }

    // Ensure index was found
    if (!child) {
        // Raise exception
        PyErr_SetString(PyExc_IndexError, "Child index out of range");
        return -1;
    }

    if (value) {
        // Get new child node from value
        newchild = nodetree_node_Py2XML(value);

        // Raise exception if NULL was returned from nodetree_node_Py2XML
        if (!newchild)
            return -1;

        // Replace old node with new one, prune old node
        xmlReplaceNode(child, newchild);
        nodetree_node_Prune(child);
    }
    else {
        // Handle del(node[index]) calls
        nodetree_node_Prune(child);
    }

    // Success
    return 0;
}

