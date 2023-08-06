/*
 * Copyright 2013 The py-lmdb authors, all rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted only as authorized by the OpenLDAP
 * Public License.
 *
 * A copy of this license is available in the file LICENSE in the
 * top-level directory of the distribution or, alternatively, at
 * <http://www.OpenLDAP.org/license.html>.
 *
 * OpenLDAP is a registered trademark of the OpenLDAP Foundation.
 *
 * Individual files and/or contributed packages may be copyright by
 * other parties and/or subject to additional restrictions.
 *
 * This work also contains materials derived from public sources.
 *
 * Additional information about OpenLDAP can be obtained at
 * <http://www.openldap.org/>.
 */

#include <sys/stat.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>

#include "Python.h"
#include "structmember.h"

#include "lmdb.h"

#define DEBUG(s, ...) \
    fprintf(stderr, "lmdb.cpython: %s:%d: " s "\n", __func__, __LINE__, \
            ## __VA_ARGS__);

#define NODEBUG

#ifdef NODEBUG
#undef DEBUG
#define DEBUG(s, ...)
#endif

#define NOINLINE __attribute__((noinline))

static PyObject *Error;
static PyObject *append_s;
static PyObject *buffers_s;
static PyObject *create_s;
static PyObject *db_s;
static PyObject *default_s;
static PyObject *delete_s;
static PyObject *dupdata_s;
static PyObject *dupsort_s;
static PyObject *key_s;
static PyObject *keys_s;
static PyObject *map_async_s;
static PyObject *map_size_s;
static PyObject *max_dbs_s;
static PyObject *max_readers_s;
static PyObject *metasync_s;
static PyObject *mode_s;
static PyObject *name_s;
static PyObject *overwrite_s;
static PyObject *parent_s;
static PyObject *path_s;
static PyObject *readonly_s;
static PyObject *reverse_key_s;
static PyObject *subdir_s;
static PyObject *sync_s;
static PyObject *txn_s;
static PyObject *value_s;
static PyObject *values_s;
static PyObject *write_s;

extern PyTypeObject PyDatabase_Type;
extern PyTypeObject PyEnvironment_Type;
extern PyTypeObject PyTransaction_Type;
extern PyTypeObject PyCursor_Type;
extern PyTypeObject PyIterator_Type;

struct EnvObject;


// So evil.
typedef struct {
    PyObject_HEAD
    PyObject *b_base;
    void *b_ptr;
    Py_ssize_t b_size;
    Py_ssize_t b_offset;
    int b_readonly;
    long b_hash;
} PyBufferObject;

struct list_head {
    struct lmdb_object *prev;
    struct lmdb_object *next;
};

#define LmdbObject_HEAD \
    PyObject_HEAD \
    struct list_head siblings; \
    struct list_head children; \
    int valid;

struct lmdb_object {
    LmdbObject_HEAD
};

#define OBJECT_INIT(o) \
    ((struct lmdb_object *)o)->siblings.prev = NULL; \
    ((struct lmdb_object *)o)->siblings.next = NULL; \
    ((struct lmdb_object *)o)->children.prev = NULL; \
    ((struct lmdb_object *)o)->children.next = NULL; \
    ((struct lmdb_object *)o)->valid = 1;


/*
 * Invalidation works by keeping a list of transactions attached to the
 * environment, which in turn have a list of cursors attached to the
 * transaction. The pointers are at the same offset so a generic function is
 * used.
 *
 * To save effort, tp_clear is overloaded to be the object's invalidation
 * function, instead of carrying a separate pointer around. Objects are added
 * to their parent's list during construction and removed only during
 * deallocation.
 *
 * When the environment is closed, it walks its list calling tp_clear on each
 * child, which in turn walk their own lists.
 *
 * Child transactions are added to their parent transaction's list.
 *
 * Iterators keep no significant state, so they are not tracked.
 */

static void link_child(struct lmdb_object *parent, struct lmdb_object *child)
{
    struct lmdb_object *sibling = parent->children.next;
    if(sibling) {
        child->siblings.next = sibling;
        sibling->siblings.prev = child;
    }
    parent->children.next = child;
}

static void unlink_child(struct lmdb_object *parent, struct lmdb_object *child)
{
    if(! parent) {
        return;
    }

    struct lmdb_object *prev = child->siblings.prev;
    struct lmdb_object *next = child->siblings.next;
    if(prev) {
        prev->siblings.next = next;
             // If double unlink_child(), this test my legitimately fail:
    } else if(parent->children.next == child) {
        parent->children.next = next;
    }
    if(next) {
        next->siblings.prev = prev;
    }
    child->siblings.prev = NULL;
    child->siblings.next = NULL;
}

static void invalidate(struct lmdb_object *parent)
{
    struct lmdb_object *child = parent->children.next;
    while(child) {
        struct lmdb_object *next = child->siblings.next;
        DEBUG("invalidating parent=%p child %p", parent, child)
        child->ob_type->tp_clear((PyObject *) child);
        child = next;
    }
}

#define LINK_CHILD(parent, child) link_child((void *)parent, (void *)child);
#define UNLINK_CHILD(parent, child) unlink_child((void *)parent, (void *)child);
#define INVALIDATE(parent) invalidate((void *)parent);


struct EnvObject;

typedef struct {
    LmdbObject_HEAD
    struct EnvObject *env; // Not refcounted.
    MDB_dbi dbi;
} DbObject;

typedef struct EnvObject {
    LmdbObject_HEAD
    MDB_env *env;
    DbObject *main_db;
} EnvObject;

typedef struct {
    LmdbObject_HEAD
    EnvObject *env;

    MDB_txn *txn;
    int buffers;
    PyBufferObject *key_buf;
} TransObject;

typedef struct {
    LmdbObject_HEAD
    TransObject *trans;

    int positioned;
    MDB_cursor *curs;
    PyBufferObject *key_buf;
    PyBufferObject *val_buf;
    PyObject *item_tup;
    MDB_val key;
    MDB_val val;
} CursorObject;


// Iterator protocol requires 'next' public method, which we want to use for
// MDB. So iterator needs to be a separate object to implement the protocol
// correctly (option #2 was setting .tp_next but exposing MDB next(), which is
// even worse).
typedef struct {
    PyObject_HEAD
    CursorObject *curs;
    int started;
    int op;
    PyObject *(*val_func)(CursorObject *);
} IterObject;




// ----------- helpers
//
//
//

enum field_type { TYPE_EOF, TYPE_UINT, TYPE_SIZE, TYPE_ADDR };

struct dict_field {
    enum field_type type;
    const char *name;
    int offset;
};


/*
 * Convert the structure `o` described by `fields` to a dict and return the new
 * dict.
 */
static PyObject *
dict_from_fields(void *o, const struct dict_field *fields)
{
    PyObject *dict = PyDict_New();
    if(! dict) {
        return NULL;
    }

    while(fields->type != TYPE_EOF) {
        uint8_t *p = ((uint8_t *) o) + fields->offset;
        unsigned PY_LONG_LONG l = 0;
        if(fields->type == TYPE_UINT) {
            l = *(unsigned int *)p;
        } else if(fields->type == TYPE_SIZE) {
            l = *(size_t *)p;
        } else if(fields->type == TYPE_ADDR) {
            l = (intptr_t) *(void **)p;
        }

        PyObject *lo = PyLong_FromUnsignedLongLong(l);
        if(! lo) {
            Py_DECREF(dict);
            return NULL;
        }

        if(PyDict_SetItemString(dict, fields->name, lo)) {
            Py_DECREF(lo);
            Py_DECREF(dict);
            return NULL;
        }
        Py_DECREF(lo);
        fields++;
    }
    return dict;
}


static PyObject * NOINLINE
buffer_from_val(PyBufferObject **bufp, MDB_val *val)
{
    PyBufferObject *buf = *bufp;
    if(! buf) {
        buf = (PyBufferObject *) PyBuffer_FromMemory("", 0);
        if(! buf) {
            return NULL;
        }
        *bufp = buf;
    }

    buf->b_hash = -1;
    buf->b_ptr = val->mv_data;
    buf->b_size = val->mv_size;
    Py_INCREF(buf);
    return (PyObject *) buf;
}


static PyObject *
string_from_val(MDB_val *val)
{
    return PyString_FromStringAndSize(val->mv_data, val->mv_size);
}


static int NOINLINE
val_from_buffer(MDB_val *val, PyObject *buf)
{
    if(PyString_CheckExact(buf)) {
        val->mv_data = PyString_AS_STRING(buf);
        val->mv_size = Py_SIZE(buf);
        return 0;
    }
    return PyObject_AsReadBuffer(buf,
        (const void **) &val->mv_data,
        (Py_ssize_t *) &val->mv_size);
}



// ------------------------
// Exceptions.
// ------------------------

static void * NOINLINE
err_set(const char *what, int rc)
{
    PyErr_Format(Error, "%s: %s", what, mdb_strerror(rc));
    return NULL;
}

static void * NOINLINE
err_invalid(void)
{
    PyErr_Format(Error, "Attempt to operate on closed/deleted/dropped object.");
    return NULL;
}

static void * NOINLINE
type_error(const char *what)
{
    PyErr_Format(PyExc_TypeError, "%s", what);
    return NULL;
}


/// ------------------------------
// argument parsing
//-------------------------------

#define OFFSET(k, y) offsetof(struct k, y)
enum arg_type {ARG_EOF, ARG_BOOL, ARG_OBJ, ARG_BUF, ARG_STR, ARG_INT};
struct argspec {
    unsigned short type;
    unsigned short offset;
    PyObject **name;
    PyTypeObject *objtype;
};


static int
parse_arg(const struct argspec *spec, PyObject *val, void *out)
{
    void *dst = ((uint8_t *)out) + spec->offset;
    int ret = 0;

    if(val != Py_None) {
        switch(spec->type) {
        case ARG_EOF:
        case ARG_BOOL:
            *((int *)dst) = val == Py_True;
            break;
        case ARG_OBJ:
            if(spec->objtype && val->ob_type != spec->objtype) {
                type_error("invalid type");
                return -1;
            }
            *((PyObject **) dst) = val;
            break;
        case ARG_BUF:
            ret = val_from_buffer((MDB_val *)dst, val);
            break;
        case ARG_STR: {
            MDB_val mv;
            if(! (ret = val_from_buffer(&mv, val))) {
                *((char **) dst) = mv.mv_data;
            }
            break;
        }
        case ARG_INT:
            *((int *) dst) = PyLong_AsUnsignedLong(val);
            if(PyErr_Occurred()) {
                ret = -1;
            }
            break;
        }
    }
    return ret;
}


/**
 * Like PyArg_ParseTupleAndKeywords except types are specialized for this
 * module, keyword strings aren't dup'd every call and the code is >3x smaller.
 */
static int NOINLINE
parse_args(int valid, const struct argspec *argspec,
           PyObject *args, PyObject *kwds, void *out)
{
    if(! valid) {
        err_invalid();
        return -1;
    }

    unsigned set = 0;
    const struct argspec *spec = argspec;
    unsigned i;
    if(args) {
        int pargsize = PyTuple_GET_SIZE(args);
        i = 0;
        while(i < pargsize && spec->type != ARG_EOF) {
            if(parse_arg(spec, PyTuple_GET_ITEM(args, i), out)) {
                return -1;
            }
            set |= (1 << i++);
            spec++;
        }

        if(i >= pargsize && spec->type == ARG_EOF) {
            type_error("too many positional arguments.");
            return -1;
        }
    }

    if(kwds) {
        i = 0;
        int c = 0;
        for(spec = argspec; spec->type != ARG_EOF; spec++) {
            unsigned bit = 1 << i++;
            PyObject *val = PyDict_GetItem(kwds, *spec->name);
            if(val) {
                if(set & bit) {
                    PyErr_Format(PyExc_TypeError, "duplicate argument: %s",
                                 PyString_AS_STRING(*spec->name));
                    return -1;
                }
                if(parse_arg(spec, val, out)) {
                    return -1;
                }
                c++;
            }
        }

        if(c != PyDict_Size(kwds)) {
            type_error("unrecognized keyword argument");
            return -1;
        }
    }
    return 0;
}


// ----------------------------
// Database
// ----------------------------

static DbObject *
db_from_name(EnvObject *env, MDB_txn *txn, const char *name,
             unsigned int flags)
{
    MDB_dbi dbi;
    int rc;

    if((rc = mdb_dbi_open(txn, name, flags, &dbi))) {
        err_set("mdb_dbi_open", rc);
        return NULL;
    }

    DbObject *dbo = PyObject_New(DbObject, &PyDatabase_Type);
    if(! dbo) {
        return NULL;
    }

    OBJECT_INIT(dbo)
    LINK_CHILD(env, dbo)
    dbo->env = env; // no refcount
    dbo->dbi = dbi;
    DEBUG("DbObject '%s' opened at %p", name, dbo)
    return dbo;
}


static DbObject *
txn_db_from_name(EnvObject *env, const char *name,
                 unsigned int flags)
{
    int rc;
    MDB_txn *txn;
    if((rc = mdb_txn_begin(env->env, NULL, 0, &txn))) {
        err_set("mdb_txn_begin", rc);
        return NULL;
    }

    DbObject *dbo = db_from_name(env, txn, name, flags);
    if(! dbo) {
        mdb_txn_abort(txn);
        return NULL;
    }

    if((rc = mdb_txn_commit(txn))) {
        Py_DECREF(dbo);
        return err_set("mdb_txn_commit", rc);
    }
    return dbo;
}

static int
db_clear(DbObject *self)
{
    if(self->env) {
        UNLINK_CHILD(self->env, self)
        self->env = NULL;
    }
    self->valid = 0;
    return 0;
}

static void
db_dealloc(DbObject *self)
{
    db_clear(self);
    PyObject_Del(self);
}

PyTypeObject PyDatabase_Type = {
    PyObject_HEAD_INIT(NULL)
    .tp_basicsize = sizeof(DbObject),
    .tp_dealloc = (destructor) db_dealloc,
    .tp_clear = (inquiry) db_clear,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_name = "_Database"
};


// -------------------------
// Environment.
// -------------------------

static int
env_clear(EnvObject *self)
{
    DEBUG("kiling env..")
    if(self->env) {
        INVALIDATE(self)
        DEBUG("Closing env")
        mdb_env_close(self->env);
        self->env = NULL;
    }
    if(self->main_db) {
        Py_CLEAR(self->main_db);
    }
    return 0;
}

static void
env_dealloc(EnvObject *self)
{
    env_clear(self);
    PyObject_Del(self);
}

static PyObject *
env_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    struct env_new {
        char *path;
        int map_size;
        int subdir;
        int readonly;
        int metasync;
        int sync;
        int map_async;
        int mode;
        int create;
        int max_readers;
        int max_dbs;
    } arg = {NULL, 10485760, 1, 0, 1, 1, 0, 0644, 1, 126, 0};

    static const struct argspec argspec[] = {
        {ARG_STR, OFFSET(env_new, path), &path_s, NULL},
        {ARG_INT, OFFSET(env_new, map_size), &map_size_s, NULL},
        {ARG_BOOL, OFFSET(env_new, subdir), &subdir_s, NULL},
        {ARG_BOOL, OFFSET(env_new, readonly), &readonly_s, NULL},
        {ARG_BOOL, OFFSET(env_new, metasync), &metasync_s, NULL},
        {ARG_BOOL, OFFSET(env_new, sync), &sync_s, NULL},
        {ARG_BOOL, OFFSET(env_new, map_async), &map_async_s, NULL},
        {ARG_INT, OFFSET(env_new, mode), &mode_s, NULL},
        {ARG_BOOL, OFFSET(env_new, create), &create_s, NULL},
        {ARG_INT, OFFSET(env_new, max_readers), &max_readers_s, NULL},
        {ARG_INT, OFFSET(env_new, max_dbs), &max_dbs_s, NULL},
        {0, 0, 0, 0}
    };

    if(parse_args(1, argspec, args, kwds, &arg)) {
        return NULL;
    }

    if(! arg.path) {
        return type_error("'path' argument required");
    }

    EnvObject *self = PyObject_New(EnvObject, type);
    if(! self) {
        return NULL;
    }

    OBJECT_INIT(self)
    self->main_db = NULL;
    self->env = NULL;

    int rc;
    if((rc = mdb_env_create(&self->env))) {
        err_set("mdb_env_create", rc);
        goto fail;
    }

    if((rc = mdb_env_set_mapsize(self->env, arg.map_size))) {
        err_set("mdb_env_set_mapsize", rc);
        goto fail;
    }

    if((rc = mdb_env_set_maxreaders(self->env, arg.max_readers))) {
        err_set("mdb_env_set_maxreaders", rc);
        goto fail;
    }

    if((rc = mdb_env_set_maxdbs(self->env, arg.max_dbs))) {
        err_set("mdb_env_set_maxdbs", rc);
        goto fail;
    }

    if(arg.create && arg.subdir) {
        struct stat st;
        errno = 0;
        stat(arg.path, &st);
        if(errno == ENOENT) {
            if(mkdir(arg.path, 0700)) {
                PyErr_SetFromErrnoWithFilename(PyExc_OSError, arg.path);
                goto fail;
            }
        }
    }

    int flags = 0; //MDB_WRITEMAP;
    if(! arg.subdir) {
        flags |= MDB_NOSUBDIR;
    }
    if(arg.readonly) {
        flags |= MDB_RDONLY;
    }
    if(! arg.metasync) {
        flags |= MDB_NOMETASYNC;
    }
    if(! arg.sync) {
        flags |= MDB_NOSYNC;
    }
    if(arg.map_async) {
        flags |= MDB_MAPASYNC;
    }

    DEBUG("mdb_env_open(%p, '%s', %d, %o);", self->env, arg.path, flags, arg.mode)
    if((rc = mdb_env_open(self->env, arg.path, flags, arg.mode))) {
        err_set(arg.path, rc);
        goto fail;
    }

    self->main_db = txn_db_from_name(self, NULL, 0);
    if(self->main_db) {
        self->valid = 1;
        DEBUG("EnvObject '%s' opened at %p", arg.path, self)
        return (PyObject *) self;
    }

fail:
    DEBUG("initialization failed")
    if(self) {
        env_dealloc(self);
    }
    return NULL;
}


