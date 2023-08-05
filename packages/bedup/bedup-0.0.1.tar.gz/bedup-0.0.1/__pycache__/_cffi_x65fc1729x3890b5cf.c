
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
    

static int _cffi_const_FS_COMPR_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_COMPR_FL) && (FS_COMPR_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_COMPR_FL));
  else if ((FS_COMPR_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_COMPR_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_COMPR_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_COMPR_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_FS_SECRM_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_SECRM_FL) && (FS_SECRM_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_SECRM_FL));
  else if ((FS_SECRM_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_SECRM_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_SECRM_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_SECRM_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_COMPR_FL(lib);
}

static int _cffi_const_FS_COMPRBLK_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_COMPRBLK_FL) && (FS_COMPRBLK_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_COMPRBLK_FL));
  else if ((FS_COMPRBLK_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_COMPRBLK_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_COMPRBLK_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_COMPRBLK_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_SECRM_FL(lib);
}

static int _cffi_const_FS_IOC_GETFLAGS(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_IOC_GETFLAGS) && (FS_IOC_GETFLAGS) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_IOC_GETFLAGS));
  else if ((FS_IOC_GETFLAGS) <= 0)
    o = PyLong_FromLongLong((long long)(FS_IOC_GETFLAGS));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_IOC_GETFLAGS));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_IOC_GETFLAGS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_COMPRBLK_FL(lib);
}

