#include <Python.h>

#include "_build_tree_imp.hpp"
#include "_tree_imp_base.hpp"
#include "_set_tree_imp.hpp"
#include "_dict_tree_imp.hpp"
#include "_pyobject_utils.hpp"

using namespace std;

template<
    class Alg_Tag,
    typename Key_Type, 
    bool Set,
    class Metadata,
    class LT>
struct _KnownMappingBuilder
{
    // Nothing.
};

template<
    class Alg_Tag,
    typename Key_Type, 
    class Metadata,
    class LT>
struct _KnownMappingBuilder<
    Alg_Tag,
    Key_Type,
    false,
    Metadata,
    LT>
{
    static _TreeImpBase *
    build_imp(PyObject * seq, PyObject * metadata, PyObject * lt)
    {    
        return new _DictTreeImp<
            Alg_Tag, 
            Key_Type, 
            Metadata, 
            LT>(seq, metadata, lt);
    }
};

template<
    class Alg_Tag,
    typename Key_Type,
    class Metadata,
    class LT>
struct _KnownMappingBuilder<
    Alg_Tag,
    Key_Type,
    true,
    Metadata,
    LT>
{
    static _TreeImpBase *
    build_imp(PyObject * seq, PyObject * metadata, PyObject * lt)
    {
        return new _SetTreeImp<
            Alg_Tag, 
            Key_Type, 
            Metadata, 
            LT>(seq, metadata, lt);
    }
};

template<
    class Alg_Tag,
    class Key_Type,
    class Metadata,
    class LT>   
struct _KnownMetadataBuilder
{
    // Nothing.
};    

template<
    class Alg_Tag,
    class Key_Type,
    class LT>   
struct _KnownMetadataBuilder<
    Alg_Tag,
    Key_Type,
    _NullMetadata,
    LT>
{
    static _TreeImpBase *
    build_imp(PyObject * seq, int mapping, PyObject * lt)
    {
        if (mapping == 0)
            return _KnownMappingBuilder<Alg_Tag, Key_Type, false, _NullMetadata, LT>::build_imp(
                seq, NULL, lt);
        if (mapping == 1)            
            return _KnownMappingBuilder<Alg_Tag, Key_Type, true, _NullMetadata, LT>::build_imp(
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
    _PyObjectCBMetadata,
    LT>
{
    static _TreeImpBase *
    build_imp(PyObject * seq, int mapping, PyObject * metadata, PyObject * lt)
    {
        if (mapping == 0)
            return _KnownMappingBuilder<Alg_Tag, Key_Type, false, _PyObjectCBMetadata, LT>::build_imp(
                seq, metadata, lt);
        if (mapping == 1)            
            return _KnownMappingBuilder<Alg_Tag, Key_Type, true, _PyObjectCBMetadata, LT>::build_imp(
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
            return _KnownMetadataBuilder<Alg_Tag, Key_Type, _NullMetadata, LT>::build_imp(
                seq, mapping, lt);
        return _KnownMetadataBuilder<Alg_Tag, Key_Type, _PyObjectCBMetadata, LT>::build_imp(
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
            return _KnownMetadataBuilder<Alg_Tag, Key_Type, _NullMetadata, std::less<Key_Type> >::build_imp(
                seq, mapping, NULL);
        return _KnownMetadataBuilder<Alg_Tag, Key_Type, _PyObjectCBMetadata, std::less<Key_Type> >::build_imp(
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

        PyObject * const args = Py_BuildValue("()");
        if (args == NULL) {
            PyErr_NoMemory();
            return NULL;
        }        
        BANYAN_PYOBJECT_INCREF(args);
        PyObject * const inst = PyObject_CallObject(KeyType, args);
        BANYAN_PYOBJECT_DECREF(args);
        if (inst == NULL)
            return _KnownKeyTypeBuilder<Alg_Tag, PyObject *>::build_imp(seq, mapping, metadata, key, cmp);

        // Tmp Ami - allow key-type optimization with metadata.
#if PY_MAJOR_VERSION >= 3
        if (PyLong_CheckExact(inst)) 
#else // #if PY_MAJOR_VERSION >= 3
        if (PyInt_CheckExact(inst)) 
#endif // #if PY_MAJOR_VERSION >= 3
            return _KnownKeyTypeBuilder<Alg_Tag, long>::build_imp(seq, mapping, metadata);
        if (PyFloat_CheckExact(inst)) 
            return _KnownKeyTypeBuilder<Alg_Tag, double>::build_imp(seq, mapping, metadata);
#if PY_MAJOR_VERSION >= 3
        if (PyByteArray_CheckExact(inst))            
#else // #if PY_MAJOR_VERSION >= 3
        if (PyString_CheckExact(inst))            
#endif // #if PY_MAJOR_VERSION >= 3
            return _KnownKeyTypeBuilder<Alg_Tag, String>::build_imp(seq, mapping, metadata);
        if (PyUnicode_CheckExact(inst))            
            return _KnownKeyTypeBuilder<Alg_Tag, UnicodeString>::build_imp(seq, mapping, metadata);
            
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

