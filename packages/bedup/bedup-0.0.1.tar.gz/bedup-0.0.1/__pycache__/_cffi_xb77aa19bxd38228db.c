
#include <Python.h>
#include <stddef.h>

#ifdef MS_WIN32
typedef __int8 int8_t;
typedef __int16 int16_t;
typedef __int32 int32_t;
typedef __int64 int64_t;
typedef unsigned __int8 uint8_t;
typedef unsigned __int16 uint16_t;
typedef unsigned __int32 uint32_t;
typedef unsigned __int64 uint64_t;
#endif

#if PY_MAJOR_VERSION < 3
# undef PyCapsule_CheckExact
# undef PyCapsule_GetPointer
# define PyCapsule_CheckExact(capsule) (PyCObject_Check(capsule))
# define PyCapsule_GetPointer(capsule, name) \
    (PyCObject_AsVoidPtr(capsule))
#endif

#if PY_MAJOR_VERSION >= 3
# define PyInt_FromLong PyLong_FromLong
# define PyInt_AsLong PyLong_AsLong
#endif

#define _cffi_from_c_double PyFloat_FromDouble
#define _cffi_from_c_float PyFloat_FromDouble
#define _cffi_from_c_signed_char PyInt_FromLong
#define _cffi_from_c_short PyInt_FromLong
#define _cffi_from_c_int PyInt_FromLong
#define _cffi_from_c_long PyInt_FromLong
#define _cffi_from_c_unsigned_char PyInt_FromLong
#define _cffi_from_c_unsigned_short PyInt_FromLong
#define _cffi_from_c_unsigned_long PyLong_FromUnsignedLong
#define _cffi_from_c_unsigned_long_long PyLong_FromUnsignedLongLong

#if SIZEOF_INT < SIZEOF_LONG
#  define _cffi_from_c_unsigned_int PyInt_FromLong
#else
#  define _cffi_from_c_unsigned_int PyLong_FromUnsignedLong
#endif

#if SIZEOF_LONG < SIZEOF_LONG_LONG
#  define _cffi_from_c_long_long PyLong_FromLongLong
#else
#  define _cffi_from_c_long_long PyInt_FromLong
#endif

#define _cffi_to_c_long PyInt_AsLong
#define _cffi_to_c_double PyFloat_AsDouble
#define _cffi_to_c_float PyFloat_AsDouble

#define _cffi_to_c_char_p                                                \
                 ((char *(*)(PyObject *))_cffi_exports[0])
#define _cffi_to_c_signed_char                                           \
                 ((signed char(*)(PyObject *))_cffi_exports[1])
#define _cffi_to_c_unsigned_char                                         \
                 ((unsigned char(*)(PyObject *))_cffi_exports[2])
#define _cffi_to_c_short                                                 \
                 ((short(*)(PyObject *))_cffi_exports[3])
#define _cffi_to_c_unsigned_short                                        \
                 ((unsigned short(*)(PyObject *))_cffi_exports[4])

#if SIZEOF_INT < SIZEOF_LONG
#  define _cffi_to_c_int                                                 \
                   ((int(*)(PyObject *))_cffi_exports[5])
#  define _cffi_to_c_unsigned_int                                        \
                   ((unsigned int(*)(PyObject *))_cffi_exports[6])
#else
#  define _cffi_to_c_int          _cffi_to_c_long
#  define _cffi_to_c_unsigned_int _cffi_to_c_unsigned_long
#endif

#define _cffi_to_c_unsigned_long                                         \
                 ((unsigned long(*)(PyObject *))_cffi_exports[7])
#define _cffi_to_c_unsigned_long_long                                    \
                 ((unsigned long long(*)(PyObject *))_cffi_exports[8])
#define _cffi_to_c_char                                                  \
                 ((char(*)(PyObject *))_cffi_exports[9])
#define _cffi_from_c_pointer                                             \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[10])
#define _cffi_to_c_pointer                                               \
    ((char *(*)(PyObject *, CTypeDescrObject *))_cffi_exports[11])
#define _cffi_get_struct_layout                                          \
    ((PyObject *(*)(Py_ssize_t[]))_cffi_exports[12])