static PyObject *
make_trans(EnvObject *env, TransObject *parent, int write, int buffers)
{
    DEBUG("make_trans(env=%p, parent=%p, write=%d, buffers=%d)",
        env, parent, write, buffers)
    if(! env->valid) {
        return err_invalid();
    }

    MDB_txn *parent_txn = NULL;
    if(parent) {
        if(! parent->valid) {
            return err_invalid();
        }
        parent_txn = parent->txn;
    }

    TransObject *self = PyObject_New(TransObject, &PyTransaction_Type);
    if(! self) {
        return NULL;
    }

    int flags = write ? 0 : MDB_RDONLY;
    int rc = mdb_txn_begin(env->env, parent_txn, flags, &self->txn);
    if(rc) {
        PyObject_Del(self);
        return err_set("mdb_txn_begin", rc);
    }

    OBJECT_INIT(self)
    LINK_CHILD(env, self)
    self->env = env;
    Py_INCREF(env);
    self->buffers = buffers;
    self->key_buf = NULL;
    return (PyObject *)self;
}


static PyObject *
env_begin(EnvObject *self, PyObject *args, PyObject *kwds)
{
    struct env_begin {
        int buffers;
        int write;
        TransObject *parent;
    } arg = {0, 0, NULL};

    static const struct argspec argspec[] = {
        {ARG_BOOL, OFFSET(env_begin, buffers), &buffers_s, NULL},
        {ARG_BOOL, OFFSET(env_begin, write), &write_s, NULL},
        {ARG_OBJ, OFFSET(env_begin, parent), &parent_s, &PyTransaction_Type},
        {0, 0, 0, 0}
    };

    if(parse_args(self->valid, argspec, args, kwds, &arg)) {
        return NULL;
    }
    return make_trans(self, arg.parent, arg.write, arg.buffers);
}

