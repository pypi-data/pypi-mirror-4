#ifndef _BANYAN_DICT_TREE_IMP_HPP
#define _BANYAN_DICT_TREE_IMP_HPP

#include <Python.h>

#include "_dict_tree_imp_base.hpp"
#include "_tree_imp.hpp"
#include "_dbg.hpp"

template<
    class Alg_Tag,
    typename Key_Type,
    class Metadata,
    class LT>
class _DictTreeImp : 
    public _DictTreeImpBase,
    public _TreeImp<
        Alg_Tag,
        Key_Type,
        false,
        Metadata,
        LT>
{
public:
    explicit
    _DictTreeImp(PyObject * fast_seq, PyObject * metadata, PyObject * lt);

    virtual 
    ~_DictTreeImp();
    
    virtual int
    traverse(visitproc visit, void * arg);    

    virtual PyObject *
    clear();

    virtual PyObject *
    pop();

    virtual PyObject *
    pop(PyObject * key, PyObject * data);

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

    virtual int
    contains(PyObject * key);

    virtual PyObject *
    erase(PyObject * key);

    virtual PyObject *
    erase_slice(PyObject * start, PyObject * stop);

    virtual PyObject *
    erase_return(PyObject * key);

    virtual PyObject *
    find(PyObject * key);

    virtual PyObject *
    find_slice(PyObject * start, PyObject * stop);

    virtual PyObject *
    get(PyObject * key, PyObject * data);

    virtual PyObject *
    insert(PyObject * key, PyObject * data, bool overwrite);
    
    virtual int
    update_slice_data(PyObject * start, PyObject * stop, PyObject * data);

#ifdef BANYAN_DEBUG
    void
    assert_valid() const;
#endif // #ifdef BANYAN_DEBUG    

protected:
    typedef   
        _TreeImp<
            Alg_Tag,
            Key_Type,
            false,
            Metadata,
            LT>     
        BaseT;            

    typedef
        typename BaseT::TreeT           
        TreeT;
};

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::_DictTreeImp(PyObject * fast_seq, PyObject * metadata, PyObject * lt) :
    BaseT(fast_seq, metadata, lt)
{
    // Do nothing.
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::~_DictTreeImp()
{
    // Do nothing.
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
int
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::contains(PyObject * key)
{
    return BaseT::contains(key);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
int
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::traverse(visitproc visit, void * arg)
{
    return BaseT::traverse(visit, arg);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::clear()
{
    return BaseT::clear();
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::pop()
{
    return BaseT::pop();
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::pop(PyObject * key, PyObject * data)
{
    try {    
        typename BaseT::InternalValueType val = 
            BaseT::tree.erase(BaseT::key_to_internal_key(key));
        data = BaseT::internal_value_to_data_inc(val);
        BaseT::dec_internal_value(val);
        return data;
    }
    catch(const std::logic_error &) {
        if (data == NULL) {
            PyErr_SetObject(PyExc_KeyError, key);        
            return NULL;
        }     
        BANYAN_PYOBJECT_INCREF(data);
        return data;                
    }

    return NULL;
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::begin(PyObject * start, PyObject * stop)
{
    return BaseT::begin(start, stop);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::rbegin(PyObject * start, PyObject * stop)
{
    return BaseT::rbegin(start, stop);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::next(
    void * mem, PyObject * stop, int type, PyObject * & cur_val)
{
    return BaseT::next(mem, stop, type, cur_val);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::prev(
    void * mem, PyObject * start, int type, PyObject * & cur_val)
{
    return BaseT::prev(mem, start, type, cur_val);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::root_iter()
{
    return BaseT::root_iter();
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void 
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::delete_node_iter(void * it)
{
    BaseT::delete_node_iter(it);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::left_iter(void * it)
{
    return BaseT::left_iter(it);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::right_iter(void * it)
{
    return BaseT::right_iter(it);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::iter_key(void * it)
{
    return BaseT::iter_key(it);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::iter_metadata(void * it)
{
    return BaseT::iter_metadata(it);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
Py_ssize_t
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::size()
{
    return BaseT::tree.size();
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::find(PyObject * key)
{
    typename TreeT::Iterator found = BaseT::tree.find(BaseT::key_to_internal_key(key));

    if (found == BaseT::end()) {
        PyErr_SetObject(PyExc_KeyError, key);
        return NULL;
    }

    return BaseT::internal_value_to_data_inc(*found);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::find_slice(PyObject * start, PyObject * stop)
{
    std::pair<typename TreeT::Iterator, typename TreeT::Iterator> start_stop = 
        BaseT::start_stop_its(start, stop);
        
    PyObject * val = PyTuple_New(std::distance(start_stop.first, start_stop.second));
    if (val == NULL) {
        PyErr_NoMemory();
        return NULL;
    }    
    for (typename TreeT::Iterator it = start_stop.first; it != start_stop.second; ++it) {
        PyObject * const data = BaseT::internal_value_to_data_inc(*it);
        PyTuple_SET_ITEM(val, std::distance(start_stop.first, it), data);
    }        
    return val;
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::get(PyObject * key, PyObject * data)
{
    typename TreeT::Iterator found = BaseT::tree.find(BaseT::key_to_internal_key(key));

    if (found == BaseT::end()) {
        BANYAN_PYOBJECT_INCREF(data);
        return data;
    }

    return BaseT::internal_value_to_data_inc(*found);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::insert(PyObject * key, PyObject * data, bool overwrite)
{
    typename BaseT::InternalValueType val = 
        BaseT::key_data_to_internal_value_inc(key, data);

    std::pair<typename TreeT::Iterator, bool> ins = 
        BaseT::tree.insert(val);
        
    if (ins.second) {
        BANYAN_PYOBJECT_INCREF(data);
        return data;
    }
        
    if (overwrite) {
        BANYAN_PYOBJECT_INCREF(data);
        BaseT::dec_internal_value(*ins.first);
        *ins.first = val;
        return data;
    }
    
    data = BaseT::internal_value_to_data_inc(*ins.first);        
    BaseT::dec_internal_value(val);        
    return data;
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::erase(PyObject * key)
{
    return BaseT::erase(key);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::erase_slice(PyObject * start, PyObject * stop)
{
    return BaseT::erase_slice(start, stop);
}    

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::erase_return(PyObject * key)
{
    return BaseT::erase_return(key);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
PyObject *
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::lt_keys(PyObject * lhs_key, PyObject * rhs_key)
{
    return BaseT::lt_keys(lhs_key, rhs_key);
}

template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
int
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::update_slice_data(
    PyObject * start, PyObject * stop, PyObject * data_fast_seq)
{
    std::pair<typename TreeT::Iterator, typename TreeT::Iterator> its = BaseT::start_stop_its(start, stop);    
    typename TreeT::Iterator b = its.first, e = its.second;

    if (std::distance(b, e) != PySequence_Fast_GET_SIZE(data_fast_seq)) {
        PyErr_SetObject(PyExc_ValueError, data_fast_seq);
        return -1;    
    }        
    
    for (size_t i = 0; i < static_cast<size_t>(PySequence_Fast_GET_SIZE(data_fast_seq)); ++i, ++b) {
        BANYAN_PYOBJECT_INCREF(PySequence_Fast_GET_ITEM(data_fast_seq, i));
        BaseT::update_data(*b, PySequence_Fast_GET_ITEM(data_fast_seq, i));
    }        
                    
    return 0;
}

#ifdef BANYAN_DEBUG
template<class Alg_Tag, typename Key_Type, class Metadata, class LT>
void
_DictTreeImp<Alg_Tag, Key_Type, Metadata, LT>::assert_valid() const
{
    BaseT::tree.assert_valid();       
}
#endif // #ifdef BANYAN_DEBUG    

#endif // #ifndef _BANYAN_DICT_TREE_IMP_HPP

