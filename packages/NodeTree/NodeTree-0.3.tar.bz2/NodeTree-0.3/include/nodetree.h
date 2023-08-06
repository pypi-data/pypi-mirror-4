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


#ifndef __NODETREE_H__
#define __NODETREE_H__

#include <Python.h>
#include <structmember.h>
#include <libxml/SAX2.h>
#include <libxml/tree.h>

/////////////////////////////////////////////////////////////////////////////
// nodetree Node functions (node.c)
//
//  Node functions not exposed to the Python API but are used internally by
//  NodeTree to parse XML, maintain the XML tree, and avoid duplicating code.

PyObject* nodetree_node_Create (xmlNode* node);
xmlNode* nodetree_node_Copy (xmlNode* node);
xmlNode* nodetree_node_Py2XML (PyObject* item);
void nodetree_node_Prune (xmlNode* node);
int nodetree_node_Child_Count (xmlNode* node);
xmlNode* nodetree_node_Child_Index (xmlNode* node, int index);
PyObject* nodetree_node_Child_Get (xmlNode* node, int index);
int nodetree_node_Child_Set(xmlNode* node, int index, PyObject* value);

// NodeTree Python object may coorespond to multiple XML nodes in the same
// or separate documents, so to handle this we store them as a linked list with
// the following struct.
//
// The first node is stored directly in the Python object as the most common
// use is for one Python object to coorespond to one XML node, in which case
// the *_Object->next will be NULL and the following struct not needed.

typedef struct _nodetree_node nodetree_node;

struct _nodetree_node {
    xmlNode* node;
    struct _nodetree_node* next;
};

//
/////////////////////////////////////////////////////////////////////////////
// nodetree._Attributes

PyTypeObject nodetree__Attributes_Type;
typedef struct {
    PyObject_HEAD
    PyObject* element;
} nodetree__Attributes_Object;
#define nodetree__Attributes_Check(op) \
    PyObject_TypeCheck(op, &nodetree__Attributes_Type)
nodetree__Attributes_Object* nodetree__Attributes_Create (PyObject* node);

//
/////////////////////////////////////////////////////////////////////////////
// nodetree.Comment
//
// Comment nodes contain a string.  They may be added to Document and Element
// nodes and do not contain any other nodes.

PyTypeObject  nodetree_Comment_Type;
typedef struct {
    PyObject_HEAD
    xmlNode* node;
    nodetree_node* next;
} nodetree_Comment_Object;
#define nodetree_Comment_Check(op) \
    PyObject_TypeCheck(op, &nodetree_Comment_Type)
PyObject* nodetree_Comment_Create (xmlNode* node);

//
/////////////////////////////////////////////////////////////////////////////
// nodetree.Document
//
// Documents are a kind of node, however, they may never be added to another
// type of node we never need to have more than one copy of them, so we have
// no need for a ->next member to store copies.

PyTypeObject  nodetree_Document_Type;
typedef struct {
    PyObject_HEAD
    xmlDoc* node;
} nodetree_Document_Object;
#define nodetree_Document_Check(op) \
    PyObject_TypeCheck(op, &nodetree_Document_Type)

//
/////////////////////////////////////////////////////////////////////////////
// nodetree.Element

PyTypeObject nodetree_Element_Type;
typedef struct {
    PyObject_HEAD
    xmlNode* node;
    nodetree_node* next;
    nodetree__Attributes_Object* attributes;
} nodetree_Element_Object;
#define nodetree_Element_Check(op) \
    PyObject_TypeCheck(op, &nodetree_Element_Type)
nodetree_Element_Object* nodetree_Element_Create (xmlNode* node);

//
/////////////////////////////////////////////////////////////////////////////
// nodetree.ProcessingInstruction

PyTypeObject nodetree_ProcessingInstruction_Type;
typedef struct {
    PyObject_HEAD
    xmlNode* node;
    nodetree_node* next;
} nodetree_ProcessingInstruction_Object;
#define nodetree_ProcessingInstruction_Check(op) \
    PyObject_TypeCheck(op, &nodetree_ProcessingInstruction_Type)
nodetree_ProcessingInstruction_Object*
nodetree_ProcessingInstruction_Create (xmlNode* node);

//
/////////////////////////////////////////////////////////////////////////////
// nodetree.Stream
//
// Streams are Document nodes which are parsed asynchronously.

PyTypeObject  nodetree_Stream_Type;
typedef struct {
    PyObject_HEAD
    xmlDoc* node;
    xmlParserCtxt* ctxt;
} nodetree_Stream_Object;
#define nodetree_Stream_Check(op) \
    PyObject_TypeCheck(op, &nodetree_Stream_Type)

//
/////////////////////////////////////////////////////////////////////////////

#endif /* __NODETREE_H__ */