static PyObject *
env_close(EnvObject *self)
{
    if(self->valid) {
        INVALIDATE(self)
        self->valid = 0;
        DEBUG("Closing env")
        mdb_env_close(self->env);
        self->env = NULL;
    }
    Py_RETURN_NONE;
}

static PyObject *
env_copy(EnvObject *self, PyObject *args)
{
    if(! self->valid) {
        return err_invalid();
    }

    PyObject *path;
    if(! PyArg_ParseTuple(args, "|O:copy", &path)) {
        return NULL;
    }
    return NULL;
}

static PyObject *
env_info(EnvObject *self)
{
    static const struct dict_field fields[] = {
        { TYPE_ADDR, "map_addr",        offsetof(MDB_envinfo, me_mapaddr) },
        { TYPE_SIZE, "map_size",        offsetof(MDB_envinfo, me_mapsize) },
        { TYPE_SIZE, "last_pgno",       offsetof(MDB_envinfo, me_last_pgno) },
        { TYPE_SIZE, "last_txnid",      offsetof(MDB_envinfo, me_last_txnid) },
        { TYPE_UINT, "max_readers",     offsetof(MDB_envinfo, me_maxreaders) },
        { TYPE_UINT, "num_readers",     offsetof(MDB_envinfo, me_numreaders) },
        { TYPE_EOF, NULL, 0 }
    };

    if(! self->valid) {
        return err_invalid();
    }

    MDB_envinfo info;
    int rc = mdb_env_info(self->env, &info);
    if(rc) {
        err_set("mdb_env_info", rc);
        return NULL;
    }
    return dict_from_fields(&info, fields);
}


