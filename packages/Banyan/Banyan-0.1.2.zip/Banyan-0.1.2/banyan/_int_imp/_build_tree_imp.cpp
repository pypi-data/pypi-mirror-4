#include <Python.h>

#include "rank_metadata.hpp"
#include "min_gap_metadata.hpp"
#include "_int_int/_tree_imp_base.hpp"
#include "_int_imp/_build_tree_imp.hpp"
#include "_int_imp/_pyobject_utils.hpp"
#include "_int_imp/_set_tree_imp.hpp"
#include "_int_imp/_dict_tree_imp.hpp"

using namespace std;

template<
    class Alg_Tag,
    typename Key_Type, 
    bool Set,
    class MetadataTag,
    class LT>
struct _KnownMappingBuilder
{
    // Nothing.
};

template<
    class Alg_Tag,
    typename Key_Type, 
    class MetadataTag,
    class LT>
struct _KnownMappingBuilder<
    Alg_Tag,
    Key_Type,
    false,
    MetadataTag,
    LT>
{
    static _TreeImpBase *
    build_imp(PyObject * seq, PyObject * metadata, PyObject * lt)
    {    
        return new _DictTreeImp<
            Alg_Tag, 
            Key_Type, 
            MetadataTag, 
            LT>(seq, metadata, lt);
    }
};

template<
    class Alg_Tag,
    typename Key_Type,
    class MetadataTag,
    class LT>
struct _KnownMappingBuilder<
    Alg_Tag,
    Key_Type,
    true,
    MetadataTag,
    LT>
{
    static _TreeImpBase *
    build_imp(PyObject * seq, PyObject * metadata, PyObject * lt)
    {
        return new _SetTreeImp<
            Alg_Tag, 
            Key_Type, 
            MetadataTag, 
            LT>(seq, metadata, lt);
    }
};

template<
    class Alg_Tag,
    class Key_Type,
    class MetadataTag,
    class LT>   
struct _KnownMetadataBuilder
{
    static _TreeImpBase *
    build_imp(PyObject * seq, int mapping, PyObject * lt)
    {
        if (mapping == 0)
            return _KnownMappingBuilder<Alg_Tag, Key_Type, false, MetadataTag, LT>::build_imp(
                seq, NULL, lt);
        if (mapping == 1)            
            return _KnownMappingBuilder<Alg_Tag, Key_Type, true, MetadataTag, LT>::build_imp(
                seq, NULL, lt);
        DBG_VERIFY(false);
        return (_TreeImpBase *)NULL;
    }
};

template<
    class Alg_Tag,
    class Key_Type,
    class LT>   
struct _KnownMetadataBuilder<
    Alg_Tag,
    Key_Type,
    _PyObjectCBMetadataTag,
    LT>
{
    static _TreeImpBase *
    build_imp(PyObject * seq, int mapping, PyObject * metadata, PyObject * lt)
    {
        if (mapping == 0)
            return _KnownMappingBuilder<Alg_Tag, Key_Type, false, _PyObjectCBMetadataTag, LT>::build_imp(
                seq, metadata, lt);
        if (mapping == 1)            
            return _KnownMappingBuilder<Alg_Tag, Key_Type, true, _PyObjectCBMetadataTag, LT>::build_imp(
                seq, metadata, lt);
        DBG_VERIFY(false);
        return (_TreeImpBase *)NULL;
    }
};

template<
    class Alg_Tag,
    class Key_Type,
    class LT>   
