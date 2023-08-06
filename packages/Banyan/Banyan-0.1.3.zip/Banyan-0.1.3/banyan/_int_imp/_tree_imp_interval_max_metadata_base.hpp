#ifndef _TREE_IMP_INTERVAL_MAX_METADATA_BASE_HPP
#define _TREE_IMP_INTERVAL_MAX_METADATA_BASE_HPP

#include <Python.h>

#include "_dbg.hpp"

struct _IntervalMaxMetadataTag{};

struct _IntervalMaxMetadata
{
    _IntervalMaxMetadata() :
        min_(NULL),
        max_(NULL)
    {
        // Do nothing.
    }        
    
    _IntervalMaxMetadata(const _IntervalMaxMetadata & other)  :
        min_(other.min_),
        max_(other.max_)
    {
        if (min_ != NULL) 
            BANYAN_PYOBJECT_INCREF(min_);
        if (max_ != NULL) 
            BANYAN_PYOBJECT_INCREF(max_);
    }
    
    _IntervalMaxMetadata & 
    operator=(const _IntervalMaxMetadata & other) 
    {
        if (this != &other)
        {
            if (min_ != NULL) 
                BANYAN_PYOBJECT_DECREF(min_);
            if (max_ != NULL) 
                BANYAN_PYOBJECT_DECREF(max_);
                
            min_ = other.min_;
            max_ = other.max_;
            
            if (min_ != NULL) 
                BANYAN_PYOBJECT_INCREF(min_);
            if (max_ != NULL) 
                BANYAN_PYOBJECT_INCREF(max_);
        }
        
        return *this;
    }
    
    virtual ~_IntervalMaxMetadata()
    {
        if (min_ != NULL) 
            BANYAN_PYOBJECT_DECREF(min_);
        if (max_ != NULL) 
            BANYAN_PYOBJECT_DECREF(max_);
    }

    void 
    update(PyObject * key, const _IntervalMaxMetadata * l, const _IntervalMaxMetadata * r)
    {
        if (min_ != NULL) 
            BANYAN_PYOBJECT_DECREF(min_);
        if (max_ != NULL) 
            BANYAN_PYOBJECT_DECREF(max_);
            
        if (!PySequence_Check(key) || 
                (min_ = PySequence_Fast_GET_ITEM(key, 0)) == NULL || 
                (max_ = PySequence_Fast_GET_ITEM(key, 1)) == NULL) {
            PyErr_SetObject(PyExc_TypeError, key);            
            throw std::logic_error("Can't take [0] or [1]");
        }
                
        if (l != NULL) {
            if (PyObject_RichCompareBool(l->min_, min_, Py_LT))
                min_ = l->min_;
            if (PyObject_RichCompareBool(max_, l->max_, Py_LT))
                max_ = l->max_;
        }                
        if (r != NULL) {
            if (PyObject_RichCompareBool(r->min_, min_, Py_LT))
                min_ = r->min_;
            if (PyObject_RichCompareBool(max_, r->max_, Py_LT))
                max_ = r->max_;
        }                
        
        BANYAN_PYOBJECT_INCREF(min_);
        BANYAN_PYOBJECT_INCREF(max_);
    }

    int 
    traverse(visitproc visit, void * arg)
    {
        if (min_ != NULL)
            Py_VISIT(min_);
        if (max_ != NULL)
            Py_VISIT(max_);
        return 0;            
    }