static PyObject *
env_open_db(EnvObject *self, PyObject *args, PyObject *kwds)
{
    struct env_open_db {
        const char *name;
        TransObject *txn;
        int reverse_key;
        int dupsort;
        int create;
    } arg = {NULL, NULL, 0, 0, 1};

    static const struct argspec argspec[] = {
        {ARG_STR, OFFSET(env_open_db, name), &name_s, NULL},
        {ARG_OBJ, OFFSET(env_open_db, txn), &txn_s, &PyTransaction_Type},
        {ARG_BOOL, OFFSET(env_open_db, reverse_key), &reverse_key_s, NULL},
        {ARG_BOOL, OFFSET(env_open_db, dupsort), &dupsort_s, NULL},
        {ARG_BOOL, OFFSET(env_open_db, create), &create_s, NULL},
        {0, 0, 0, 0}
    };

    if(parse_args(1, argspec, args, kwds, &arg)) {
        return NULL;
    }

    int flags = 0;
    if(arg.reverse_key) {
        flags |= MDB_REVERSEKEY;
    }
    if(arg.dupsort) {
        flags |= MDB_DUPSORT;
    }
    if(arg.create) {
        flags |= MDB_CREATE;
    }

    if(arg.txn) {
        return (PyObject *) db_from_name(self, arg.txn->txn, arg.name, flags);
    } else {
        return (PyObject *) txn_db_from_name(self, arg.name, flags);
    }
}


static PyObject *
env_path(EnvObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }

    const char *path;
    int rc;
    if((rc = mdb_env_get_path(self->env, &path))) {
        return err_set("mdb_env_get_path", rc);
    }
    return PyString_FromString(path);
}


static PyObject *
env_stat(EnvObject *self)
{
    static const struct dict_field fields[] = {
        { TYPE_UINT, "psize",           offsetof(MDB_stat, ms_psize) },
        { TYPE_UINT, "depth",           offsetof(MDB_stat, ms_depth) },
        { TYPE_SIZE, "branch_pages",    offsetof(MDB_stat, ms_branch_pages) },
        { TYPE_SIZE, "leaf_pages",      offsetof(MDB_stat, ms_leaf_pages) },
        { TYPE_SIZE, "overflow_pages",  offsetof(MDB_stat, ms_overflow_pages) },
        { TYPE_SIZE, "entries",         offsetof(MDB_stat, ms_entries) },
        { TYPE_EOF, NULL, 0 }
    };

    if(! self->valid) {
        return err_invalid();
    }

    MDB_stat st;
    int rc = mdb_env_stat(self->env, &st);
    if(rc) {
        err_set("mdb_env_stat", rc);
        return NULL;
    }
    return dict_from_fields(&st, fields);
}

static PyObject *
env_sync(EnvObject *self, PyObject *arg)
{
    if(! self->valid) {
        return err_invalid();
    }

    int force = arg == NULL;
    if(arg) {
        int force = PyObject_IsTrue(arg);
        if(force == -1) {
            return NULL;
        }
    }

    int rc = mdb_env_sync(self->env, force);
    if(rc) {
        return err_set("mdb_env_sync", rc);
    }
    Py_RETURN_NONE;
}

static struct PyMethodDef env_methods[] = {
    {"begin", (PyCFunction)env_begin, METH_VARARGS|METH_KEYWORDS},
    {"close", (PyCFunction)env_close, METH_NOARGS},
    {"copy", (PyCFunction)env_copy, METH_VARARGS},
    {"info", (PyCFunction)env_info, METH_NOARGS},
    {"open_db", (PyCFunction)env_open_db, METH_VARARGS|METH_KEYWORDS},
    {"path", (PyCFunction)env_path, METH_NOARGS},
    {"stat", (PyCFunction)env_stat, METH_NOARGS},
    {"sync", (PyCFunction)env_sync, METH_OLDARGS},
    {NULL, NULL}
};


