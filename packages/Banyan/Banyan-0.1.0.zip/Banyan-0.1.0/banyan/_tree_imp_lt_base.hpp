#ifndef _TREE_IMP_LT_BASE_HPP
#define _TREE_IMP_LT_BASE_HPP

#include <Python.h>

#include "_tree_imp_metadata_base.hpp"
#include "_dbg.hpp"

template<
    class Alg_Tag,
    typename Key_Type,
    bool Set,
    class Metadata,
    class LT>
struct _TreeImpLTBase
{
    // Nothing.
};

template<
    class Alg_Tag,
    typename Key_Type,
    bool Set,
    class Metadata>
struct _TreeImpLTBase<
        Alg_Tag,
        Key_Type,
        Set,
        Metadata,
        std::less<Key_Type> > : 
    protected _TreeImpMetadataBase<
        Alg_Tag,
        Key_Type,
        Set,
        Metadata,
        std::less<Key_Type> >
{
protected:
    typedef
        _TreeImpMetadataBase<
            Alg_Tag,
            Key_Type,
            Set,
            Metadata,
            std::less<Key_Type> >    
    BaseT;

protected: 
    explicit
    _TreeImpLTBase(PyObject * seq, PyObject * metadata, PyObject * lt) :
        BaseT(seq, metadata, std::less<Key_Type>())
    {
        DBG_ASSERT(lt == NULL);
        DBG_ASSERT(seq != NULL);
    }   
};

template<
    class Alg_Tag,
    typename Key_Type,
    bool Set,
    class Metadata>
struct _TreeImpLTBase<
        Alg_Tag,
        Key_Type,
        Set,
        Metadata,
        _PyObjectStdLT> : 
    protected _TreeImpMetadataBase<
        Alg_Tag,
        Key_Type,
        Set,
        Metadata,
        _PyObjectStdLT>
{
protected:
    typedef
        _TreeImpMetadataBase<
            Alg_Tag,
            Key_Type,
            Set,
            Metadata,
            _PyObjectStdLT>    
    BaseT;

protected: 
    explicit
    _TreeImpLTBase(PyObject * seq, PyObject * metadata, PyObject * lt) :
        BaseT(seq, metadata, _PyObjectStdLT())
    {
        DBG_ASSERT(lt == NULL);
        DBG_ASSERT(seq != NULL);
    }   
};

template<
    class Alg_Tag,
    typename Key_Type,
    bool Set,
    class Metadata>
struct _TreeImpLTBase<
        Alg_Tag,
        Key_Type,
        Set,
        Metadata,
        _PyObjectCmpCBLT> : 
    protected _TreeImpMetadataBase<
        Alg_Tag,
        Key_Type,
        Set,
        Metadata,
        _PyObjectCmpCBLT>
{
protected:
    typedef
        _TreeImpMetadataBase<
            Alg_Tag,
            Key_Type,
            Set,
            Metadata,
            _PyObjectCmpCBLT>    
    BaseT;

protected: 
    explicit
    _TreeImpLTBase(PyObject * seq, PyObject * metadata, PyObject * cmp) :
        BaseT(seq, metadata, _PyObjectCmpCBLT(cmp))
    {
        DBG_ASSERT(seq != NULL);
    }   

    int
    traverse(visitproc visit, void * arg)
    {
        return BaseT::tree.less_than().visit(visit, arg);        
    }
};

template<
    class Alg_Tag,
    typename Key_Type,
    bool Set,
    class Metadata>
struct _TreeImpLTBase<
        Alg_Tag,
        Key_Type,
        Set,
        Metadata,
        _PyObjectKeyCBLT> : 
    protected _TreeImpMetadataBase<
        Alg_Tag,
        Key_Type,
        Set,
        Metadata,
        _PyObjectKeyCBLT>
{
protected:
    typedef
        _TreeImpMetadataBase<
            Alg_Tag,
            Key_Type,
            Set,
            Metadata,
            _PyObjectKeyCBLT>    
    BaseT;

protected: 
    explicit
    _TreeImpLTBase(PyObject * seq, PyObject * metadata, PyObject * key) :
        BaseT(seq, metadata, _PyObjectKeyCBLT(key))
    {
        DBG_ASSERT(seq != NULL);
    }   

    int
    traverse(visitproc visit, void * arg)
    {
        return BaseT::tree.less_than().visit(visit, arg);        
    }
};

#endif // #ifndef _TREE_IMP_LT_BASE_HPP