struct _KnownLTBuilder
{
    static _TreeImpBase *
    build_imp(PyObject * seq, int mapping, PyObject * metadata, PyObject * lt)
    {
        if (metadata == Py_None)
            return _KnownMetadataBuilder<Alg_Tag, Key_Type, _NullMetadataTag, LT>::build_imp(
                seq, mapping, lt);                
        DBG_ASSERT(metadata != NULL && PyTuple_Check(metadata) && PyTuple_Size(metadata) == 2);        

        PyObject * const meta = PyTuple_GET_ITEM(metadata, 0);
        DBG_ASSERT(PyCallable_Check(meta));
        DBG_ASSERT(PyType_Check(meta));
        PyObject * const inst = PyObject_CallFunctionObjArgs(meta, NULL);        
        if (inst == NULL) {
            PyErr_NoMemory();
            return NULL;
        }        
        BANYAN_PYOBJECT_DUMMY_INCREF(inst);            
        if (PyObject_TypeCheck(inst, &RankMetadataType)) {
            BANYAN_PYOBJECT_DECREF(inst);
            return _KnownMetadataBuilder<Alg_Tag, Key_Type, _RankMetadataTag, LT>::build_imp(
                seq, mapping, lt);                
        }
        if (PyObject_TypeCheck(inst, &MinGapMetadataType)) {
            BANYAN_PYOBJECT_DECREF(inst);
            return _KnownMetadataBuilder<Alg_Tag, Key_Type, _MinGapMetadataTag, LT>::build_imp(
                seq, mapping, lt);                
        }

        BANYAN_PYOBJECT_DECREF(inst);
        return _KnownMetadataBuilder<Alg_Tag, Key_Type, _PyObjectCBMetadataTag, LT>::build_imp(
            seq, mapping, metadata, lt);                
    }            
};

template<
    class Alg_Tag,
    class Key_Type>
struct _KnownKeyTypeBuilder
{
    static _TreeImpBase *
    build_imp(PyObject * seq, int mapping, PyObject * metadata)
    {
        if (metadata == Py_None)
            return _KnownMetadataBuilder<Alg_Tag, Key_Type, _NullMetadataTag, std::less<Key_Type> >::build_imp(
                seq, mapping, NULL);
        DBG_ASSERT(metadata != NULL && PyTuple_Check(metadata) && PyTuple_Size(metadata) == 2);        

        PyObject * const meta = PyTuple_GET_ITEM(metadata, 0);
        DBG_ASSERT(PyCallable_Check(meta));
        DBG_ASSERT(PyType_Check(meta));
        PyObject * const inst = PyObject_CallFunctionObjArgs(meta, NULL);        
        if (inst == NULL) {
            PyErr_NoMemory();
            return NULL;
        }        
        BANYAN_PYOBJECT_DUMMY_INCREF(inst);            
        if (PyObject_TypeCheck(inst, &RankMetadataType)) {
            BANYAN_PYOBJECT_DECREF(inst);
            return _KnownMetadataBuilder<Alg_Tag, Key_Type, _RankMetadataTag, std::less<Key_Type> >::build_imp(
                seq, mapping, NULL);                
        }
        if (PyObject_TypeCheck(inst, &MinGapMetadataType)) {
            BANYAN_PYOBJECT_DECREF(inst);
            return _KnownMetadataBuilder<Alg_Tag, Key_Type, _MinGapMetadataTag, std::less<Key_Type> >::build_imp(
                seq, mapping, NULL);                
        }

        BANYAN_PYOBJECT_DECREF(inst);
        return _KnownMetadataBuilder<Alg_Tag, Key_Type, _PyObjectCBMetadataTag, std::less<Key_Type> >::build_imp(
            seq, mapping, metadata, NULL);                
    }
};

template<
    class Alg_Tag>
struct _KnownKeyTypeBuilder<
    Alg_Tag,
    PyObject *>
{
    static _TreeImpBase *
    build_imp(PyObject * seq, int mapping, PyObject * metadata, PyObject * key, PyObject * cmp)
    {
        DBG_ASSERT(key == Py_None || cmp == Py_None);
#if PY_MAJOR_VERSION >= 3
        if (cmp != Py_None) {
            const int warn_res = PyErr_WarnEx(
                PyExc_DeprecationWarning, "cmp function deprecated in favour of key function", 1);            
                
            if (warn_res == -1)      
                throw runtime_error("warning threw");              
        }                           
#endif // #if PY_MAJOR_VERSION >= 3

        // Tmp Ami - who checks if callable? Should not be in assert.
        if (key != Py_None) 
            return _KnownLTBuilder<Alg_Tag, PyObject *, _PyObjectKeyCBLT>::build_imp(
                seq, mapping, metadata, key);
        if (cmp != Py_None)
            return _KnownLTBuilder<Alg_Tag, PyObject *, _PyObjectCmpCBLT>::build_imp(
                seq, mapping, metadata, cmp);
        return _KnownLTBuilder<Alg_Tag, PyObject *, _PyObjectStdLT>::build_imp(
            seq, mapping, metadata, NULL);
    }
};

