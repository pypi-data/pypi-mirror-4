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

struct _NullMetadataTag{};
struct _RankMetadataTag{};
struct _MinGapMetadataTag{};
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

template<
    class Alg_Tag,
    typename Key_Type,
    bool Set,
    class LT>
struct _TreeImpMetadataBase<
        Alg_Tag,
        Key_Type,
        Set,
        _NullMetadataTag,
        LT> :
    public _TreeImpValueTypeBase<
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

    virtual PyObject *
    iter_metadata(void * it)
    {
        Py_RETURN_NONE;
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
        _RankMetadataTag,
        LT> :
    public _TreeImpValueTypeBase<
        Alg_Tag,
        Key_Type,
        Set,
        _RankMetadata,
        LT>    
{
protected:
    typedef
        _TreeImpValueTypeBase<
            Alg_Tag,
            Key_Type,
            Set,
            _RankMetadata,
            LT>    
        BaseT;
        
    typedef typename BaseT::TreeT TreeT;        

protected: 
    explicit
    _TreeImpMetadataBase(PyObject * seq, PyObject * metadata, const LT & lt) :
        BaseT(seq, _RankMetadata(), lt)
    {
        DBG_ASSERT(seq != NULL);
        DBG_ASSERT(metadata == NULL);
    }   

    virtual PyObject *
    iter_metadata(void * it)
    {                
        const size_t rank = BaseT::iter_internal_metadata(it).rank;
#if PY_MAJOR_VERSION >= 3
        return PyLong_FromLong(rank);
#else // #if PY_MAJOR_VERSION >= 3
        return PyInt_FromLong(rank);            
#endif // #if PY_MAJOR_VERSION >= 3
    }

    virtual PyObject *
    rank_updator_kth(size_t k)
    {
        if (k >= BaseT::tree.size()) {
            PyErr_SetObject(
                PyExc_IndexError, 
#if PY_MAJOR_VERSION >= 3
                PyLong_FromLong(k));
#else // #if PY_MAJOR_VERSION >= 3
                PyInt_FromLong(k));            
#endif // #if PY_MAJOR_VERSION >= 3
            return NULL;
        }            

        const typename TreeT::NodeT * const n = static_cast<const typename TreeT::NodeT *>(
            _rank_updator_kth(	BaseT::tree.node_begin(), k));
        return BaseT::internal_value_to_key_inc(n->val);
    }

    virtual PyObject *
    rank_updator_order(PyObject * key)
    {
        typename TreeT::Iterator b = 
            BaseT::tree.lower_bound(BaseT::key_to_internal_key(key));
        const size_t o = b == BaseT::tree.end()? 
            BaseT::tree.size() :
            _rank_updator_order(b.p);                        
#if PY_MAJOR_VERSION >= 3
        return PyLong_FromLong(o);            
#else // #if PY_MAJOR_VERSION >= 3
        return PyInt_FromLong(o);            
#endif // #if PY_MAJOR_VERSION >= 3
    }
};

template<
    typename Key_Type,
    bool Set,
    class LT>