PyTypeObject PyEnvironment_Type = {
    PyObject_HEAD_INIT(0)
    .tp_basicsize = sizeof(EnvObject),
    .tp_dealloc = (destructor) env_dealloc,
    .tp_clear = (inquiry) env_clear,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = env_methods,
    .tp_name = "Environment",
    .tp_new = env_new,
};


// ==================================
/// cursors
// ==================================

static int
cursor_clear(CursorObject *self)
{
    if(self->valid) {
        INVALIDATE(self)
        UNLINK_CHILD(self->trans, self)
        mdb_cursor_close(self->curs);
        self->valid = 0;
    }
    if(self->key_buf) {
        self->key_buf->b_size = 0;
        Py_CLEAR(self->key_buf);
    }
    if(self->val_buf) {
        self->val_buf->b_size = 0;
        Py_CLEAR(self->val_buf);
    }
    if(self->item_tup) {
        Py_CLEAR(self->item_tup);
    }
    Py_CLEAR(self->trans);
    return 0;
}

static void
cursor_dealloc(CursorObject *self)
{
    DEBUG("destroying cursor")
    cursor_clear(self);
    PyObject_Del(self);
}

static PyObject *
make_cursor(DbObject *db, TransObject *trans)
{
    if(! trans->valid) {
        return err_invalid();
    }
    if(! db) {
        db = trans->env->main_db;
    }

    CursorObject *self = PyObject_New(CursorObject, &PyCursor_Type);
    int rc = mdb_cursor_open(trans->txn, db->dbi, &self->curs);
    if(rc) {
        PyObject_Del(self);
        return err_set("mdb_cursor_open", rc);
    }

    DEBUG("sizeof cursor = %d", (int) sizeof *self)
    OBJECT_INIT(self)
    LINK_CHILD(trans, self)
    self->positioned = 0;
    self->key_buf = NULL;
    self->val_buf = NULL;
    self->key.mv_size = 0;
    self->val.mv_size = 0;
    self->item_tup = NULL;
    self->trans = trans;
    Py_INCREF(self->trans);
    return (PyObject *) self;
}

static PyObject *
cursor_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    struct cursor_new {
        DbObject *db;
        TransObject *trans;
    } arg = {NULL, NULL};

    static const struct argspec argspec[] = {
        {ARG_OBJ, OFFSET(cursor_new, db), &db_s, &PyDatabase_Type},
        {ARG_OBJ, OFFSET(cursor_new, trans), &txn_s, &PyTransaction_Type},
        {0, 0, 0, 0}
    };

    if(parse_args(1, argspec, args, kwds, &arg)) {
        return NULL;
    }

    if(! (arg.db && arg.trans)) {
        return type_error("db and transaction parameters required.");
    }
    return make_cursor(arg.db, arg.trans);
}

static PyObject *
cursor_count(CursorObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }

    size_t count;
    int rc = mdb_cursor_count(self->curs, &count);
    if(rc) {
        return err_set("mdb_cursor_count", rc);
    }
    return PyLong_FromUnsignedLongLong(count);
}


static int
_cursor_get_c(CursorObject *self, enum MDB_cursor_op op)
{
    int rc = mdb_cursor_get(self->curs, &self->key, &self->val, op);
    self->positioned = rc == 0;
    if(rc) {
        self->key.mv_size = 0;
        self->val.mv_size = 0;
        if(rc != MDB_NOTFOUND) {
            if(! (rc == EINVAL && op == MDB_GET_CURRENT)) {
                err_set("mdb_cursor_get", rc);
                return -1;
            }
        }
    }
    return 0;
}


static PyObject *
_cursor_get(CursorObject *self, enum MDB_cursor_op op)
{
    if(_cursor_get_c(self, op)) {
        return NULL;
    }
    PyObject *res = self->positioned ? Py_True : Py_False;
    Py_INCREF(res);
    return res;
}


static PyObject *
cursor_delete(CursorObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }
    PyObject *ret = Py_False;
    if(self->positioned) {
        DEBUG("deleting key '%.*s'",
              (int) self->key.mv_size,
              (char*) self->key.mv_data)
        int rc = mdb_cursor_del(self->curs, 0);
        if(rc) {
            return err_set("mdb_cursor_del", rc);
        }
        ret = Py_True;
        _cursor_get_c(self, MDB_GET_CURRENT);
    }
    Py_INCREF(ret);
    return ret;
}


static PyObject *
cursor_first(CursorObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }
    return _cursor_get(self, MDB_FIRST);
}

static PyObject *
cursor_item(CursorObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }
    if(self->trans->buffers) {
        if(! buffer_from_val(&self->key_buf, &self->key)) {
            return NULL;
        }
        if(! buffer_from_val(&self->val_buf, &self->val)) {
            return NULL;
        }
        if(! self->item_tup) {
            self->item_tup = PyTuple_Pack(2, self->key_buf, self->val_buf);
        }
        Py_INCREF(self->item_tup);
        return self->item_tup;
    }

    PyObject *key = string_from_val(&self->key);
    if(! key) {
        return NULL;
    }
    PyObject *val = string_from_val(&self->val);
    if(! val) {
        Py_DECREF(key);
        return NULL;
    }
    PyObject *tup = PyTuple_Pack(2, key, val);
    if(! tup) {
        Py_DECREF(key);
        Py_DECREF(val);
        return NULL;
    }
    return tup;
}

static PyObject *
cursor_key(CursorObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }
    if(self->trans->buffers) {
        if(! buffer_from_val(&self->key_buf, &self->key)) {
            return NULL;
        }
        Py_INCREF(self->key_buf);
        return (PyObject *) self->key_buf;
    }
    return string_from_val(&self->key);
}

static PyObject *
cursor_last(CursorObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }
    return _cursor_get(self, MDB_LAST);
}

static PyObject *
cursor_next(CursorObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }
    return _cursor_get(self, MDB_NEXT);
}

static PyObject *
cursor_prev(CursorObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }
    return _cursor_get(self, MDB_PREV);
}