#define _cffi_restore_errno                                              \
    ((void(*)(void))_cffi_exports[13])
#define _cffi_save_errno                                                 \
    ((void(*)(void))_cffi_exports[14])
#define _cffi_from_c_char                                                \
    ((PyObject *(*)(char))_cffi_exports[15])
#define _cffi_from_c_deref                                               \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[16])
#define _cffi_to_c                                                       \
    ((int(*)(char *, CTypeDescrObject *, PyObject *))_cffi_exports[17])
#define _cffi_from_c_struct                                              \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[18])
#define _cffi_to_c_wchar_t                                               \
    ((wchar_t(*)(PyObject *))_cffi_exports[19])
#define _cffi_from_c_wchar_t                                             \
    ((PyObject *(*)(wchar_t))_cffi_exports[20])
#define _cffi_to_c_long_double                                           \
    ((long double(*)(PyObject *))_cffi_exports[21])
#define _CFFI_NUM_EXPORTS 22

#if SIZEOF_LONG < SIZEOF_LONG_LONG
#  define _cffi_to_c_long_long PyLong_AsLongLong
#else
#  define _cffi_to_c_long_long _cffi_to_c_long
#endif

typedef struct _ctypedescr CTypeDescrObject;

static void *_cffi_exports[_CFFI_NUM_EXPORTS];
static PyObject *_cffi_types, *_cffi_VerificationError;

static PyObject *_cffi_setup_custom(PyObject *lib);   /* forward */

static PyObject *_cffi_setup(PyObject *self, PyObject *args)
{
    PyObject *library;
    if (!PyArg_ParseTuple(args, "OOO", &_cffi_types, &_cffi_VerificationError,
                                       &library))
        return NULL;
    Py_INCREF(_cffi_types);
    Py_INCREF(_cffi_VerificationError);
    return _cffi_setup_custom(library);
}

static void _cffi_init(void)
{
    PyObject *module = PyImport_ImportModule("_cffi_backend");
    PyObject *c_api_object;

    if (module == NULL)
        return;

    c_api_object = PyObject_GetAttrString(module, "_C_API");
    if (c_api_object == NULL)
        return;
    if (!PyCapsule_CheckExact(c_api_object)) {
        PyErr_SetNone(PyExc_ImportError);
        return;
    }
    memcpy(_cffi_exports, PyCapsule_GetPointer(c_api_object, "cffi"),
           _CFFI_NUM_EXPORTS * sizeof(void *));
}

#define _cffi_type(num) ((CTypeDescrObject *)PyList_GET_ITEM(_cffi_types, num))

/**********/



#include <linux/fs.h>
#include <linux/fiemap.h>


static int _cffi_const_FIEMAP_EXTENT_DATA_INLINE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_EXTENT_DATA_INLINE) && (FIEMAP_EXTENT_DATA_INLINE) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_EXTENT_DATA_INLINE));
  else if ((FIEMAP_EXTENT_DATA_INLINE) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_EXTENT_DATA_INLINE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_EXTENT_DATA_INLINE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_EXTENT_DATA_INLINE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_FIEMAP_FLAG_SYNC(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_FLAG_SYNC) && (FIEMAP_FLAG_SYNC) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_FLAG_SYNC));
  else if ((FIEMAP_FLAG_SYNC) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_FLAG_SYNC));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_FLAG_SYNC));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_FLAG_SYNC", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_EXTENT_DATA_INLINE(lib);
}

static int _cffi_const_FIEMAP_FLAGS_COMPAT(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_FLAGS_COMPAT) && (FIEMAP_FLAGS_COMPAT) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_FLAGS_COMPAT));
  else if ((FIEMAP_FLAGS_COMPAT) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_FLAGS_COMPAT));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_FLAGS_COMPAT));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_FLAGS_COMPAT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_FLAG_SYNC(lib);
}

static int _cffi_const_FIEMAP_EXTENT_LAST(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_EXTENT_LAST) && (FIEMAP_EXTENT_LAST) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_EXTENT_LAST));
  else if ((FIEMAP_EXTENT_LAST) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_EXTENT_LAST));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_EXTENT_LAST));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_EXTENT_LAST", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_FLAGS_COMPAT(lib);
}