struct _TreeImpMetadataBase<
        _OVTreeTag,
        Key_Type,
        Set,
        _RankMetadataTag,
        LT> :
    public _TreeImpValueTypeBase<
        _OVTreeTag,
        Key_Type,
        Set,
        _NullMetadata,
        LT>    
{
protected:
    typedef
        _TreeImpValueTypeBase<
            _OVTreeTag,
            Key_Type,
            Set,
            _NullMetadata,
            LT>    
        BaseT;
        
    typedef typename BaseT::TreeT TreeT;        

protected: 
    explicit
    _TreeImpMetadataBase(PyObject * seq, PyObject * metadata, const LT & lt) :
        BaseT(seq, _NullMetadata(), lt)
    {
        DBG_ASSERT(seq != NULL);
    }   

    virtual PyObject *
    iter_metadata(void * it)
    {
        const size_t rank = BaseT::iter_size(it);
#if PY_MAJOR_VERSION >= 3
        return PyLong_FromLong(rank);
#else // #if PY_MAJOR_VERSION >= 3
        return PyInt_FromLong(rank);            
#endif // #if PY_MAJOR_VERSION >= 3
    }

    virtual PyObject *
    rank_updator_kth(size_t k)
    {    
        if (k >= BaseT::tree.size()) {
            PyErr_SetObject(
                PyExc_IndexError, 
#if PY_MAJOR_VERSION >= 3
                PyLong_FromLong(k));
#else // #if PY_MAJOR_VERSION >= 3
                PyInt_FromLong(k));            
#endif // #if PY_MAJOR_VERSION >= 3
            return NULL;
        }            
            
        return BaseT::internal_value_to_key_inc(BaseT::tree.buf[k]);            
    }

    virtual PyObject *
    rank_updator_order(PyObject * key)
    {
        typename TreeT::Iterator b = 
            BaseT::tree.lower_bound(BaseT::key_to_internal_key(key));
        const size_t o = std::distance(BaseT::tree.begin(), b);                      
#if PY_MAJOR_VERSION >= 3
        return PyLong_FromLong(o);            
#else // #if PY_MAJOR_VERSION >= 3
        return PyInt_FromLong(o);            
#endif // #if PY_MAJOR_VERSION >= 3
    }
};

template<typename Key_Type>
struct __MinGapMetadata
{
    __MinGapMetadata() 
    {
        PyErr_SetString(PyExc_TypeError, "MinGapUpdator incompatible with type");
        throw std::logic_error("MinGapUpdator incompatible with type");    
    }

    template<typename T, class C>
    void 
    update(const T &, const C *, const C *)
    {
        DBG_VERIFY(false);
    }
    
    PyObject *
    repr_inc() const
    {
        DBG_VERIFY(false);
        return NULL;
    }
    
    PyObject *
    val_inc() const
    {
        DBG_VERIFY(false);
        return NULL;
    }

    int 
    traverse(visitproc, void *)
    {
        DBG_VERIFY(false);
        return 0;
    }

    Key_Type min_gap;
};

template<>
struct __MinGapMetadata<long> :
    public _MinGapMetadata<long> 
{
    typedef __MinGapMetadata<long> ThisT;

    void 
    update(const std::pair<long, PyObject *> & key, const ThisT * l, const ThisT * r)
    {
        _MinGapMetadata<long>::update(key.first, l, r);
    }
    
    PyObject *
    repr_inc() const
    {
        if (min_gap < 0)
            Py_RETURN_NONE;
            
#if PY_MAJOR_VERSION >= 3
        return PyLong_FromLong(min_gap);
#else // #if PY_MAJOR_VERSION >= 3
        return PyInt_FromLong(min_gap);            
#endif // #if PY_MAJOR_VERSION >= 3                    
    }
    
    PyObject *
    val_inc() const
    {
        if (min_gap < 0) {
            PyErr_SetString(PyExc_RuntimeError, "Min-gap undefined");          
            return NULL;
        }            
            
#if PY_MAJOR_VERSION >= 3
        return PyLong_FromLong(min_gap);
#else // #if PY_MAJOR_VERSION >= 3
        return PyInt_FromLong(min_gap);            
#endif // #if PY_MAJOR_VERSION >= 3                    
    }

    int 
    traverse(visitproc, void *)
    {
        return 0;
    }
};

template<>
struct __MinGapMetadata<double> :
    public _MinGapMetadata<double> 
{
    typedef __MinGapMetadata<double> ThisT;

    void 
    update(const std::pair<double, PyObject *> & key, const ThisT * l, const ThisT * r)
    {
        _MinGapMetadata<double>::update(key.first, l, r);
    }

    PyObject *
    repr_inc() const
    {
        if (min_gap < 0)
            Py_RETURN_NONE;
            
        return PyFloat_FromDouble(min_gap);            
    }
    
    PyObject *
    val_inc() const
    {
        if (min_gap < 0) {
            PyErr_SetString(PyExc_RuntimeError, "Min-gap undefined");          
            return NULL;
        }            
            
        return PyFloat_FromDouble(min_gap);            
    }

    int 
    traverse(visitproc, void *)
    {
        return 0;
    }
};