template<
    class Alg_Tag>
struct _KnownAlgBuilder
{
    static _TreeImpBase *
    build_imp(
        PyObject * seq,
        PyObject * KeyType, 
        int mapping, 
        PyObject * metadata,
        PyObject * key, 
        PyObject * cmp)
    {
        if (KeyType == Py_None) 
            return _KnownKeyTypeBuilder<Alg_Tag, PyObject *>::build_imp(seq, mapping, metadata, key, cmp);

        DBG_ASSERT(key == Py_None);            
        DBG_ASSERT(cmp == Py_None);            
        DBG_ASSERT(PyType_Check(KeyType));

        PyObject * const inst = PyObject_CallFunctionObjArgs(KeyType, NULL);
        BANYAN_PYOBJECT_DUMMY_INCREF(inst);
        if (inst == NULL) {
            BANYAN_PYOBJECT_DECREF(inst);
            return _KnownKeyTypeBuilder<Alg_Tag, PyObject *>::build_imp(seq, mapping, metadata, key, cmp);
        }
        
#if PY_MAJOR_VERSION >= 3
        if (PyLong_CheckExact(inst)) {
#else // #if PY_MAJOR_VERSION >= 3
        if (PyInt_CheckExact(inst)) {
#endif // #if PY_MAJOR_VERSION >= 3
            BANYAN_PYOBJECT_DECREF(inst);
            return _KnownKeyTypeBuilder<Alg_Tag, long>::build_imp(seq, mapping, metadata);
        }
        if (PyFloat_CheckExact(inst)) {
            BANYAN_PYOBJECT_DECREF(inst);
            return _KnownKeyTypeBuilder<Alg_Tag, double>::build_imp(seq, mapping, metadata);
        }            
#if PY_MAJOR_VERSION >= 3
        if (PyByteArray_CheckExact(inst)) {
#else // #if PY_MAJOR_VERSION >= 3
        if (PyString_CheckExact(inst)) {       
#endif // #if PY_MAJOR_VERSION >= 3
            BANYAN_PYOBJECT_DECREF(inst);
            return _KnownKeyTypeBuilder<Alg_Tag, String>::build_imp(seq, mapping, metadata);
        }            
        if (PyUnicode_CheckExact(inst)) {
            BANYAN_PYOBJECT_DECREF(inst);                   
            return _KnownKeyTypeBuilder<Alg_Tag, UnicodeString>::build_imp(seq, mapping, metadata);
        }            

        BANYAN_PYOBJECT_DECREF(inst);
        return _KnownKeyTypeBuilder<Alg_Tag, PyObject *>::build_imp(seq, mapping, metadata, key, cmp);
    }    
};

_TreeImpBase *
_build_tree_imp(
    int alg, 
    PyObject * seq,
    PyObject * KeyType, 
    int mapping,
    PyObject * metadata, 
    PyObject * key,
    PyObject * cmp)
{
    if (alg == 0)
        return _KnownAlgBuilder<_RBTreeTag>::build_imp(seq, KeyType, mapping, metadata, key, cmp);
    if (alg == 1)
        return _KnownAlgBuilder<_SplayTreeTag>::build_imp(seq, KeyType, mapping, metadata, key, cmp);
    if (alg == 2)
        return _KnownAlgBuilder<_OVTreeTag>::build_imp(seq, KeyType, mapping, metadata, key, cmp); 
    DBG_VERIFY(false);        
    return (_TreeImpBase *)NULL;
}

