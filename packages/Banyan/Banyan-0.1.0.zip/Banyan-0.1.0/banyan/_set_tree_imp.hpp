#ifndef _BANYAN_SET_TREE_IMP_HPP
#define _BANYAN_SET_TREE_IMP_HPP

#include <Python.h>

#include "_set_tree_imp_base.hpp"
#include "_tree_imp.hpp"
#include "_dbg.hpp"

template<
    class Alg_Tag,
    typename Key_Type,
    class Metadata,
    class LT>
class _SetTreeImp : 
    public _SetTreeImpBase,
    public _TreeImp<
        Alg_Tag,
        Key_Type,
        true,
        Metadata,
        LT>
{
public:
    explicit
    _SetTreeImp(PyObject * fast_seq, PyObject * metadata, PyObject * lt);

    virtual 
    ~_SetTreeImp();
    
    virtual int
    contains(PyObject * key);

    virtual PyObject *
    erase(PyObject * key);

    virtual PyObject *
    erase_slice(PyObject * start, PyObject * stop);

    virtual PyObject *
    discard(PyObject * key);

    virtual PyObject *
    erase_return(PyObject * key);

    virtual int
    traverse(visitproc visit, void * arg);    

    virtual PyObject *
    clear();

    virtual PyObject *
    pop();

    virtual void *
    begin(PyObject * start, PyObject * stop);

    virtual void *
    rbegin(PyObject * start, PyObject * stop);

    virtual void *
    next(void * mem, PyObject * stop, int type, PyObject * & cur_val);

    virtual void *
    prev(void * mem, PyObject * start, int type, PyObject * & cur_val);

    virtual void *
    root_iter();

    virtual void 
    delete_node_iter(void * it);

    virtual void *
    left_iter(void * it);

    virtual void *
    right_iter(void * it);

    virtual PyObject *
    iter_key(void * it);

    virtual PyObject *
    iter_metadata(void * it);

    virtual Py_ssize_t
    size();
    
    virtual PyObject *
    lt_keys(PyObject * lhs_key, PyObject * rhs_key);

    virtual PyObject *
    insert(PyObject * key);

    virtual PyObject *
    ext_union(PyObject * o, int type);

    virtual PyObject *
    ext_cmp(PyObject * o, int type);

#ifdef BANYAN_DEBUG
    void
    assert_valid() const;
#endif // #ifdef BANYAN_DEBUG    

protected:
    typedef   
        _TreeImp<
            Alg_Tag,
            Key_Type,
            true,
            Metadata,
            LT>     
        BaseT;         
        
    typedef
        typename BaseT::TreeT           
        TreeT;
};

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::_SetTreeImp(PyObject * fast_seq, PyObject * metadata, PyObject * lt) :
    BaseT(fast_seq, metadata, lt)
{
    // Do nothing.
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::~_SetTreeImp()
{
    // Do nothing.
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
int
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::contains(PyObject * key)
{
    return BaseT::contains(key);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
int
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::traverse(visitproc visit, void * arg)
{
    return BaseT::traverse(visit, arg);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::clear()
{
    return BaseT::clear();
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::pop()
{
    return BaseT::pop();
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::begin(PyObject * start, PyObject * stop)
{
    return BaseT::begin(start, stop);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::rbegin(PyObject * start, PyObject * stop)
{
    return BaseT::rbegin(start, stop);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::next(
    void * mem, PyObject * stop, int type, PyObject * & cur_val)
{
    return BaseT::next(mem, stop, type, cur_val);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::prev(
    void * mem, PyObject * start, int type, PyObject * & cur_val)
{
    return BaseT::prev(mem, start, type, cur_val);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::root_iter()
{
    return BaseT::root_iter();
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void 
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::delete_node_iter(void * it)
{
    BaseT::delete_node_iter(it);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::left_iter(void * it)
{
    return BaseT::left_iter(it);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::right_iter(void * it)
{
    return BaseT::right_iter(it);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::iter_key(void * it)
{
    return BaseT::iter_key(it);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::iter_metadata(void * it)
{
    return BaseT::iter_metadata(it);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
Py_ssize_t
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::size()
{
    return BaseT::tree.size();
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::insert(PyObject * key)
{
    std::pair<typename TreeT::Iterator, bool> ins;
    
    try {
        ins = BaseT::tree.insert(BaseT::key_to_internal_key(key));
    }
    catch(...) {
        PyErr_SetObject(PyExc_KeyError, key);        
        throw;
    }
    
    if (ins.second) 
        BANYAN_PYOBJECT_INCREF(key);

    Py_RETURN_NONE;                
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::ext_union(PyObject * fast_seq, int type)
{
    typedef
        std::vector<typename BaseT::InternalKeyType, PyMemMallocAllocator<typename BaseT::InternalKeyType> >
        VecT;

     VecT sorted = BaseT::sort_inc_unique_seq(fast_seq);

    VecT union_res;    
    switch (type) {
    case 0:
        std::set_union(
            BaseT::tree.begin(), BaseT::tree.end(),
            sorted.begin(), sorted.end(),
            back_inserter(union_res),
            BaseT::tree.less_than());
        break;            
    case 1:        
        std::set_intersection(
            BaseT::tree.begin(), BaseT::tree.end(),
            sorted.begin(), sorted.end(),
            back_inserter(union_res),
            BaseT::tree.less_than());
        break;            
    case 2:        
        std::set_difference(
            BaseT::tree.begin(), BaseT::tree.end(),
            sorted.begin(), sorted.end(),
            back_inserter(union_res),
            BaseT::tree.less_than());
        break;            
    case 3:        
        std::set_symmetric_difference(
            BaseT::tree.begin(), BaseT::tree.end(),
            sorted.begin(), sorted.end(),
            back_inserter(union_res),
            BaseT::tree.less_than());
        break;            
    default:
        DBG_ASSERT(0);
    };            

    PyObject * const res = PyTuple_New(union_res.size());
    if (res == NULL) {
        PyErr_NoMemory();
        return NULL;
    }
    
    for (size_t i = 0; i < union_res.size(); ++i) {
        PyObject * const k = BaseT::internal_value_to_key_inc(union_res[i]);
        PyTuple_SET_ITEM(res, i, k);
    }            
    
    for (size_t i = 0; i < sorted.size(); ++i)
        BaseT::dec_internal_value(sorted[i]);    

    return res;
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::ext_cmp(PyObject * fast_seq, int type)
{
    typedef
        std::vector<typename BaseT::InternalKeyType, PyMemMallocAllocator<typename BaseT::InternalKeyType> >
        VecT;
        
    VecT sorted = BaseT::sort_inc_unique_seq(fast_seq);

    bool res = false;        
    switch (type) {
    case 0:
        res = std::includes(
            sorted.begin(), sorted.end(),
            BaseT::tree.begin(), BaseT::tree.end(),
            BaseT::tree.less_than());
        break;            
    case 1:        
        res = std::includes(
            BaseT::tree.begin(), BaseT::tree.end(),
            sorted.begin(), sorted.end(),
            BaseT::tree.less_than());
        break;            
    case 2:        
        res = 
            std::distance(sorted.begin(), sorted.end()) == 
                std::distance(BaseT::tree.begin(), BaseT::tree.end()) && 
            std::equal(
                sorted.begin(), sorted.end(),
                BaseT::tree.begin(),
                LTEq<typename TreeT::LTT>(BaseT::tree.less_than()));
        break;            
    case 3:        
        res = disjoint(
            BaseT::tree.begin(), BaseT::tree.end(),
            sorted.begin(), sorted.end(),
            BaseT::tree.less_than());
        break;            
    default:
        DBG_ASSERT(0);
    };            
    
    if (res)
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;        
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::erase(PyObject * key)
{
    return BaseT::erase(key);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::erase_slice(PyObject * start, PyObject * stop)
{
    return BaseT::erase_slice(start, stop);
}    

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::discard(PyObject * key)
{
    try {    
        typename BaseT::InternalValueType val = 
            BaseT::tree.erase(BaseT::key_to_internal_key(key));
        BaseT::dec_internal_value(val);
    }
    catch(const std::logic_error &) {
        // Do nothing.
    }

    Py_RETURN_NONE;
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::erase_return(PyObject * key)
{
    return BaseT::erase_return(key);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::lt_keys(PyObject * lhs_key, PyObject * rhs_key)
{
    return BaseT::lt_keys(lhs_key, rhs_key);
}

#ifdef BANYAN_DEBUG
template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void
_SetTreeImp<Alg_Tag, Key_Type, Metadata, LT>::assert_valid() const
{
    BaseT::tree.assert_valid();       
}
#endif // #ifdef BANYAN_DEBUG    

#endif // #ifndef _BANYAN_SET_TREE_IMP_HPP

