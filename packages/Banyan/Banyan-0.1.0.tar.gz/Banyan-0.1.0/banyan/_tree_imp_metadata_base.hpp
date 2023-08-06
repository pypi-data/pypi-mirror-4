#ifndef _TREE_IMP_METADATA_BASE_HPP
#define _TREE_IMP_METADATA_BASE_HPP

#include <Python.h>

#include "_tree_imp_value_type_base.hpp"
#include "_tree_imp_pyobject_key_value_type_dict_base.hpp"
#include "_tree_imp_pyobject_key_value_type_set_base.hpp"
#include "_tree_imp_non_pyobject_key_value_type_dict_base.hpp"
#include "_tree_imp_non_pyobject_key_value_type_set_base.hpp"
#include "_dbg.hpp"

template<
    class Alg_Tag,
    typename Key_Type,
    bool Set,
    class Metadata,
    class LT>
struct _TreeImpMetadataBase :
    protected _TreeImpValueTypeBase<
        Alg_Tag,
        Key_Type,
        Set,
        Metadata,
        LT>        
{
protected:
    typedef
        _TreeImpValueTypeBase<
            Alg_Tag,
            Key_Type,
            Set,
            Metadata,
            LT>    
    BaseT;

protected: 
    explicit
    _TreeImpMetadataBase(PyObject * seq, PyObject * metadata, const LT & lt) :
        BaseT(seq, Metadata(metadata), lt)
    {
        DBG_ASSERT(seq != NULL);
    }   

    int
    traverse(visitproc visit, void * arg)
    {
        return BaseT::tree.meta().visit(visit, arg);        
    }

    PyObject *
    iter_metadata(void * it)
    {
        return BaseT::iter_metadata(it).meta();
    }
};

template<
    class Alg_Tag,
    typename Key_Type,
    bool Set,
    class LT>
struct _TreeImpMetadataBase<
        Alg_Tag,
        Key_Type,
        Set,
        _NullMetadata,
        LT> :
    protected _TreeImpValueTypeBase<
        Alg_Tag,
        Key_Type,
        Set,
        _NullMetadata,
        LT>    
{
protected:
    typedef
        _TreeImpValueTypeBase<
            Alg_Tag,
            Key_Type,
            Set,
            _NullMetadata,
            LT>    
    BaseT;

protected: 
    explicit
    _TreeImpMetadataBase(PyObject * seq, PyObject * metadata, const LT & lt) :
        BaseT(seq, _NullMetadata(), lt)
    {
        DBG_ASSERT(seq != NULL);
        DBG_ASSERT(metadata == NULL);
    }   

    PyObject *
    iter_metadata(void * it)
    {
        return Py_None;
    }
};

template<
    typename Key_Type>
class _NonPyObjectKeySetPyObjectCBMetadata :
    public _PyObjectCBMetadata
{
public:
    explicit _NonPyObjectKeySetPyObjectCBMetadata(PyObject * cbs) :
        _PyObjectCBMetadata(cbs)
    {
        // Do nothing.
    }        
    
    inline void 
    update(
        const std::pair<Key_Type, PyObject *> & value, 
        const _PyObjectCBMetadata * l, const _PyObjectCBMetadata * r)
    {
        _PyObjectCBMetadata::update(value.second, l, r);
    }
};        
    
template<
    class Alg_Tag,
    typename Key_Type,
    class LT>
struct _TreeImpMetadataBase<
        Alg_Tag,
        Key_Type,
        true,
        _PyObjectCBMetadata,
        LT> :
    protected _TreeImpMetadataBase<
        Alg_Tag,
        Key_Type,
        true,
        _NonPyObjectKeySetPyObjectCBMetadata<Key_Type>,
        LT>        
{
protected:
    typedef
        _TreeImpMetadataBase<
            Alg_Tag,
            Key_Type,
            true,
            _NonPyObjectKeySetPyObjectCBMetadata<Key_Type>,
            LT>    
    BaseT;

protected: 
    explicit
    _TreeImpMetadataBase(PyObject * seq, PyObject * metadata, const LT & lt) :
        BaseT(seq, metadata, lt)
    {
        // Do nothing.
    }   
};