static PyObject *
cursor_put(CursorObject *self, PyObject *args, PyObject *kwds)
{
    struct cursor_put {
        MDB_val key;
        MDB_val val;
        int dupdata;
        int overwrite;
        int append;
    } arg = {{0, 0}, {0, 0}, 0, 1, 0};

    static const struct argspec argspec[] = {
        {ARG_BUF, OFFSET(cursor_put, key), &key_s, NULL},
        {ARG_BUF, OFFSET(cursor_put, val), &value_s, NULL},
        {ARG_BOOL, OFFSET(cursor_put, dupdata), &dupdata_s, NULL},
        {ARG_BOOL, OFFSET(cursor_put, overwrite), &overwrite_s, NULL},
        {ARG_BOOL, OFFSET(cursor_put, append), &append_s, NULL},
        {0, 0, 0, 0}
    };

    if(parse_args(self->valid, argspec, args, kwds, &arg)) {
        return NULL;
    }

    int flags = 0;
    if(! arg.dupdata) {
        flags |= MDB_NODUPDATA;
    }
    if(! arg.overwrite) {
        flags |= MDB_NOOVERWRITE;
    }
    if(! arg.append) {
        flags |= MDB_APPEND;
    }

    int rc = mdb_cursor_put(self->curs, &arg.key, &arg.val, flags);
    if(rc) {
        if(rc == MDB_KEYEXIST) {
            Py_RETURN_FALSE;
        }
        return err_set("mdb_put", rc);
    }
    Py_RETURN_TRUE;
}


static PyObject *
cursor_set_key(CursorObject *self, PyObject *arg)
{
    if(! self->valid) {
        return err_invalid();
    }
    if(val_from_buffer(&self->key, arg)) {
        return NULL;
    }
    return _cursor_get(self, MDB_SET_KEY);
}

static PyObject *
cursor_set_range(CursorObject *self, PyObject *arg)
{
    if(! self->valid) {
        return err_invalid();
    }
    if(val_from_buffer(&self->key, arg)) {
        return NULL;
    }
    if(self->key.mv_size) {
        return _cursor_get(self, MDB_SET_RANGE);
    }
    return _cursor_get(self, MDB_FIRST);
}

static PyObject *
cursor_value(CursorObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }
    if(self->trans->buffers) {
        if(! buffer_from_val(&self->val_buf, &self->val)) {
            return NULL;
        }
        Py_INCREF(self->val_buf);
        return (PyObject *) self->val_buf;
    }
    return string_from_val(&self->val);
}

// ==================================
// Cursor iteration
// ==================================

static PyObject *
iter_from_args(CursorObject *self, PyObject *args, PyObject *kwds,
                   enum MDB_cursor_op pos_op, enum MDB_cursor_op op)
{
    struct iter_from_args {
        int keys;
        int values;
    } arg = {1, 1};

    static const struct argspec argspec[] = {
        {ARG_BOOL, OFFSET(iter_from_args, keys), &keys_s, NULL},
        {ARG_BOOL, OFFSET(iter_from_args, values), &values_s, NULL},
        {0, 0, 0, 0}
    };

    if(parse_args(self->valid, argspec, args, kwds, &arg)) {
        return NULL;
    }

    if(! self->positioned) {
        if(_cursor_get_c(self, pos_op)) {
            return NULL;
        }
    }

    IterObject *iter = PyObject_New(IterObject, &PyIterator_Type);
    if(! iter) {
        return NULL;
    }

    if(! arg.values) {
        iter->val_func = (void *)cursor_key;
    } else if(! arg.keys) {
        iter->val_func = (void *)cursor_value;
    } else {
        iter->val_func = (void *)cursor_item;
    }

    iter->curs = self;
    Py_INCREF(self);
    iter->started = 0;
    iter->op = op;
    return (PyObject *) iter;
}

static PyObject *
cursor_iter(CursorObject *self)
{
    return iter_from_args(self, NULL, NULL, MDB_FIRST, MDB_NEXT);
}

static PyObject *
cursor_iternext(CursorObject *self, PyObject *args, PyObject *kwargs)
{
    return iter_from_args(self, args, kwargs, MDB_FIRST, MDB_NEXT);
}

static PyObject *
cursor_iterprev(CursorObject *self, PyObject *args, PyObject *kwargs)
{
    return iter_from_args(self, args, kwargs, MDB_LAST, MDB_PREV);
}

static struct PyMethodDef cursor_methods[] = {
    {"count", (PyCFunction)cursor_count, METH_NOARGS},
    {"delete", (PyCFunction)cursor_delete, METH_NOARGS},
    {"first", (PyCFunction)cursor_first, METH_NOARGS},
    {"item", (PyCFunction)cursor_item, METH_NOARGS},
    {"iternext", (PyCFunction)cursor_iternext, METH_VARARGS|METH_KEYWORDS},
    {"iterprev", (PyCFunction)cursor_iterprev, METH_VARARGS|METH_KEYWORDS},
    {"key", (PyCFunction)cursor_key, METH_NOARGS},
    {"last", (PyCFunction)cursor_last, METH_NOARGS},
    {"next", (PyCFunction)cursor_next, METH_NOARGS},
    {"prev", (PyCFunction)cursor_prev, METH_NOARGS},
    {"put", (PyCFunction)cursor_put, METH_VARARGS|METH_KEYWORDS},
    {"set_key", (PyCFunction)cursor_set_key, METH_O},
    {"set_range", (PyCFunction)cursor_set_range, METH_O},
    {"value", (PyCFunction)cursor_value, METH_NOARGS},
    {NULL, NULL}
};

PyTypeObject PyCursor_Type = {
    PyObject_HEAD_INIT(0)
    .tp_basicsize = sizeof(CursorObject),
    .tp_dealloc = (destructor) cursor_dealloc,
    .tp_clear = (inquiry) cursor_clear,
    .tp_flags = Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_ITER,
    .tp_iter = (getiterfunc)cursor_iter,
    .tp_methods = cursor_methods,
    .tp_name = "Cursor",
    .tp_new = cursor_new
};



/// ------------------------
// iterator
// -------------

static void
iter_dealloc(IterObject *self)
{
    DEBUG("destroying iterator")
    Py_CLEAR(self->curs);
    PyObject_Del(self);
}


static PyObject *
iter_iter(IterObject *self)
{
    Py_INCREF(self);
    return (PyObject *)self;
}