template<>
struct __MinGapMetadata<PyObject *>
{
    typedef __MinGapMetadata<PyObject *> ThisT;
    
    __MinGapMetadata() :
        min_(NULL),
        max_(NULL),
        min_gap(NULL)
    {
        // Do nothing.
    }        
    
    __MinGapMetadata(const ThisT & other)  :
        min_(other.min_),
        max_(other.max_),
        min_gap(other.min_gap)
    {
        if (min_ != NULL) 
            BANYAN_PYOBJECT_INCREF(min_);
        if (max_ != NULL) 
            BANYAN_PYOBJECT_INCREF(max_);
        if (min_gap != NULL) 
            BANYAN_PYOBJECT_INCREF(min_gap);
    }
    
    __MinGapMetadata & 
    operator=(const ThisT & other) 
    {
        if (this != &other)
        {
            if (min_ != NULL) 
                BANYAN_PYOBJECT_DECREF(min_);
            if (max_ != NULL) 
                BANYAN_PYOBJECT_DECREF(max_);
            if (min_gap != NULL) 
                BANYAN_PYOBJECT_DECREF(min_gap);
                
            min_ = other.min_;
            max_ = other.max_;
            min_gap = other.min_gap;
            
            if (min_ != NULL) 
                BANYAN_PYOBJECT_INCREF(min_);
            if (max_ != NULL) 
                BANYAN_PYOBJECT_INCREF(max_);
            if (min_gap != NULL) 
                BANYAN_PYOBJECT_INCREF(min_gap);
        }
        
        return *this;
    }
    
    virtual ~__MinGapMetadata()
    {
        if (min_ != NULL) 
            BANYAN_PYOBJECT_DECREF(min_);
        if (max_ != NULL) 
            BANYAN_PYOBJECT_DECREF(max_);
        if (min_gap != NULL) 
            BANYAN_PYOBJECT_DECREF(min_gap);
    }

    void 
    update(PyObject * key, const ThisT * l, const ThisT * r)
    {
        if (min_ != NULL) 
            BANYAN_PYOBJECT_DECREF(min_);
        if (max_ != NULL) 
            BANYAN_PYOBJECT_DECREF(max_);
        if (min_gap != NULL) 
            BANYAN_PYOBJECT_DECREF(min_gap);
        
        min_ = max_ = key;
        min_gap = NULL;
        
        if (l != NULL) {
            min_ = l->min_;
            
            min_gap = child_min_gap_inc(key, l->max_, l->min_gap);
            DBG_ASSERT(min_gap != NULL);
        }
        if (r != NULL) {
            max_ = r->max_;
            
            PyObject * const right_min_gap = child_min_gap_inc(key, r->min_, r->min_gap);
            
            if (min_gap == NULL)
                min_gap = right_min_gap;
            else if (min_gap != NULL && PyObject_RichCompareBool(right_min_gap, min_gap, Py_LT)) {
                BANYAN_PYOBJECT_DECREF(min_gap);
                min_gap = right_min_gap;
            }
            else
                BANYAN_PYOBJECT_DECREF(right_min_gap);                            
            DBG_ASSERT(min_gap != NULL);
        }
        
        DBG_VERIFY((l == NULL && r == NULL) || min_gap != NULL);
        
        BANYAN_PYOBJECT_INCREF(min_);
        BANYAN_PYOBJECT_INCREF(max_);
    }
    