static int _cffi_const_FS_IOC_FIEMAP(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_IOC_FIEMAP) && (FS_IOC_FIEMAP) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_IOC_FIEMAP));
  else if ((FS_IOC_FIEMAP) <= 0)
    o = PyLong_FromLongLong((long long)(FS_IOC_FIEMAP));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_IOC_FIEMAP));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_IOC_FIEMAP", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_EXTENT_LAST(lib);
}

static int _cffi_const_FIEMAP_EXTENT_UNWRITTEN(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_EXTENT_UNWRITTEN) && (FIEMAP_EXTENT_UNWRITTEN) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_EXTENT_UNWRITTEN));
  else if ((FIEMAP_EXTENT_UNWRITTEN) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_EXTENT_UNWRITTEN));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_EXTENT_UNWRITTEN));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_EXTENT_UNWRITTEN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_IOC_FIEMAP(lib);
}

static int _cffi_const_FIEMAP_EXTENT_SHARED(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_EXTENT_SHARED) && (FIEMAP_EXTENT_SHARED) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_EXTENT_SHARED));
  else if ((FIEMAP_EXTENT_SHARED) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_EXTENT_SHARED));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_EXTENT_SHARED));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_EXTENT_SHARED", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_EXTENT_UNWRITTEN(lib);
}

static int _cffi_const_FIEMAP_MAX_OFFSET(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_MAX_OFFSET) && (FIEMAP_MAX_OFFSET) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_MAX_OFFSET));
  else if ((FIEMAP_MAX_OFFSET) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_MAX_OFFSET));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_MAX_OFFSET));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_MAX_OFFSET", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_EXTENT_SHARED(lib);
}

static int _cffi_const_FIEMAP_EXTENT_MERGED(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_EXTENT_MERGED) && (FIEMAP_EXTENT_MERGED) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_EXTENT_MERGED));
  else if ((FIEMAP_EXTENT_MERGED) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_EXTENT_MERGED));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_EXTENT_MERGED));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_EXTENT_MERGED", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_MAX_OFFSET(lib);
}

static int _cffi_const_FIEMAP_EXTENT_ENCODED(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_EXTENT_ENCODED) && (FIEMAP_EXTENT_ENCODED) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_EXTENT_ENCODED));
  else if ((FIEMAP_EXTENT_ENCODED) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_EXTENT_ENCODED));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_EXTENT_ENCODED));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_EXTENT_ENCODED", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_EXTENT_MERGED(lib);
}

static void _cffi_check_struct_fiemap_extent(struct fiemap_extent *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->fe_logical) << 1);
  (void)((p->fe_physical) << 1);
  (void)((p->fe_length) << 1);
  (void)((p->fe_flags) << 1);
}
static PyObject *
_cffi_layout_struct_fiemap_extent(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct fiemap_extent y; };
  static Py_ssize_t nums[] = {
    sizeof(struct fiemap_extent),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct fiemap_extent, fe_logical),
    sizeof(((struct fiemap_extent *)0)->fe_logical),
    offsetof(struct fiemap_extent, fe_physical),
    sizeof(((struct fiemap_extent *)0)->fe_physical),
    offsetof(struct fiemap_extent, fe_length),
    sizeof(((struct fiemap_extent *)0)->fe_length),
    offsetof(struct fiemap_extent, fe_flags),
    sizeof(((struct fiemap_extent *)0)->fe_flags),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_fiemap_extent(0);
}

static int _cffi_const_FIEMAP_EXTENT_DATA_ENCRYPTED(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_EXTENT_DATA_ENCRYPTED) && (FIEMAP_EXTENT_DATA_ENCRYPTED) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_EXTENT_DATA_ENCRYPTED));
  else if ((FIEMAP_EXTENT_DATA_ENCRYPTED) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_EXTENT_DATA_ENCRYPTED));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_EXTENT_DATA_ENCRYPTED));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_EXTENT_DATA_ENCRYPTED", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_EXTENT_ENCODED(lib);
}