class _PyObjectKeySetPyObjectCBMetadata :
    public _PyObjectCBMetadata
{
public:
    explicit _PyObjectKeySetPyObjectCBMetadata(PyObject * cbs) :
        _PyObjectCBMetadata(cbs)
    {
        // Do nothing.
    }        
    
    inline void 
    update(PyObject * key, const _PyObjectCBMetadata * l, const _PyObjectCBMetadata * r)
    {
        _PyObjectCBMetadata::update(key, l, r);
    }
};        
    
template<
    class Alg_Tag,
    class LT>
struct _TreeImpMetadataBase<
        Alg_Tag,
        PyObject *,
        true,
        _PyObjectCBMetadata,
        LT> :
    protected _TreeImpMetadataBase<
        Alg_Tag,
        PyObject *,
        true,
        _PyObjectKeySetPyObjectCBMetadata,
        LT>        
{
protected:
    typedef
        _TreeImpMetadataBase<
            Alg_Tag,
            PyObject *,
            true,
            _PyObjectKeySetPyObjectCBMetadata,
            LT>    
    BaseT;

protected: 
    explicit
    _TreeImpMetadataBase(PyObject * seq, PyObject * metadata, const LT & lt) :
        BaseT(seq, metadata, lt)
    {
        // Do nothing.
    }   
};

template<
    typename Key_Type>
class _NonPyObjectKeyDictPyObjectCBMetadata :
    public _PyObjectCBMetadata
{
public:
    explicit _NonPyObjectKeyDictPyObjectCBMetadata(PyObject * cbs) :
        _PyObjectCBMetadata(cbs)
    {
        // Do nothing.
    }        
    
    inline void 
    update(
        const std::pair<std::pair<Key_Type, PyObject *>, PyObject *> & value, 
        const _PyObjectCBMetadata * l, const _PyObjectCBMetadata * r)
    {
        _PyObjectCBMetadata::update(value.first.second, l, r);
    }
};        

template<
    class Alg_Tag,
    typename Key_Type,
    class LT>
struct _TreeImpMetadataBase<
        Alg_Tag,
        Key_Type,
        false,
        _PyObjectCBMetadata,
        LT> :
    protected _TreeImpMetadataBase<
        Alg_Tag,
        Key_Type,
        false,
        _NonPyObjectKeyDictPyObjectCBMetadata<Key_Type>,
        LT>        
{
protected:
    typedef
        _TreeImpMetadataBase<
            Alg_Tag,
            Key_Type,
            false,
            _NonPyObjectKeyDictPyObjectCBMetadata<Key_Type>,
            LT>    
    BaseT;

protected: 
    explicit
    _TreeImpMetadataBase(PyObject * seq, PyObject * metadata, const LT & lt) :
        BaseT(seq, metadata, lt)
    {
        // Do nothing.
    }   
};

class _PyObjectKeyDictPyObjectCBMetadata :
    public _PyObjectCBMetadata
{
public:
    explicit _PyObjectKeyDictPyObjectCBMetadata(PyObject * cbs) :
        _PyObjectCBMetadata(cbs)
    {
        // Do nothing.
    }        
    
    inline void 
    update(PyObject * val, const _PyObjectCBMetadata * l, const _PyObjectCBMetadata * r)
    {
        DBG_ASSERT(PyTuple_Check(val));
        DBG_ASSERT(PyTuple_Size(val) == 2);                
        _PyObjectCBMetadata::update(PyTuple_GET_ITEM(val, 0), l, r);
    }
};        
    
template<
    class Alg_Tag,
    class LT>
struct _TreeImpMetadataBase<
        Alg_Tag,
        PyObject *,
        false,
        _PyObjectCBMetadata,
        LT> :
    protected _TreeImpMetadataBase<
        Alg_Tag,
        PyObject *,
        false,
        _PyObjectKeyDictPyObjectCBMetadata,
        LT>        
{
protected:
    typedef
        _TreeImpMetadataBase<
            Alg_Tag,
            PyObject *,
            false,
            _PyObjectKeyDictPyObjectCBMetadata,
            LT>    
    BaseT;

protected: 
    explicit
    _TreeImpMetadataBase(PyObject * seq, PyObject * metadata, const LT & lt) :
        BaseT(seq, metadata, lt)
    {
        // Do nothing.
    }   
};

#endif // #ifndef _TREE_IMP_METADATA_BASE_HPP

