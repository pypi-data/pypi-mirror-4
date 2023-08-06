#ifndef _TREE_IMP_METADATA_BASE_HPP
#define _TREE_IMP_METADATA_BASE_HPP

#include <Python.h>

#include <climits>
#include <cfloat>

#include "_dbg.hpp"
#include "_tree_imp_value_type_base.hpp"
#include "_tree_imp_pyobject_key_value_type_dict_base.hpp"
#include "_tree_imp_pyobject_key_value_type_set_base.hpp"
#include "_tree_imp_non_pyobject_key_value_type_dict_base.hpp"
#include "_tree_imp_non_pyobject_key_value_type_set_base.hpp"
#include "_dsa/_rank_updator.hpp"
#include "_dsa/_min_gap_updator.hpp"

struct _PyObjectCBMetadataTag{};

template<
    typename Key_Type>
class _KeyTypePyObjectCBMetadata :
    public _PyObjectCBMetadata
{
public:
    explicit _KeyTypePyObjectCBMetadata(PyObject * cbs) :
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

template<>
class _KeyTypePyObjectCBMetadata<
        PyObject *> :
    public _PyObjectCBMetadata
{
public:
    explicit _KeyTypePyObjectCBMetadata(PyObject * cbs) :
        _PyObjectCBMetadata(cbs)
    {
        // Do nothing.
    }        
};  

template<
    class Alg_Tag,
    typename Key_Type,
    bool Set,
    class Metadata,
    class LT>
struct _TreeImpMetadataBase :
    public _TreeImpValueTypeBase<
        Alg_Tag,
        Key_Type,
        Set,
        _KeyTypePyObjectCBMetadata<Key_Type>,
        LT>        
{
protected:
    typedef
        _TreeImpValueTypeBase<
            Alg_Tag,
            Key_Type,
            Set,
            _KeyTypePyObjectCBMetadata<Key_Type>,
            LT>    
        BaseT;
        
    typedef
        _KeyTypePyObjectCBMetadata<Key_Type>
        MetadataT;        

protected: 
    explicit
    _TreeImpMetadataBase(PyObject * seq, PyObject * metadata, const LT & lt) :
        BaseT(seq, MetadataT(metadata), lt)
    {
        DBG_ASSERT(seq != NULL);
    }   

    int
    traverse(visitproc visit, void * arg)
    {
        const int v = BaseT::traverse(visit, arg);
        if (v)
            return v;
    
        return BaseT::tree.meta().traverse(visit, arg);        
    }

    virtual PyObject *
    iter_metadata(void * it)
    {
        PyObject * const meta = BaseT::iter_internal_metadata(it).meta();
        BANYAN_PYOBJECT_INCREF(meta);
        return meta;
    }
};

#endif // #ifndef _TREE_IMP_METADATA_BASE_HPP
    
