
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



#include <unistd.h>
#include <sys/syscall.h>

#define IOPRIO_CLASS_SHIFT      (13)
#define IOPRIO_PRIO_VALUE(class, data) (((class) << IOPRIO_CLASS_SHIFT) | data)
#define IOPRIO_PRIO_MASK        ((1UL << IOPRIO_CLASS_SHIFT) - 1)
#define IOPRIO_PRIO_CLASS(mask) ((mask) >> IOPRIO_CLASS_SHIFT)
#define IOPRIO_PRIO_DATA(mask)  ((mask) & IOPRIO_PRIO_MASK)
#define IOPRIO_PRIO_VALUE(class, data) (((class) << IOPRIO_CLASS_SHIFT) | data)

enum {
    IOPRIO_CLASS_NONE,
    IOPRIO_CLASS_RT,
    IOPRIO_CLASS_BE,
    IOPRIO_CLASS_IDLE,
};

enum {
    IOPRIO_WHO_PROCESS = 1,
    IOPRIO_WHO_PGRP,
    IOPRIO_WHO_USER,
};

static inline int ioprio_set(int which, int who, int ioprio) {
    return syscall(SYS_ioprio_set, which, who, ioprio);
}

static inline int ioprio_get(int which, int who) {
    return syscall(SYS_ioprio_get, which, who);
}


static int _cffi_const_IOPRIO_WHO_PROCESS(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (IOPRIO_WHO_PROCESS) && (IOPRIO_WHO_PROCESS) <= LONG_MAX)
    o = PyInt_FromLong((long)(IOPRIO_WHO_PROCESS));
  else if ((IOPRIO_WHO_PROCESS) <= 0)
    o = PyLong_FromLongLong((long long)(IOPRIO_WHO_PROCESS));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(IOPRIO_WHO_PROCESS));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IOPRIO_WHO_PROCESS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_IOPRIO_CLASS_BE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (IOPRIO_CLASS_BE) && (IOPRIO_CLASS_BE) <= LONG_MAX)
    o = PyInt_FromLong((long)(IOPRIO_CLASS_BE));
  else if ((IOPRIO_CLASS_BE) <= 0)
    o = PyLong_FromLongLong((long long)(IOPRIO_CLASS_BE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(IOPRIO_CLASS_BE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IOPRIO_CLASS_BE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IOPRIO_WHO_PROCESS(lib);
}

static int _cffi_const_IOPRIO_CLASS_IDLE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (IOPRIO_CLASS_IDLE) && (IOPRIO_CLASS_IDLE) <= LONG_MAX)
    o = PyInt_FromLong((long)(IOPRIO_CLASS_IDLE));
  else if ((IOPRIO_CLASS_IDLE) <= 0)
    o = PyLong_FromLongLong((long long)(IOPRIO_CLASS_IDLE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(IOPRIO_CLASS_IDLE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IOPRIO_CLASS_IDLE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IOPRIO_CLASS_BE(lib);
}

static int _cffi_const_IOPRIO_CLASS_RT(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (IOPRIO_CLASS_RT) && (IOPRIO_CLASS_RT) <= LONG_MAX)
    o = PyInt_FromLong((long)(IOPRIO_CLASS_RT));
  else if ((IOPRIO_CLASS_RT) <= 0)
    o = PyLong_FromLongLong((long long)(IOPRIO_CLASS_RT));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(IOPRIO_CLASS_RT));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IOPRIO_CLASS_RT", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IOPRIO_CLASS_IDLE(lib);
}

static PyObject *
_cffi_f_IOPRIO_PRIO_VALUE(PyObject *self, PyObject *args)
{
  int x0;
  int x1;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:IOPRIO_PRIO_VALUE", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_int(arg0);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_int(arg1);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = IOPRIO_PRIO_VALUE(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result);
}

static PyObject *
_cffi_f_ioprio_get(PyObject *self, PyObject *args)
{
  int x0;
  int x1;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:ioprio_get", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_int(arg0);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_int(arg1);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ioprio_get(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result);
}

static int _cffi_const_IOPRIO_WHO_USER(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (IOPRIO_WHO_USER) && (IOPRIO_WHO_USER) <= LONG_MAX)
    o = PyInt_FromLong((long)(IOPRIO_WHO_USER));
  else if ((IOPRIO_WHO_USER) <= 0)
    o = PyLong_FromLongLong((long long)(IOPRIO_WHO_USER));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(IOPRIO_WHO_USER));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IOPRIO_WHO_USER", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IOPRIO_CLASS_RT(lib);
}

static int _cffi_const_IOPRIO_WHO_PGRP(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (IOPRIO_WHO_PGRP) && (IOPRIO_WHO_PGRP) <= LONG_MAX)
    o = PyInt_FromLong((long)(IOPRIO_WHO_PGRP));
  else if ((IOPRIO_WHO_PGRP) <= 0)
    o = PyLong_FromLongLong((long long)(IOPRIO_WHO_PGRP));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(IOPRIO_WHO_PGRP));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IOPRIO_WHO_PGRP", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IOPRIO_WHO_USER(lib);
}

static PyObject *
_cffi_f_IOPRIO_PRIO_CLASS(PyObject *self, PyObject *arg0)
{
  int x0;
  int result;

  x0 = _cffi_to_c_int(arg0);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = IOPRIO_PRIO_CLASS(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result);
}

static PyObject *
_cffi_f_ioprio_set(PyObject *self, PyObject *args)
{
  int x0;
  int x1;
  int x2;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:ioprio_set", &arg0, &arg1, &arg2))
    return NULL;

  x0 = _cffi_to_c_int(arg0);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_int(arg1);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  x2 = _cffi_to_c_int(arg2);
  if (x2 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = ioprio_set(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result);
}

static int _cffi_const_IOPRIO_CLASS_NONE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (IOPRIO_CLASS_NONE) && (IOPRIO_CLASS_NONE) <= LONG_MAX)
    o = PyInt_FromLong((long)(IOPRIO_CLASS_NONE));
  else if ((IOPRIO_CLASS_NONE) <= 0)
    o = PyLong_FromLongLong((long long)(IOPRIO_CLASS_NONE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(IOPRIO_CLASS_NONE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "IOPRIO_CLASS_NONE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_IOPRIO_WHO_PGRP(lib);
}

static PyObject *
_cffi_f_IOPRIO_PRIO_DATA(PyObject *self, PyObject *arg0)
{
  int x0;
  int result;

  x0 = _cffi_to_c_int(arg0);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = IOPRIO_PRIO_DATA(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result);
}

static PyObject *_cffi_setup_custom(PyObject *lib)
{
  if (_cffi_const_IOPRIO_CLASS_NONE(lib) < 0)
    return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef _cffi_methods[] = {
  {"IOPRIO_PRIO_VALUE", _cffi_f_IOPRIO_PRIO_VALUE, METH_VARARGS},
  {"ioprio_get", _cffi_f_ioprio_get, METH_VARARGS},
  {"IOPRIO_PRIO_CLASS", _cffi_f_IOPRIO_PRIO_CLASS, METH_O},
  {"ioprio_set", _cffi_f_ioprio_set, METH_VARARGS},
  {"IOPRIO_PRIO_DATA", _cffi_f_IOPRIO_PRIO_DATA, METH_O},
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

PyMODINIT_FUNC
init_cffi_xa16b0d47xe9cd013f(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi_xa16b0d47xe9cd013f", _cffi_methods);
  if (lib == NULL || 0 < 0)
    return;
  _cffi_init();
  return;
}