static PyObject *
iter_next(IterObject *self)
{
    if(! self->curs->valid) {
        return err_invalid();
    }
    if(! self->curs->positioned) {
        return NULL;
    }
    if(self->started) {
        if(_cursor_get_c(self->curs, self->op)) {
            return NULL;
        }
        if(! self->curs->positioned) {
            return NULL;
        }
    }
    PyObject *val = self->val_func(self->curs);
    self->started = 1;
    return val;
}

static struct PyMethodDef iter_methods[] = {
    {"next", (PyCFunction)cursor_next, METH_NOARGS},
    {NULL, NULL}
};

PyTypeObject PyIterator_Type = {
    PyObject_HEAD_INIT(0)
    .tp_basicsize = sizeof(IterObject),
    .tp_dealloc = (destructor) iter_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT|Py_TPFLAGS_HAVE_ITER,
    .tp_iter = (getiterfunc)iter_iter,
    .tp_iternext = (iternextfunc)iter_next,
    .tp_methods = iter_methods,
    .tp_name = "Iterator"
};


/// ------------------------
//transactions
//////////////////////
//
//
//

static int
trans_clear(TransObject *self)
{
    if(self->valid) {
        INVALIDATE(self)
        if(self->txn) {
            DEBUG("aborting")
            mdb_txn_abort(self->txn);
            self->txn = NULL;
        }
        self->valid = 0;
    }
    UNLINK_CHILD(self->env, self)
    Py_CLEAR(self->env);
    return 0;
}


static void
trans_dealloc(TransObject *self)
{
    DEBUG("deleting trans")
    trans_clear(self);
    PyObject_Del(self);
}


static PyObject *
trans_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    struct trans_new {
        EnvObject *env;
        TransObject *parent;
        int write;
        int buffers;
    } arg = {NULL, NULL, 0, 0};

    static const struct argspec argspec[] = {
        {ARG_OBJ, OFFSET(trans_new, env), &txn_s, &PyTransaction_Type},
        {ARG_OBJ, OFFSET(trans_new, parent), &parent_s, &PyTransaction_Type},
        {ARG_BOOL, OFFSET(trans_new, write), &write_s, NULL},
        {ARG_BOOL, OFFSET(trans_new, buffers), &buffers_s, NULL},
        {0, 0, 0, 0}
    };

    if(! arg.env) {
        return type_error("'env' argument required");
    }
    if(parse_args(1, argspec, args, kwds, &arg)) {
        return NULL;
    }
    return make_trans(arg.env, arg.parent, arg.write, arg.buffers);
}


static PyObject *
trans_abort(TransObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }
    DEBUG("aborting")
    INVALIDATE(self)
    mdb_txn_abort(self->txn);
    self->txn = NULL;
    self->valid = 0;
    Py_RETURN_NONE;
}

static PyObject *
trans_commit(TransObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }
    DEBUG("committing")
    INVALIDATE(self)
    int rc = mdb_txn_commit(self->txn);
    self->txn = NULL;
    self->valid = 0;
    if(rc) {
        return err_set("mdb_txn_commit", rc);
    }
    Py_RETURN_NONE;
}


static PyObject *
trans_cursor(TransObject *self, PyObject *args, PyObject *kwds)
{
    struct trans_cursor {
        DbObject *db;
    } arg = { 0 };

    static const struct argspec argspec[] = {
        {ARG_OBJ, OFFSET(trans_cursor, db), &db_s, &PyDatabase_Type},
        {0, 0, 0, 0}
    };

    if(parse_args(self->valid, argspec, args, kwds, &arg)) {
        return NULL;
    }
    if(! arg.db) {
        arg.db = self->env->main_db;
    }
    return make_cursor(arg.db, self);
}


static PyObject *
trans_delete(TransObject *self, PyObject *args, PyObject *kwds)
{
    struct trans_delete {
        MDB_val key;
        MDB_val val;
        DbObject *db;
    } arg = {{0, 0}, {0, 0}, NULL};

    static const struct argspec argspec[] = {
        {ARG_BUF, OFFSET(trans_delete, key), &key_s, NULL},
        {ARG_BUF, OFFSET(trans_delete, val), &value_s, NULL},
        {ARG_OBJ, OFFSET(trans_delete, db), &db_s, &PyDatabase_Type},
        {0, 0, 0, 0}
    };

    if(parse_args(self->valid, argspec, args, kwds, &arg)) {
        return NULL;
    }
    if(! arg.db) {
        arg.db = self->env->main_db;
    }
    MDB_val *val_ptr = arg.val.mv_size ? &arg.val : NULL;
    int rc = mdb_del(self->txn, arg.db->dbi, &arg.key, val_ptr);
    if(rc) {
        if(rc == MDB_NOTFOUND) {
             Py_RETURN_FALSE;
        }
        return err_set("mdb_del", rc);
    }
    Py_RETURN_TRUE;
}


static PyObject *
trans_drop(TransObject *self, PyObject *args, PyObject *kwds)
{
    struct trans_drop {
        DbObject *db;
        int delete;
    } arg = { NULL, 1 };

    static const struct argspec argspec[] = {
        {ARG_OBJ, OFFSET(trans_drop, db), &db_s, &PyDatabase_Type},
        {ARG_BOOL, OFFSET(trans_drop, delete), &delete_s, NULL},
        {0, 0, 0, 0}
    };

    if(parse_args(self->valid, argspec, args, kwds, &arg)) {
        return NULL;
    }
    if(! arg.db) {
        return type_error("'db' argument required.");
    }

    int rc = mdb_drop(self->txn, arg.db->dbi, arg.delete);
    if(rc) {
        return err_set("mdb_drop", rc);
    }
    Py_RETURN_NONE;
}

static PyObject *
trans_get(TransObject *self, PyObject *args, PyObject *kwds)
{
    struct trans_get {
        MDB_val key;
        PyObject *default_;
        DbObject *db;
    } arg = {{0, 0}, Py_None, self->env->main_db};

    static const struct argspec argspec[] = {
        {ARG_BUF, OFFSET(trans_get, key), &key_s, NULL},
        {ARG_OBJ, OFFSET(trans_get, default_), &default_s, NULL},
        {ARG_OBJ, OFFSET(trans_get, db), &db_s, &PyDatabase_Type},
        {0, 0, 0, 0}
    };

    if(parse_args(self->valid, argspec, args, kwds, &arg)) {
        return NULL;
    }

    if(! arg.key.mv_data) {
        return type_error("key must be given.");
    }

    MDB_val val;
    int rc = mdb_get(self->txn, arg.db->dbi, &arg.key, &val);
    if(rc) {
        if(rc == MDB_NOTFOUND) {
            Py_INCREF(arg.default_);
            return arg.default_;
        }
        return err_set("mdb_get", rc);
    }
    if(self->buffers) {
        return buffer_from_val(&self->key_buf, &val);
    }
    return string_from_val(&val);
}