    PyObject * min_, * max_;
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
        _IntervalMaxMetadataTag,
        LT> :
    public _TreeImpValueTypeBase<
        Alg_Tag,
        Key_Type,
        Set,
        _IntervalMaxMetadata,
        LT>    
{
public: 
    explicit
    _TreeImpMetadataBase(PyObject * seq, PyObject * metadata, const LT & lt) :
        BaseT(seq, _IntervalMaxMetadata(), lt)
    {
        DBG_ASSERT(seq != NULL);
        DBG_ASSERT(metadata == NULL);
    }   

    virtual PyObject *
    iter_metadata(void * it)
    {                
        PyObject * const min_ = BaseT::iter_internal_metadata(it).min_;
        PyObject * const max_ = BaseT::iter_internal_metadata(it).max_;
        
        PyObject * const ret = Py_BuildValue("(OO)", min_, max_);
        BANYAN_PYOBJECT_DUMMY_INCREF(min_);
        BANYAN_PYOBJECT_DUMMY_INCREF(max_);
        BANYAN_PYOBJECT_DECREF(min_);
        BANYAN_PYOBJECT_DECREF(max_);
        
        return ret;
    }

    virtual PyObject *
    interval_max_updator_overlapping(PyObject * b, PyObject * e)
    {
        PyObject * const l = PyList_New(0);
        if (l == NULL) {
            PyErr_NoMemory();
            throw std::bad_alloc();
        }
        
        if (BaseT::tree.size() == 0)
            return l;

        interval_max_updator_overlapping(b, e, BaseT::root_iter(), l);
        
        return l;
    }

    virtual PyObject *
    interval_max_updator_overlapping(PyObject * p)
    {    
        PyObject * const l = PyList_New(0);
        if (l == NULL) {
            PyErr_NoMemory();
            throw std::bad_alloc();
        }
        
        if (BaseT::tree.size() == 0)
            return l;
        
        interval_max_updator_overlapping(p, BaseT::root_iter(), l);
        
        return l;
    }
    
protected:
    typedef
        _TreeImpValueTypeBase<
            Alg_Tag,
            Key_Type,
            Set,
            _IntervalMaxMetadata,
            LT>    
        BaseT;
        
    typedef typename BaseT::TreeT TreeT;        

private:    
    void
    interval_max_updator_overlapping(PyObject * b_, PyObject * e_, void * node, PyObject * l)
    {
        PyObject * const interval = BaseT::internal_value_to_key_inc(BaseT::iter_value(node));        
        PyObject * const b = PySequence_Fast_GET_ITEM(interval, 0);
        PyObject * const e = PySequence_Fast_GET_ITEM(interval, 1);
        DBG_ASSERT(b != NULL && e != NULL);
        BANYAN_PYOBJECT_DECREF(interval);
        
        if (PyObject_RichCompareBool(b, e_, Py_LE) && PyObject_RichCompareBool(b_, e, Py_LE)) 
            if (PyList_Append(l, interval) == -1) {
                PyErr_NoMemory();
                std::bad_alloc();
            }
            
        void * const left_node = BaseT::left_iter(node);
        if (left_node != NULL) {            
            if (PyObject_RichCompareBool(b_, BaseT::iter_internal_metadata(left_node).max_, Py_LE)) 
                interval_max_updator_overlapping(b_, e_, left_node, l);
            else
                BaseT::delete_node_iter(left_node);       
        }            
                
        void * const right_node = BaseT::right_iter(node);
        if (right_node != NULL) {            
            if (PyObject_RichCompareBool(e_, BaseT::iter_internal_metadata(right_node).min_, Py_GE)) 
                interval_max_updator_overlapping(b_, e_, right_node, l);
            else
                BaseT::delete_node_iter(right_node);       
        }            
        
        BaseT::delete_node_iter(node);       
    }

    void
    interval_max_updator_overlapping(PyObject * p, void * node, PyObject * l)
    {    
        PyObject * const interval = BaseT::internal_value_to_key_inc(BaseT::iter_value(node));        
        PyObject * const b = PySequence_Fast_GET_ITEM(interval, 0);
        PyObject * const e = PySequence_Fast_GET_ITEM(interval, 1);
        BANYAN_PYOBJECT_DECREF(interval);
        
        if (PyObject_RichCompareBool(b, p, Py_LE) && PyObject_RichCompareBool(p, e, Py_LE)) 
            if (PyList_Append(l, interval) == -1) {
                PyErr_NoMemory();
                std::bad_alloc();
            }
            
        void * const left_node = BaseT::left_iter(node);
        if (left_node != NULL) {            
            if (PyObject_RichCompareBool(p, BaseT::iter_internal_metadata(left_node).max_, Py_LE)) 
                interval_max_updator_overlapping(p, left_node, l);
            else
                BaseT::delete_node_iter(left_node);       
        }            
                
        void * const right_node = BaseT::right_iter(node);
        if (right_node != NULL) {            
            if (PyObject_RichCompareBool(p, BaseT::iter_internal_metadata(right_node).min_, Py_GE)) 
                interval_max_updator_overlapping(p, right_node, l);
            else
                BaseT::delete_node_iter(right_node);       
        }            
        
        BaseT::delete_node_iter(node);       
    }
};

#endif // #ifndef _TREE_IMP_INTERVAL_MAX_METADATA_BASE_HPP
    