static int _cffi_const_FIEMAP_EXTENT_DATA_TAIL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_EXTENT_DATA_TAIL) && (FIEMAP_EXTENT_DATA_TAIL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_EXTENT_DATA_TAIL));
  else if ((FIEMAP_EXTENT_DATA_TAIL) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_EXTENT_DATA_TAIL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_EXTENT_DATA_TAIL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_EXTENT_DATA_TAIL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_EXTENT_DATA_ENCRYPTED(lib);
}

static int _cffi_const_FIEMAP_EXTENT_DELALLOC(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_EXTENT_DELALLOC) && (FIEMAP_EXTENT_DELALLOC) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_EXTENT_DELALLOC));
  else if ((FIEMAP_EXTENT_DELALLOC) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_EXTENT_DELALLOC));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_EXTENT_DELALLOC));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_EXTENT_DELALLOC", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_EXTENT_DATA_TAIL(lib);
}

static void _cffi_check_struct_fiemap(struct fiemap *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->fm_start) << 1);
  (void)((p->fm_length) << 1);
  (void)((p->fm_flags) << 1);
  (void)((p->fm_mapped_extents) << 1);
  (void)((p->fm_extent_count) << 1);
  { struct fiemap_extent(*tmp)[0] = &p->fm_extents; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_fiemap(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct fiemap y; };
  static Py_ssize_t nums[] = {
    sizeof(struct fiemap),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct fiemap, fm_start),
    sizeof(((struct fiemap *)0)->fm_start),
    offsetof(struct fiemap, fm_length),
    sizeof(((struct fiemap *)0)->fm_length),
    offsetof(struct fiemap, fm_flags),
    sizeof(((struct fiemap *)0)->fm_flags),
    offsetof(struct fiemap, fm_mapped_extents),
    sizeof(((struct fiemap *)0)->fm_mapped_extents),
    offsetof(struct fiemap, fm_extent_count),
    sizeof(((struct fiemap *)0)->fm_extent_count),
    offsetof(struct fiemap, fm_extents),
    sizeof(((struct fiemap *)0)->fm_extents),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_fiemap(0);
}

static int _cffi_const_FIEMAP_EXTENT_UNKNOWN(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_EXTENT_UNKNOWN) && (FIEMAP_EXTENT_UNKNOWN) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_EXTENT_UNKNOWN));
  else if ((FIEMAP_EXTENT_UNKNOWN) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_EXTENT_UNKNOWN));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_EXTENT_UNKNOWN));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_EXTENT_UNKNOWN", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_EXTENT_DELALLOC(lib);
}

static int _cffi_const_FIEMAP_EXTENT_NOT_ALIGNED(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_EXTENT_NOT_ALIGNED) && (FIEMAP_EXTENT_NOT_ALIGNED) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_EXTENT_NOT_ALIGNED));
  else if ((FIEMAP_EXTENT_NOT_ALIGNED) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_EXTENT_NOT_ALIGNED));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_EXTENT_NOT_ALIGNED));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_EXTENT_NOT_ALIGNED", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_EXTENT_UNKNOWN(lib);
}

static int _cffi_const_FIEMAP_FLAG_XATTR(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FIEMAP_FLAG_XATTR) && (FIEMAP_FLAG_XATTR) <= LONG_MAX)
    o = PyInt_FromLong((long)(FIEMAP_FLAG_XATTR));
  else if ((FIEMAP_FLAG_XATTR) <= 0)
    o = PyLong_FromLongLong((long long)(FIEMAP_FLAG_XATTR));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FIEMAP_FLAG_XATTR));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FIEMAP_FLAG_XATTR", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FIEMAP_EXTENT_NOT_ALIGNED(lib);
}

static PyObject *_cffi_setup_custom(PyObject *lib)
{
  if (_cffi_const_FIEMAP_FLAG_XATTR(lib) < 0)
    return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef _cffi_methods[] = {
  {"_cffi_layout_struct_fiemap_extent", _cffi_layout_struct_fiemap_extent, METH_NOARGS},
  {"_cffi_layout_struct_fiemap", _cffi_layout_struct_fiemap, METH_NOARGS},
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

PyMODINIT_FUNC
init_cffi_xb77aa19bxd38228db(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi_xb77aa19bxd38228db", _cffi_methods);
  if (lib == NULL || 0 < 0)
    return;
  _cffi_init();
  return;
}
