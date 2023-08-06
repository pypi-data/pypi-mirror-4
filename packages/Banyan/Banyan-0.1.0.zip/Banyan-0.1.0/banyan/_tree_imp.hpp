#ifndef _BANYAN_TREE_IMP_HPP
#define _BANYAN_TREE_IMP_HPP

#include <Python.h>

#include "_tree_imp_lt_base.hpp"
#include "_functional.hpp"
#include "_dbg.hpp"

template<
    class Alg_Tag,
    typename Key_Type,
    bool Set,
    class Metadata,
    class LT>
class _TreeImp : 
    protected _TreeImpLTBase<
        Alg_Tag,
        Key_Type,
        Set,
        Metadata,
        LT>
{
public:
    explicit
    _TreeImp(PyObject * fast_seq, PyObject * metadata, PyObject * lt);

    ~_TreeImp();
    
    int
    traverse(visitproc visit, void * arg);    
    
    int
    contains(PyObject * key);

    PyObject *
    erase(PyObject * key);

    PyObject *
    erase_return(PyObject * key);

    PyObject *
    clear();

    PyObject *
    pop();

    void *
    begin(PyObject * start, PyObject * stop);

    void *
    rbegin(PyObject * start, PyObject * stop);

    void *
    next(void * cur, PyObject * stop, int type, PyObject * & cur_val);

    void *
    prev(void * cur, PyObject * start, int type, PyObject * & cur_val);
    
    PyObject *
    iter_key(void * it);
    
    PyObject *
    iter_metadata(void * it);

    Py_ssize_t
    size();

    PyObject *
    lt_keys(PyObject * lhs_key, PyObject * rhs_key);

    PyObject *
    erase_slice(PyObject * start, PyObject * stop);

#ifdef BANYAN_DEBUG
    void
    assert_valid() const;
#endif // #ifdef BANYAN_DEBUG    

protected:    
    typedef 
        _TreeImpLTBase<
            Alg_Tag,
            Key_Type,
            Set,
            Metadata,
            LT>
        BaseT;
        
    typedef typename BaseT::TreeT TreeT;        
    
    typedef typename BaseT::InternalKeyType InternalKeyType;
    typedef typename BaseT::InternalValueType InternalValueType;
    
private:
    typedef
        _TreeImp<
            Alg_Tag,
            Key_Type,
            Set,
            Metadata,
            LT>
        ThisT;        
        
protected:
    std::pair<typename TreeT::Iterator, typename TreeT::Iterator>
    start_stop_its(PyObject * start, PyObject * stop);
};

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::_TreeImp(PyObject * fast_seq, PyObject * metadata, PyObject * lt) :
    BaseT(fast_seq, metadata, lt)
{
    // Do nothing.
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::~_TreeImp()
{
    clear();
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
int
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::traverse(visitproc visit, void * arg)
{
    const int base_traverse = BaseT::traverse(visit, arg);
    if (base_traverse != 0)
        return base_traverse;
            
    return 0;
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
std::pair<
    typename _TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::TreeT::Iterator, 
    typename _TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::TreeT::Iterator>
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::start_stop_its(PyObject * start, PyObject * stop)
{
    if (start == Py_None && stop == Py_None) 
        return std::make_pair(BaseT::tree.begin(), BaseT::tree.end());
        
    if (start == Py_None && stop != Py_None) {
        typename TreeT::Iterator b, e;
        b = e = BaseT::tree.begin();
        const InternalKeyType stop_k = BaseT::key_to_internal_key(stop);
        while (true) {
            if (e == BaseT::tree.end() || 
                    !BaseT::tree.less_than()(
                        TreeT::KeyExtractorT::extract(*e),
                        stop_k))
                break;    
            ++e;
        }
        return std::make_pair(b, e);
    }                    
    
    DBG_VERIFY(start != Py_None);
    
    typename TreeT::Iterator b;
    b = BaseT::tree.lower_bound(BaseT::key_to_internal_key(start));
    
    typename TreeT::Iterator e;
    if (stop == Py_None)
        e = BaseT::tree.end();
    else {
        e = b;
        while (true) {
            if (e == BaseT::tree.end() || !BaseT::tree.less_than()(
                    TreeT::KeyExtractorT::extract(*e),
                    BaseT::key_to_internal_key(stop)))
                break;    
            ++e;
        }
    }            
    
    return std::make_pair(b, e);
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
int
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::contains(PyObject * key)
{
    return BaseT::tree.find(BaseT::key_to_internal_key(key)) != BaseT::end();
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
PyObject *
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::erase(PyObject * key)
{
    try {    
        InternalValueType val = BaseT::tree.erase(BaseT::key_to_internal_key(key));
        
        BaseT::dec_internal_value(val);

        Py_RETURN_NONE;
    }
    catch(const std::logic_error &) {
        PyErr_SetObject(PyExc_KeyError, key);        
        throw;
    }
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
PyObject *
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::erase_return(PyObject * key)
{
    InternalValueType val;
    try {    
        val = BaseT::tree.erase(BaseT::key_to_internal_key(key));
    }
    catch(const std::logic_error &) {
        PyErr_SetObject(PyExc_KeyError, key);        
        throw;
    }

    PyObject * const p = BaseT::internal_value_to_value_inc(val);
    BaseT::dec_internal_value(val);
    return p;
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
PyObject *
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::erase_slice(PyObject * start, PyObject * stop)
{
    std::pair<typename TreeT::Iterator, typename TreeT::Iterator> its = start_stop_its(start, stop);    
    typename TreeT::Iterator b = its.first, e = its.second;
    typename TreeT::Iterator begin_ = BaseT::tree.begin();
    
    if (b == begin_ && e == BaseT::tree.end()) {
        clear();
        
        Py_RETURN_NONE;
    }
    
    if (b == BaseT::tree.end()) {
        DBG_ASSERT(e == BaseT::tree.end());

        Py_RETURN_NONE;
    }
    
    const size_t orig_size = BaseT::tree.size();        
        
    if (b == begin_ && e != BaseT::tree.end()) {
        TreeT larger(NULL, NULL, BaseT::tree.meta(), BaseT::tree.less_than());
        BaseT::tree.split(TreeT::KeyExtractorT::extract(*e), larger);  

        size_t num_erased = 0;        
        for (typename TreeT::Iterator it = BaseT::tree.begin(); it != BaseT::tree.end(); ++it) {
            ++num_erased;
            BaseT::dec_internal_value(*it);            
        }         
        
        BaseT::tree.swap(larger);   
        BaseT::tree.restore_size(orig_size - num_erased);

        DBG_ONLY(BaseT::tree.assert_valid();)

        Py_RETURN_NONE;
    }
    
    if (b != begin_ && e == BaseT::tree.end()) {
        TreeT larger(NULL, NULL, BaseT::tree.meta(), BaseT::tree.less_than());
        BaseT::tree.split(TreeT::KeyExtractorT::extract(*b), larger);  
    
        size_t num_erased = 0;        
        for (typename TreeT::Iterator it = larger.begin(); it != larger.end(); ++it) {
            ++num_erased;
            BaseT::dec_internal_value(*it);            
        }         
        
        BaseT::tree.restore_size(orig_size - num_erased);

        DBG_ONLY(BaseT::tree.assert_valid();)

        Py_RETURN_NONE;
    }
    
    const typename BaseT::KeyType start_key = TreeT::KeyExtractorT::extract(*b);
    const typename BaseT::KeyType stop_key = TreeT::KeyExtractorT::extract(*e);
    
    TreeT mid(NULL, NULL, BaseT::tree.meta(), BaseT::tree.less_than());
    BaseT::tree.split(start_key, mid);  

    TreeT right(NULL, NULL, BaseT::tree.meta(), BaseT::tree.less_than());
    // Tmp Ami - suspicious
    if (stop != Py_None)
        mid.split(stop_key, right);

    size_t num_erased = 0;        
    for (typename TreeT::Iterator it = mid.begin(); it != mid.end(); ++it) {
        ++num_erased;
        BaseT::dec_internal_value(*it);            
    }            
    
    BaseT::tree.join(right);     
    BaseT::tree.restore_size(orig_size - num_erased);

    DBG_ONLY(BaseT::tree.assert_valid();)
         
    Py_RETURN_NONE;
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
PyObject *
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::clear()
{
    for (typename TreeT::Iterator it = BaseT::tree.begin(); it != BaseT::end(); ++it) 
        BaseT::dec_internal_value(*it);        

    BaseT::tree.clear();
    
    Py_RETURN_NONE;
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
PyObject *
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::pop()
{
    if (BaseT::tree.size() == 0) {
        PyErr_SetString(PyExc_KeyError, "Attempting to pop an empty tree");
        
        return NULL;
    }
    
    typename BaseT::InternalValueType popped = BaseT::tree.pop();
    PyObject * const ret = BaseT::internal_value_to_value_inc(popped);
    return ret;
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
void *
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::begin(PyObject * start, PyObject * stop)
{
    if (start == NULL && stop == NULL) 
        return BaseT::mem_begin(NULL, NULL);
            
    if (start == NULL && stop != NULL) {
        const InternalKeyType stop_k = BaseT::key_to_internal_key(stop);                        
        return BaseT::mem_begin(NULL, &stop_k);
    }        
    
    DBG_VERIFY(start != NULL);
    const InternalKeyType start_k = BaseT::key_to_internal_key(start);                        

    if (stop == NULL)
        return BaseT::mem_begin(&start_k, NULL);
        
    const InternalKeyType stop_k = BaseT::key_to_internal_key(stop);                        
    return BaseT::mem_begin(&start_k, &stop_k);
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
void *
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::rbegin(PyObject * start, PyObject * stop)
{
    if (start == NULL && stop == NULL) 
        return BaseT::mem_rbegin(NULL, NULL);
            
    if (start == NULL && stop != NULL) {
        const InternalKeyType stop_k = BaseT::key_to_internal_key(stop);                        
        return BaseT::mem_rbegin(NULL, &stop_k);
    }        
    
    DBG_VERIFY(start != NULL);
    const InternalKeyType start_k = BaseT::key_to_internal_key(start);                        

    if (stop == NULL)
        return BaseT::mem_rbegin(&start_k, NULL);
        
    const InternalKeyType stop_k = BaseT::key_to_internal_key(stop);                        
    return BaseT::mem_rbegin(&start_k, &stop_k);
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
void *
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::next(
    void * mem, PyObject * stop, int type, PyObject * & cur_val)
{
    DBG_ASSERT(mem != NULL);       
    
    switch(type) {
    case 0:
        cur_val = BaseT::internal_value_to_key_inc(
            BaseT::mem_value(mem));
        break;
    case 1:
        cur_val = BaseT::internal_value_to_data_inc(
            BaseT::mem_value(mem));
        break;
    case 2:
        cur_val = BaseT::internal_value_to_value_inc(
            BaseT::mem_value(mem));
        break;
    default:
        DBG_ASSERT(false);
    };    
    
    if (stop == NULL)
        return BaseT::mem_next(mem, NULL);
        
    const InternalKeyType stop_k = BaseT::key_to_internal_key(stop);                        
    return BaseT::mem_next(mem, &stop_k);
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
void *
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::prev(
    void * mem, PyObject * start, int type, PyObject * & cur_val)
{
    DBG_ASSERT(mem != NULL);
    
    switch(type) {
    case 0:
        cur_val = BaseT::internal_value_to_key_inc(
            BaseT::mem_value(mem));
        break;
    case 1:
        cur_val = BaseT::internal_value_to_data_inc(
            BaseT::mem_value(mem));
        break;
    case 2:
        cur_val = BaseT::internal_value_to_value_inc(
            BaseT::mem_value(mem));
        break;
    default:
        DBG_ASSERT(false);
    };
    
    if (start == NULL)
        return BaseT::mem_prev(mem, NULL);
        
    const InternalKeyType start_k = BaseT::key_to_internal_key(start);                        
    return BaseT::mem_prev(mem, &start_k);
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
PyObject *
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::iter_key(void * it)
{
    DBG_ASSERT(it != NULL);
    PyObject * const p = BaseT::internal_value_to_key_inc(BaseT::iter_value(it));
    return p;
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
PyObject *
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::iter_metadata(void * it)
{
    DBG_ASSERT(it != NULL);
    PyObject * const p = BaseT::iter_metadata(it);
    BANYAN_PYOBJECT_INCREF(p);
    return p;
}

template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
PyObject *
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::lt_keys(PyObject * lhs_key, PyObject * rhs_key)
{
    if (BaseT::tree.less_than()(
            BaseT::key_to_internal_key(lhs_key), 
            BaseT::key_to_internal_key(rhs_key)))
        Py_RETURN_TRUE;
    
    Py_RETURN_FALSE;        
}

#ifdef BANYAN_DEBUG
template<class Alg_Tag, typename Key_Type, bool Set, class Metadata, class LT>
void
_TreeImp<Alg_Tag, Key_Type, Set, Metadata, LT>::assert_valid() const
{
    BaseT::tree.assert_valid();       
    DBG_ASSERT(BaseT::tree.size() != static_cast<size_t>(-1));
    typename BaseT::TreeT::Iterator it = const_cast<TreeT &>(BaseT::tree).begin();
    while (it != const_cast<TreeT &>(BaseT::tree).end()) 
        BaseT::assert_valid(*it++);

    const_cast<TreeT &>(BaseT::tree).less_than().assert_valid();
    const_cast<TreeT &>(BaseT::tree).meta().assert_valid();
}
#endif // #ifdef BANYAN_DEBUG    

#endif // #ifndef _BANYAN_TREE_IMP_HPP