    PyObject * 
    child_min_gap_inc(PyObject * key, PyObject * child_ext, PyObject * child_min_gap) 
    {
        PyObject * const gap = PyNumber_Subtract(key, child_ext);
        if (gap == NULL) {
            PyErr_SetString(PyExc_TypeError, "Failed to subtract");
            throw std::logic_error("Failed to subtract");
        }
        BANYAN_PYOBJECT_DUMMY_INCREF(gap);
        PyObject * const abs_gap = PyNumber_Absolute(gap);
        if (abs_gap == NULL) {
            PyErr_SetString(PyExc_TypeError, "Failed to take absolute value");
            throw std::logic_error("Failed to take absolute value");
        }
        BANYAN_PYOBJECT_DUMMY_INCREF(abs_gap);
        BANYAN_PYOBJECT_DECREF(gap);     
        
        if (child_min_gap == NULL || PyObject_RichCompareBool(abs_gap, child_min_gap, Py_LE))
            return abs_gap;
 
        BANYAN_PYOBJECT_DECREF(abs_gap);
        BANYAN_PYOBJECT_INCREF(child_min_gap);
        return child_min_gap;
    }

    int 
    traverse(visitproc visit, void * arg)
    {
        if (min_ != NULL)
            Py_VISIT(min_);
        if (max_ != NULL)
            Py_VISIT(max_);
        if (min_gap != NULL)            
            Py_VISIT(min_gap);
        return 0;            
    }

    PyObject *
    repr_inc() const
    {
        if (min_gap == NULL)
            Py_RETURN_NONE;
            
        BANYAN_PYOBJECT_INCREF(min_gap);
        return min_gap;            
    }
    
    PyObject *
    val_inc() const
    {
        if (min_gap == NULL) { 
            PyErr_SetString(PyExc_RuntimeError, "Min-gap undefined");          
            
            return NULL;
        }            
            
        BANYAN_PYOBJECT_INCREF(min_gap);
        return min_gap;            
    }

    PyObject * min_, * max_, * min_gap;
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
        _MinGapMetadataTag,
        LT> :
    public _TreeImpValueTypeBase<
        Alg_Tag,
        Key_Type,
        Set,
        __MinGapMetadata<Key_Type>,
        LT>    
{
protected:
    typedef
        _TreeImpValueTypeBase<
            Alg_Tag,
            Key_Type,
            Set,
            __MinGapMetadata<Key_Type>,
            LT>    
        BaseT;
        
    typedef typename BaseT::TreeT TreeT;        

protected: 
    explicit
    _TreeImpMetadataBase(PyObject * seq, PyObject * metadata, const LT & lt) :
        BaseT(seq, __MinGapMetadata<Key_Type>(), lt)
    {
        DBG_ASSERT(seq != NULL);
        DBG_ASSERT(metadata == NULL);
    }   

    virtual PyObject *
    iter_metadata(void * it)
    {                
        return BaseT::iter_internal_metadata(it).repr_inc();
    }

    virtual PyObject *
    min_gap_updator_min_gap()
    {    
        void * const root = BaseT::root_iter();
        if (root == NULL) {
            PyErr_SetString(PyExc_RuntimeError, "Min-gap undefined");          
            return NULL;
        }            

        PyObject * const ret = BaseT::iter_internal_metadata(root).val_inc();    
        
        BaseT::delete_node_iter(root);
        
        return ret;
    }

    int
    traverse(visitproc visit, void * arg)
    {
        int v = BaseT::traverse(visit, arg);
        if (v)
            return v;
    
        v = BaseT::tree.meta().traverse(visit, arg);        
        if (v)
            return v;
            
        // Tmp Ami
        /*            
        for (typename TreeT::Iterator it = BaseT::tree.begin(); it != BaseT::end(); ++it) {
            Py_VISIT(it->first.second);            
            Py_VISIT(it->second);
        }*/
                
        return 0;            
    }
};

#endif // #ifndef _TREE_IMP_METADATA_BASE_HPP
    