static PyObject *
trans_put(TransObject *self, PyObject *args, PyObject *kwds)
{
    struct trans_put {
        MDB_val key;
        MDB_val value;
        int dupdata;
        int overwrite;
        int append;
        DbObject *db;
    } arg = {{0, 0}, {0, 0}, 0, 1, 0, self->env->main_db};

    static const struct argspec argspec[] = {
        {ARG_BUF, OFFSET(trans_put, key), &key_s, NULL},
        {ARG_BUF, OFFSET(trans_put, value), &value_s, NULL},
        {ARG_BOOL, OFFSET(trans_put, dupdata), &dupdata_s, NULL},
        {ARG_BOOL, OFFSET(trans_put, overwrite), &overwrite_s, NULL},
        {ARG_BOOL, OFFSET(trans_put, append), &append_s, NULL},
        {ARG_OBJ, OFFSET(trans_put, db), &db_s, &PyDatabase_Type},
        {0, 0, 0, 0}
    };

    if(parse_args(self->valid, argspec, args, kwds, &arg)) {
        return NULL;
    }

    int flags = 0;
    if(! arg.dupdata) {
        flags |= MDB_NODUPDATA;
    }
    if(! arg.overwrite) {
        flags |= MDB_NOOVERWRITE;
    }
    if(arg.append) {
        flags |= MDB_APPEND;
    }

    DEBUG("inserting '%.*s' (%d) -> '%.*s' (%d)",
        (int)arg.key.mv_size, (char *)arg.key.mv_data,
        (int)arg.key.mv_size,
        (int)arg.value.mv_size, (char *)arg.value.mv_data,
        (int)arg.value.mv_size)

    int rc = mdb_put(self->txn, (arg.db)->dbi, &arg.key, &arg.value, flags);
    if(rc) {
        if(rc == MDB_KEYEXIST) {
            Py_RETURN_FALSE;
        }
        return err_set("mdb_put", rc);
    }
    Py_RETURN_TRUE;
}

static PyObject *trans_enter(TransObject *self)
{
    if(! self->valid) {
        return err_invalid();
    }
    Py_INCREF(self);
    return (PyObject *)self;
}

static PyObject *trans_exit(TransObject *self, PyObject *args)
{
    if(! self->valid) {
        return err_invalid();
    }
    if(PyTuple_GET_ITEM(args, 0) == Py_None) {
        return trans_commit(self);
    } else {
        return trans_abort(self);
    }
}


static struct PyMethodDef trans_methods[] = {
    {"__enter__", (PyCFunction)trans_enter, METH_NOARGS},
    {"__exit__", (PyCFunction)trans_exit, METH_VARARGS},
    {"abort", (PyCFunction)trans_abort, METH_NOARGS},
    {"commit", (PyCFunction)trans_commit, METH_NOARGS},
    {"cursor", (PyCFunction)trans_cursor, METH_VARARGS|METH_KEYWORDS},
    {"delete", (PyCFunction)trans_delete, METH_VARARGS|METH_KEYWORDS},
    {"drop", (PyCFunction)trans_drop, METH_VARARGS|METH_KEYWORDS},
    {"get", (PyCFunction)trans_get, METH_VARARGS|METH_KEYWORDS},
    {"put", (PyCFunction)trans_put, METH_VARARGS|METH_KEYWORDS},
    {NULL, NULL}
};

PyTypeObject PyTransaction_Type = {
    PyObject_HEAD_INIT(0)
    .tp_basicsize = sizeof(TransObject),
    .tp_dealloc = (destructor) trans_dealloc,
    .tp_clear = (inquiry) trans_clear,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = trans_methods,
    .tp_name = "Transaction",
    .tp_new = trans_new,
};


static int add_type(PyObject *mod, PyTypeObject *type)
{
    if(PyType_Ready(type)) {
        return -1;
    }
    return PyObject_SetAttrString(mod, type->tp_name, (PyObject *)type);
 }

PyMODINIT_FUNC
initcpython(void)
{
    PyObject *mod = Py_InitModule3("cpython", NULL, "");
    if(! mod) {
        return;
    }

    static PyTypeObject *types[] = {
        &PyEnvironment_Type,
        &PyCursor_Type,
        &PyTransaction_Type,
        &PyIterator_Type,
        &PyDatabase_Type,
        NULL
    };
    int i;
    for(i = 0; types[i]; i++) {
        if(add_type(mod, types[i])) {
            return;
        }
    }

    static struct { PyObject **obj; const char *s; } strs[] = {
        {&append_s, "append"},
        {&buffers_s, "buffers"},
        {&create_s, "create"},
        {&db_s, "db"},
        {&default_s, "default"},
        {&dupdata_s, "dupdata"},
        {&dupsort_s, "dupsort"},
        {&key_s, "key"},
        {&keys_s, "keys"},
        {&map_async_s, "map_async"},
        {&map_size_s, "map_size"},
        {&max_dbs_s, "max_dbs"},
        {&max_readers_s, "max_readers"},
        {&metasync_s, "metasync"},
        {&mode_s, "mode"},
        {&name_s, "name"},
        {&overwrite_s, "overwrite"},
        {&parent_s, "parent"},
        {&path_s, "path"},
        {&readonly_s, "readonly"},
        {&reverse_key_s, "reverse_key"},
        {&subdir_s, "subdir"},
        {&sync_s, "sync"},
        {&txn_s, "txn"},
        {&value_s, "value"},
        {&values_s, "values"},
        {&write_s, "write"},
        {NULL, NULL}
    };
    for(i = 0; strs[i].obj; i++) {
        *strs[i].obj = PyString_InternFromString(strs[i].s);
        if(! *strs[i].obj) {
            return;
        }
    }

    Error = PyErr_NewException("lmdb.Error", NULL, NULL);
    if(! Error) {
        return;
    }
    if(PyObject_SetAttrString(mod, "Error", Error)) {
        return;
    }
    if(PyObject_SetAttrString(mod, "open", (PyObject *)&PyEnvironment_Type)) {
        return;
    }
}