static int _cffi_const_FS_NOCOW_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_NOCOW_FL) && (FS_NOCOW_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_NOCOW_FL));
  else if ((FS_NOCOW_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_NOCOW_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_NOCOW_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_NOCOW_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_IOC_GETFLAGS(lib);
}

static int _cffi_const_FS_NOCOMP_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_NOCOMP_FL) && (FS_NOCOMP_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_NOCOMP_FL));
  else if ((FS_NOCOMP_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_NOCOMP_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_NOCOMP_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_NOCOMP_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_NOCOW_FL(lib);
}

static int _cffi_const_FS_JOURNAL_DATA_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_JOURNAL_DATA_FL) && (FS_JOURNAL_DATA_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_JOURNAL_DATA_FL));
  else if ((FS_JOURNAL_DATA_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_JOURNAL_DATA_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_JOURNAL_DATA_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_JOURNAL_DATA_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_NOCOMP_FL(lib);
}

static int _cffi_const_FS_FL_USER_MODIFIABLE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_FL_USER_MODIFIABLE) && (FS_FL_USER_MODIFIABLE) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_FL_USER_MODIFIABLE));
  else if ((FS_FL_USER_MODIFIABLE) <= 0)
    o = PyLong_FromLongLong((long long)(FS_FL_USER_MODIFIABLE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_FL_USER_MODIFIABLE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_FL_USER_MODIFIABLE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_JOURNAL_DATA_FL(lib);
}

static int _cffi_const_FS_DIRSYNC_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_DIRSYNC_FL) && (FS_DIRSYNC_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_DIRSYNC_FL));
  else if ((FS_DIRSYNC_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_DIRSYNC_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_DIRSYNC_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_DIRSYNC_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_FL_USER_MODIFIABLE(lib);
}

static int _cffi_const_FS_INDEX_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_INDEX_FL) && (FS_INDEX_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_INDEX_FL));
  else if ((FS_INDEX_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_INDEX_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_INDEX_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_INDEX_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_DIRSYNC_FL(lib);
}

static int _cffi_const_FS_IMAGIC_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_IMAGIC_FL) && (FS_IMAGIC_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_IMAGIC_FL));
  else if ((FS_IMAGIC_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_IMAGIC_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_IMAGIC_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_IMAGIC_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_INDEX_FL(lib);
}

static int _cffi_const_FS_NODUMP_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_NODUMP_FL) && (FS_NODUMP_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_NODUMP_FL));
  else if ((FS_NODUMP_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_NODUMP_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_NODUMP_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_NODUMP_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_IMAGIC_FL(lib);
}

static int _cffi_const_FS_IMMUTABLE_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_IMMUTABLE_FL) && (FS_IMMUTABLE_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_IMMUTABLE_FL));
  else if ((FS_IMMUTABLE_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_IMMUTABLE_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_IMMUTABLE_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_IMMUTABLE_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_NODUMP_FL(lib);
}

static int _cffi_const_FS_TOPDIR_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_TOPDIR_FL) && (FS_TOPDIR_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_TOPDIR_FL));
  else if ((FS_TOPDIR_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_TOPDIR_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_TOPDIR_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_TOPDIR_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_IMMUTABLE_FL(lib);
}

static int _cffi_const_FS_NOTAIL_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_NOTAIL_FL) && (FS_NOTAIL_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_NOTAIL_FL));
  else if ((FS_NOTAIL_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_NOTAIL_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_NOTAIL_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_NOTAIL_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_TOPDIR_FL(lib);
}

static int _cffi_const_FS_UNRM_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_UNRM_FL) && (FS_UNRM_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_UNRM_FL));
  else if ((FS_UNRM_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_UNRM_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_UNRM_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_UNRM_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_NOTAIL_FL(lib);
}

static int _cffi_const_FS_APPEND_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_APPEND_FL) && (FS_APPEND_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_APPEND_FL));
  else if ((FS_APPEND_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_APPEND_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_APPEND_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_APPEND_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_UNRM_FL(lib);
}

static int _cffi_const_FS_DIRTY_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_DIRTY_FL) && (FS_DIRTY_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_DIRTY_FL));
  else if ((FS_DIRTY_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_DIRTY_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_DIRTY_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_DIRTY_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_APPEND_FL(lib);
}

static int _cffi_const_FS_DIRECTIO_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_DIRECTIO_FL) && (FS_DIRECTIO_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_DIRECTIO_FL));
  else if ((FS_DIRECTIO_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_DIRECTIO_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_DIRECTIO_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_DIRECTIO_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_DIRTY_FL(lib);
}

static int _cffi_const_FS_ECOMPR_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_ECOMPR_FL) && (FS_ECOMPR_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_ECOMPR_FL));
  else if ((FS_ECOMPR_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_ECOMPR_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_ECOMPR_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_ECOMPR_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_DIRECTIO_FL(lib);
}

static int _cffi_const_FS_BTREE_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_BTREE_FL) && (FS_BTREE_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_BTREE_FL));
  else if ((FS_BTREE_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_BTREE_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_BTREE_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_BTREE_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_ECOMPR_FL(lib);
}

static int _cffi_const_FS_RESERVED_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_RESERVED_FL) && (FS_RESERVED_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_RESERVED_FL));
  else if ((FS_RESERVED_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_RESERVED_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_RESERVED_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_RESERVED_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_BTREE_FL(lib);
}

static int _cffi_const_FS_EXTENT_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_EXTENT_FL) && (FS_EXTENT_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_EXTENT_FL));
  else if ((FS_EXTENT_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_EXTENT_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_EXTENT_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_EXTENT_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_RESERVED_FL(lib);
}

static int _cffi_const_FS_NOATIME_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_NOATIME_FL) && (FS_NOATIME_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_NOATIME_FL));
  else if ((FS_NOATIME_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_NOATIME_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_NOATIME_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_NOATIME_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_EXTENT_FL(lib);
}

static int _cffi_const_FS_IOC_SETFLAGS(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_IOC_SETFLAGS) && (FS_IOC_SETFLAGS) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_IOC_SETFLAGS));
  else if ((FS_IOC_SETFLAGS) <= 0)
    o = PyLong_FromLongLong((long long)(FS_IOC_SETFLAGS));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_IOC_SETFLAGS));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_IOC_SETFLAGS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_NOATIME_FL(lib);
}

static int _cffi_const_FS_FL_USER_VISIBLE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_FL_USER_VISIBLE) && (FS_FL_USER_VISIBLE) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_FL_USER_VISIBLE));
  else if ((FS_FL_USER_VISIBLE) <= 0)
    o = PyLong_FromLongLong((long long)(FS_FL_USER_VISIBLE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_FL_USER_VISIBLE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_FL_USER_VISIBLE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_IOC_SETFLAGS(lib);
}

static int _cffi_const_FS_SYNC_FL(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (FS_SYNC_FL) && (FS_SYNC_FL) <= LONG_MAX)
    o = PyInt_FromLong((long)(FS_SYNC_FL));
  else if ((FS_SYNC_FL) <= 0)
    o = PyLong_FromLongLong((long long)(FS_SYNC_FL));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(FS_SYNC_FL));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "FS_SYNC_FL", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_FS_FL_USER_VISIBLE(lib);
}

static PyObject *_cffi_setup_custom(PyObject *lib)
{
  if (_cffi_const_FS_SYNC_FL(lib) < 0)
    return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef _cffi_methods[] = {
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

PyMODINIT_FUNC
init_cffi_x65fc1729x3890b5cf(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi_x65fc1729x3890b5cf", _cffi_methods);
  if (lib == NULL || 0 < 0)
    return;
  _cffi_init();
  return;
}
