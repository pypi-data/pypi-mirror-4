
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



    #include <btrfs-progs/ioctl.h>
    #include <btrfs-progs/ctree.h>
    

static void _cffi_check_struct_btrfs_timespec(struct btrfs_timespec *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->sec) << 1);
  (void)((p->nsec) << 1);
}
static PyObject *
_cffi_layout_struct_btrfs_timespec(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_timespec y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_timespec),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_timespec, sec),
    sizeof(((struct btrfs_timespec *)0)->sec),
    offsetof(struct btrfs_timespec, nsec),
    sizeof(((struct btrfs_timespec *)0)->nsec),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_timespec(0);
}

static int _cffi_const_BTRFS_IOC_INO_LOOKUP(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_IOC_INO_LOOKUP) && (BTRFS_IOC_INO_LOOKUP) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_IOC_INO_LOOKUP));
  else if ((BTRFS_IOC_INO_LOOKUP) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_IOC_INO_LOOKUP));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_IOC_INO_LOOKUP));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_IOC_INO_LOOKUP", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_BTRFS_EXTENT_DATA_KEY(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_EXTENT_DATA_KEY) && (BTRFS_EXTENT_DATA_KEY) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_EXTENT_DATA_KEY));
  else if ((BTRFS_EXTENT_DATA_KEY) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_EXTENT_DATA_KEY));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_EXTENT_DATA_KEY));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_EXTENT_DATA_KEY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_IOC_INO_LOOKUP(lib);
}

static void _cffi_check_struct_btrfs_ioctl_ino_path_args(struct btrfs_ioctl_ino_path_args *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->inum) << 1);
  (void)((p->size) << 1);
  (void)((p->fspath) << 1);
}
static PyObject *
_cffi_layout_struct_btrfs_ioctl_ino_path_args(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_ioctl_ino_path_args y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_ioctl_ino_path_args),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_ioctl_ino_path_args, inum),
    sizeof(((struct btrfs_ioctl_ino_path_args *)0)->inum),
    offsetof(struct btrfs_ioctl_ino_path_args, size),
    sizeof(((struct btrfs_ioctl_ino_path_args *)0)->size),
    offsetof(struct btrfs_ioctl_ino_path_args, fspath),
    sizeof(((struct btrfs_ioctl_ino_path_args *)0)->fspath),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_ioctl_ino_path_args(0);
}

static int _cffi_const_BTRFS_DIR_INDEX_KEY(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_DIR_INDEX_KEY) && (BTRFS_DIR_INDEX_KEY) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_DIR_INDEX_KEY));
  else if ((BTRFS_DIR_INDEX_KEY) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_DIR_INDEX_KEY));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_DIR_INDEX_KEY));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_DIR_INDEX_KEY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_EXTENT_DATA_KEY(lib);
}

static void _cffi_check_struct_btrfs_ioctl_search_header(struct btrfs_ioctl_search_header *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->transid) << 1);
  (void)((p->objectid) << 1);
  (void)((p->offset) << 1);
  (void)((p->type) << 1);
  (void)((p->len) << 1);
}
static PyObject *
_cffi_layout_struct_btrfs_ioctl_search_header(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_ioctl_search_header y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_ioctl_search_header),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_ioctl_search_header, transid),
    sizeof(((struct btrfs_ioctl_search_header *)0)->transid),
    offsetof(struct btrfs_ioctl_search_header, objectid),
    sizeof(((struct btrfs_ioctl_search_header *)0)->objectid),
    offsetof(struct btrfs_ioctl_search_header, offset),
    sizeof(((struct btrfs_ioctl_search_header *)0)->offset),
    offsetof(struct btrfs_ioctl_search_header, type),
    sizeof(((struct btrfs_ioctl_search_header *)0)->type),
    offsetof(struct btrfs_ioctl_search_header, len),
    sizeof(((struct btrfs_ioctl_search_header *)0)->len),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_ioctl_search_header(0);
}

static void _cffi_check_struct_btrfs_ioctl_fs_info_args(struct btrfs_ioctl_fs_info_args *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->max_id) << 1);
  (void)((p->num_devices) << 1);
  { unsigned char(*tmp)[16] = &p->fsid; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_btrfs_ioctl_fs_info_args(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_ioctl_fs_info_args y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_ioctl_fs_info_args),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_ioctl_fs_info_args, max_id),
    sizeof(((struct btrfs_ioctl_fs_info_args *)0)->max_id),
    offsetof(struct btrfs_ioctl_fs_info_args, num_devices),
    sizeof(((struct btrfs_ioctl_fs_info_args *)0)->num_devices),
    offsetof(struct btrfs_ioctl_fs_info_args, fsid),
    sizeof(((struct btrfs_ioctl_fs_info_args *)0)->fsid),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_ioctl_fs_info_args(0);
}

static void _cffi_check_struct_btrfs_ioctl_search_args(struct btrfs_ioctl_search_args *p)
{
  /* only to generate compile-time warnings or errors */
  { struct btrfs_ioctl_search_key(*tmp) = &p->key; (void)tmp; }
  { char(*tmp)[3992] = &p->buf; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_btrfs_ioctl_search_args(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_ioctl_search_args y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_ioctl_search_args),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_ioctl_search_args, key),
    sizeof(((struct btrfs_ioctl_search_args *)0)->key),
    offsetof(struct btrfs_ioctl_search_args, buf),
    sizeof(((struct btrfs_ioctl_search_args *)0)->buf),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_ioctl_search_args(0);
}

static PyObject *
_cffi_f_btrfs_stack_inode_ref_name_len(PyObject *self, PyObject *arg0)
{
  struct btrfs_inode_ref*  x0;
  unsigned long result;

  x0 = (struct btrfs_inode_ref* )_cffi_to_c_pointer(arg0, _cffi_type(0));
  if (x0 == (struct btrfs_inode_ref* )NULL && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = btrfs_stack_inode_ref_name_len(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_unsigned_long(result);
}

static PyObject *
_cffi_f_btrfs_stack_inode_size(PyObject *self, PyObject *arg0)
{
  struct btrfs_inode_item*  x0;
  unsigned long result;

  x0 = (struct btrfs_inode_item* )_cffi_to_c_pointer(arg0, _cffi_type(1));
  if (x0 == (struct btrfs_inode_item* )NULL && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = btrfs_stack_inode_size(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_unsigned_long(result);
}

static int _cffi_const_BTRFS_FIRST_FREE_OBJECTID(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_FIRST_FREE_OBJECTID) && (BTRFS_FIRST_FREE_OBJECTID) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_FIRST_FREE_OBJECTID));
  else if ((BTRFS_FIRST_FREE_OBJECTID) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_FIRST_FREE_OBJECTID));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_FIRST_FREE_OBJECTID));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_FIRST_FREE_OBJECTID", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_DIR_INDEX_KEY(lib);
}

static int _cffi_const_BTRFS_IOC_TREE_SEARCH(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_IOC_TREE_SEARCH) && (BTRFS_IOC_TREE_SEARCH) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_IOC_TREE_SEARCH));
  else if ((BTRFS_IOC_TREE_SEARCH) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_IOC_TREE_SEARCH));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_IOC_TREE_SEARCH));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_IOC_TREE_SEARCH", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_FIRST_FREE_OBJECTID(lib);
}

static void _cffi_check_struct_btrfs_inode_item(struct btrfs_inode_item *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->generation) << 1);
  (void)((p->transid) << 1);
  (void)((p->size) << 1);
  (void)((p->nbytes) << 1);
  (void)((p->block_group) << 1);
  (void)((p->nlink) << 1);
  (void)((p->uid) << 1);
  (void)((p->gid) << 1);
  (void)((p->mode) << 1);
  (void)((p->rdev) << 1);
  (void)((p->flags) << 1);
  (void)((p->sequence) << 1);
  { struct btrfs_timespec(*tmp) = &p->atime; (void)tmp; }
  { struct btrfs_timespec(*tmp) = &p->ctime; (void)tmp; }
  { struct btrfs_timespec(*tmp) = &p->mtime; (void)tmp; }
  { struct btrfs_timespec(*tmp) = &p->otime; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_btrfs_inode_item(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_inode_item y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_inode_item),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_inode_item, generation),
    sizeof(((struct btrfs_inode_item *)0)->generation),
    offsetof(struct btrfs_inode_item, transid),
    sizeof(((struct btrfs_inode_item *)0)->transid),
    offsetof(struct btrfs_inode_item, size),
    sizeof(((struct btrfs_inode_item *)0)->size),
    offsetof(struct btrfs_inode_item, nbytes),
    sizeof(((struct btrfs_inode_item *)0)->nbytes),
    offsetof(struct btrfs_inode_item, block_group),
    sizeof(((struct btrfs_inode_item *)0)->block_group),
    offsetof(struct btrfs_inode_item, nlink),
    sizeof(((struct btrfs_inode_item *)0)->nlink),
    offsetof(struct btrfs_inode_item, uid),
    sizeof(((struct btrfs_inode_item *)0)->uid),
    offsetof(struct btrfs_inode_item, gid),
    sizeof(((struct btrfs_inode_item *)0)->gid),
    offsetof(struct btrfs_inode_item, mode),
    sizeof(((struct btrfs_inode_item *)0)->mode),
    offsetof(struct btrfs_inode_item, rdev),
    sizeof(((struct btrfs_inode_item *)0)->rdev),
    offsetof(struct btrfs_inode_item, flags),
    sizeof(((struct btrfs_inode_item *)0)->flags),
    offsetof(struct btrfs_inode_item, sequence),
    sizeof(((struct btrfs_inode_item *)0)->sequence),
    offsetof(struct btrfs_inode_item, atime),
    sizeof(((struct btrfs_inode_item *)0)->atime),
    offsetof(struct btrfs_inode_item, ctime),
    sizeof(((struct btrfs_inode_item *)0)->ctime),
    offsetof(struct btrfs_inode_item, mtime),
    sizeof(((struct btrfs_inode_item *)0)->mtime),
    offsetof(struct btrfs_inode_item, otime),
    sizeof(((struct btrfs_inode_item *)0)->otime),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_inode_item(0);
}

static void _cffi_check_struct_btrfs_root_item(struct btrfs_root_item *p)
{
  /* only to generate compile-time warnings or errors */
  { struct btrfs_inode_item(*tmp) = &p->inode; (void)tmp; }
  (void)((p->generation) << 1);
  (void)((p->root_dirid) << 1);
  (void)((p->bytenr) << 1);
  (void)((p->byte_limit) << 1);
  (void)((p->bytes_used) << 1);
  (void)((p->last_snapshot) << 1);
  (void)((p->flags) << 1);
  (void)((p->refs) << 1);
  { struct btrfs_disk_key(*tmp) = &p->drop_progress; (void)tmp; }
  (void)((p->drop_level) << 1);
  (void)((p->level) << 1);
  (void)((p->generation_v2) << 1);
  (void)((p->ctransid) << 1);
  (void)((p->otransid) << 1);
  (void)((p->stransid) << 1);
  (void)((p->rtransid) << 1);
  { struct btrfs_timespec(*tmp) = &p->ctime; (void)tmp; }
  { struct btrfs_timespec(*tmp) = &p->otime; (void)tmp; }
  { struct btrfs_timespec(*tmp) = &p->stime; (void)tmp; }
  { struct btrfs_timespec(*tmp) = &p->rtime; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_btrfs_root_item(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_root_item y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_root_item),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_root_item, inode),
    sizeof(((struct btrfs_root_item *)0)->inode),
    offsetof(struct btrfs_root_item, generation),
    sizeof(((struct btrfs_root_item *)0)->generation),
    offsetof(struct btrfs_root_item, root_dirid),
    sizeof(((struct btrfs_root_item *)0)->root_dirid),
    offsetof(struct btrfs_root_item, bytenr),
    sizeof(((struct btrfs_root_item *)0)->bytenr),
    offsetof(struct btrfs_root_item, byte_limit),
    sizeof(((struct btrfs_root_item *)0)->byte_limit),
    offsetof(struct btrfs_root_item, bytes_used),
    sizeof(((struct btrfs_root_item *)0)->bytes_used),
    offsetof(struct btrfs_root_item, last_snapshot),
    sizeof(((struct btrfs_root_item *)0)->last_snapshot),
    offsetof(struct btrfs_root_item, flags),
    sizeof(((struct btrfs_root_item *)0)->flags),
    offsetof(struct btrfs_root_item, refs),
    sizeof(((struct btrfs_root_item *)0)->refs),
    offsetof(struct btrfs_root_item, drop_progress),
    sizeof(((struct btrfs_root_item *)0)->drop_progress),
    offsetof(struct btrfs_root_item, drop_level),
    sizeof(((struct btrfs_root_item *)0)->drop_level),
    offsetof(struct btrfs_root_item, level),
    sizeof(((struct btrfs_root_item *)0)->level),
    offsetof(struct btrfs_root_item, generation_v2),
    sizeof(((struct btrfs_root_item *)0)->generation_v2),
    offsetof(struct btrfs_root_item, ctransid),
    sizeof(((struct btrfs_root_item *)0)->ctransid),
    offsetof(struct btrfs_root_item, otransid),
    sizeof(((struct btrfs_root_item *)0)->otransid),
    offsetof(struct btrfs_root_item, stransid),
    sizeof(((struct btrfs_root_item *)0)->stransid),
    offsetof(struct btrfs_root_item, rtransid),
    sizeof(((struct btrfs_root_item *)0)->rtransid),
    offsetof(struct btrfs_root_item, ctime),
    sizeof(((struct btrfs_root_item *)0)->ctime),
    offsetof(struct btrfs_root_item, otime),
    sizeof(((struct btrfs_root_item *)0)->otime),
    offsetof(struct btrfs_root_item, stime),
    sizeof(((struct btrfs_root_item *)0)->stime),
    offsetof(struct btrfs_root_item, rtime),
    sizeof(((struct btrfs_root_item *)0)->rtime),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_root_item(0);
}

static void _cffi_check_struct_btrfs_ioctl_ino_lookup_args(struct btrfs_ioctl_ino_lookup_args *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->treeid) << 1);
  (void)((p->objectid) << 1);
}
static PyObject *
_cffi_layout_struct_btrfs_ioctl_ino_lookup_args(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_ioctl_ino_lookup_args y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_ioctl_ino_lookup_args),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_ioctl_ino_lookup_args, treeid),
    sizeof(((struct btrfs_ioctl_ino_lookup_args *)0)->treeid),
    offsetof(struct btrfs_ioctl_ino_lookup_args, objectid),
    sizeof(((struct btrfs_ioctl_ino_lookup_args *)0)->objectid),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_ioctl_ino_lookup_args(0);
}

static void _cffi_check_struct_btrfs_file_extent_item(struct btrfs_file_extent_item *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->generation) << 1);
  (void)((p->ram_bytes) << 1);
  (void)((p->compression) << 1);
  (void)((p->encryption) << 1);
  (void)((p->other_encoding) << 1);
  (void)((p->type) << 1);
  (void)((p->disk_bytenr) << 1);
  (void)((p->disk_num_bytes) << 1);
  (void)((p->offset) << 1);
  (void)((p->num_bytes) << 1);
}
static PyObject *
_cffi_layout_struct_btrfs_file_extent_item(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_file_extent_item y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_file_extent_item),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_file_extent_item, generation),
    sizeof(((struct btrfs_file_extent_item *)0)->generation),
    offsetof(struct btrfs_file_extent_item, ram_bytes),
    sizeof(((struct btrfs_file_extent_item *)0)->ram_bytes),
    offsetof(struct btrfs_file_extent_item, compression),
    sizeof(((struct btrfs_file_extent_item *)0)->compression),
    offsetof(struct btrfs_file_extent_item, encryption),
    sizeof(((struct btrfs_file_extent_item *)0)->encryption),
    offsetof(struct btrfs_file_extent_item, other_encoding),
    sizeof(((struct btrfs_file_extent_item *)0)->other_encoding),
    offsetof(struct btrfs_file_extent_item, type),
    sizeof(((struct btrfs_file_extent_item *)0)->type),
    offsetof(struct btrfs_file_extent_item, disk_bytenr),
    sizeof(((struct btrfs_file_extent_item *)0)->disk_bytenr),
    offsetof(struct btrfs_file_extent_item, disk_num_bytes),
    sizeof(((struct btrfs_file_extent_item *)0)->disk_num_bytes),
    offsetof(struct btrfs_file_extent_item, offset),
    sizeof(((struct btrfs_file_extent_item *)0)->offset),
    offsetof(struct btrfs_file_extent_item, num_bytes),
    sizeof(((struct btrfs_file_extent_item *)0)->num_bytes),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_file_extent_item(0);
}

static int _cffi_const_BTRFS_ROOT_TREE_OBJECTID(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_ROOT_TREE_OBJECTID) && (BTRFS_ROOT_TREE_OBJECTID) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_ROOT_TREE_OBJECTID));
  else if ((BTRFS_ROOT_TREE_OBJECTID) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_ROOT_TREE_OBJECTID));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_ROOT_TREE_OBJECTID));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_ROOT_TREE_OBJECTID", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_IOC_TREE_SEARCH(lib);
}

static int _cffi_const_BTRFS_FSID_SIZE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_FSID_SIZE) && (BTRFS_FSID_SIZE) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_FSID_SIZE));
  else if ((BTRFS_FSID_SIZE) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_FSID_SIZE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_FSID_SIZE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_FSID_SIZE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_ROOT_TREE_OBJECTID(lib);
}

static void _cffi_check_struct_btrfs_inode_ref(struct btrfs_inode_ref *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->index) << 1);
  (void)((p->name_len) << 1);
}
static PyObject *
_cffi_layout_struct_btrfs_inode_ref(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_inode_ref y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_inode_ref),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_inode_ref, index),
    sizeof(((struct btrfs_inode_ref *)0)->index),
    offsetof(struct btrfs_inode_ref, name_len),
    sizeof(((struct btrfs_inode_ref *)0)->name_len),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_inode_ref(0);
}

static void _cffi_check_struct_btrfs_dir_item(struct btrfs_dir_item *p)
{
  /* only to generate compile-time warnings or errors */
  { struct btrfs_disk_key(*tmp) = &p->location; (void)tmp; }
  (void)((p->transid) << 1);
  (void)((p->data_len) << 1);
  (void)((p->name_len) << 1);
  (void)((p->type) << 1);
}
static PyObject *
_cffi_layout_struct_btrfs_dir_item(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_dir_item y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_dir_item),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_dir_item, location),
    sizeof(((struct btrfs_dir_item *)0)->location),
    offsetof(struct btrfs_dir_item, transid),
    sizeof(((struct btrfs_dir_item *)0)->transid),
    offsetof(struct btrfs_dir_item, data_len),
    sizeof(((struct btrfs_dir_item *)0)->data_len),
    offsetof(struct btrfs_dir_item, name_len),
    sizeof(((struct btrfs_dir_item *)0)->name_len),
    offsetof(struct btrfs_dir_item, type),
    sizeof(((struct btrfs_dir_item *)0)->type),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_dir_item(0);
}

static PyObject *
_cffi_f_btrfs_stack_inode_mode(PyObject *self, PyObject *arg0)
{
  struct btrfs_inode_item*  x0;
  unsigned int result;

  x0 = (struct btrfs_inode_item* )_cffi_to_c_pointer(arg0, _cffi_type(1));
  if (x0 == (struct btrfs_inode_item* )NULL && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = btrfs_stack_inode_mode(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_unsigned_int(result);
}

static void _cffi_check_struct_btrfs_data_container(struct btrfs_data_container *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->bytes_left) << 1);
  (void)((p->bytes_missing) << 1);
  (void)((p->elem_cnt) << 1);
  (void)((p->elem_missed) << 1);
  { unsigned long(*tmp)[0] = &p->val; (void)tmp; }
}
static PyObject *
_cffi_layout_struct_btrfs_data_container(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_data_container y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_data_container),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_data_container, bytes_left),
    sizeof(((struct btrfs_data_container *)0)->bytes_left),
    offsetof(struct btrfs_data_container, bytes_missing),
    sizeof(((struct btrfs_data_container *)0)->bytes_missing),
    offsetof(struct btrfs_data_container, elem_cnt),
    sizeof(((struct btrfs_data_container *)0)->elem_cnt),
    offsetof(struct btrfs_data_container, elem_missed),
    sizeof(((struct btrfs_data_container *)0)->elem_missed),
    offsetof(struct btrfs_data_container, val),
    sizeof(((struct btrfs_data_container *)0)->val),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_data_container(0);
}

static PyObject *
_cffi_f_btrfs_root_generation(PyObject *self, PyObject *arg0)
{
  struct btrfs_root_item*  x0;
  unsigned long result;

  x0 = (struct btrfs_root_item* )_cffi_to_c_pointer(arg0, _cffi_type(2));
  if (x0 == (struct btrfs_root_item* )NULL && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = btrfs_root_generation(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_unsigned_long(result);
}

static int _cffi_const_BTRFS_IOC_FS_INFO(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_IOC_FS_INFO) && (BTRFS_IOC_FS_INFO) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_IOC_FS_INFO));
  else if ((BTRFS_IOC_FS_INFO) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_IOC_FS_INFO));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_IOC_FS_INFO));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_IOC_FS_INFO", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_FSID_SIZE(lib);
}

static int _cffi_const_BTRFS_UUID_SIZE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_UUID_SIZE) && (BTRFS_UUID_SIZE) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_UUID_SIZE));
  else if ((BTRFS_UUID_SIZE) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_UUID_SIZE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_UUID_SIZE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_UUID_SIZE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_IOC_FS_INFO(lib);
}

static PyObject *
_cffi_f_btrfs_stack_file_extent_generation(PyObject *self, PyObject *arg0)
{
  struct btrfs_file_extent_item*  x0;
  unsigned long result;

  x0 = (struct btrfs_file_extent_item* )_cffi_to_c_pointer(arg0, _cffi_type(3));
  if (x0 == (struct btrfs_file_extent_item* )NULL && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = btrfs_stack_file_extent_generation(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_unsigned_long(result);
}

static void _cffi_check_struct_btrfs_ioctl_search_key(struct btrfs_ioctl_search_key *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->tree_id) << 1);
  (void)((p->min_objectid) << 1);
  (void)((p->max_objectid) << 1);
  (void)((p->min_offset) << 1);
  (void)((p->max_offset) << 1);
  (void)((p->min_transid) << 1);
  (void)((p->max_transid) << 1);
  (void)((p->min_type) << 1);
  (void)((p->max_type) << 1);
  (void)((p->nr_items) << 1);
}
static PyObject *
_cffi_layout_struct_btrfs_ioctl_search_key(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_ioctl_search_key y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_ioctl_search_key),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_ioctl_search_key, tree_id),
    sizeof(((struct btrfs_ioctl_search_key *)0)->tree_id),
    offsetof(struct btrfs_ioctl_search_key, min_objectid),
    sizeof(((struct btrfs_ioctl_search_key *)0)->min_objectid),
    offsetof(struct btrfs_ioctl_search_key, max_objectid),
    sizeof(((struct btrfs_ioctl_search_key *)0)->max_objectid),
    offsetof(struct btrfs_ioctl_search_key, min_offset),
    sizeof(((struct btrfs_ioctl_search_key *)0)->min_offset),
    offsetof(struct btrfs_ioctl_search_key, max_offset),
    sizeof(((struct btrfs_ioctl_search_key *)0)->max_offset),
    offsetof(struct btrfs_ioctl_search_key, min_transid),
    sizeof(((struct btrfs_ioctl_search_key *)0)->min_transid),
    offsetof(struct btrfs_ioctl_search_key, max_transid),
    sizeof(((struct btrfs_ioctl_search_key *)0)->max_transid),
    offsetof(struct btrfs_ioctl_search_key, min_type),
    sizeof(((struct btrfs_ioctl_search_key *)0)->min_type),
    offsetof(struct btrfs_ioctl_search_key, max_type),
    sizeof(((struct btrfs_ioctl_search_key *)0)->max_type),
    offsetof(struct btrfs_ioctl_search_key, nr_items),
    sizeof(((struct btrfs_ioctl_search_key *)0)->nr_items),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_ioctl_search_key(0);
}

static int _cffi_const_BTRFS_INODE_ITEM_KEY(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_INODE_ITEM_KEY) && (BTRFS_INODE_ITEM_KEY) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_INODE_ITEM_KEY));
  else if ((BTRFS_INODE_ITEM_KEY) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_INODE_ITEM_KEY));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_INODE_ITEM_KEY));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_INODE_ITEM_KEY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_UUID_SIZE(lib);
}

static PyObject *
_cffi_f_btrfs_stack_inode_generation(PyObject *self, PyObject *arg0)
{
  struct btrfs_inode_item*  x0;
  unsigned long result;

  x0 = (struct btrfs_inode_item* )_cffi_to_c_pointer(arg0, _cffi_type(1));
  if (x0 == (struct btrfs_inode_item* )NULL && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = btrfs_stack_inode_generation(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_unsigned_long(result);
}

static int _cffi_const_BTRFS_IOC_DEFRAG(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_IOC_DEFRAG) && (BTRFS_IOC_DEFRAG) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_IOC_DEFRAG));
  else if ((BTRFS_IOC_DEFRAG) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_IOC_DEFRAG));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_IOC_DEFRAG));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_IOC_DEFRAG", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_INODE_ITEM_KEY(lib);
}

static int _cffi_const_BTRFS_IOC_INO_PATHS(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_IOC_INO_PATHS) && (BTRFS_IOC_INO_PATHS) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_IOC_INO_PATHS));
  else if ((BTRFS_IOC_INO_PATHS) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_IOC_INO_PATHS));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_IOC_INO_PATHS));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_IOC_INO_PATHS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_IOC_DEFRAG(lib);
}

static int _cffi_const_BTRFS_IOC_CLONE(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_IOC_CLONE) && (BTRFS_IOC_CLONE) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_IOC_CLONE));
  else if ((BTRFS_IOC_CLONE) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_IOC_CLONE));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_IOC_CLONE));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_IOC_CLONE", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_IOC_INO_PATHS(lib);
}

static int _cffi_const_BTRFS_DIR_ITEM_KEY(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_DIR_ITEM_KEY) && (BTRFS_DIR_ITEM_KEY) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_DIR_ITEM_KEY));
  else if ((BTRFS_DIR_ITEM_KEY) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_DIR_ITEM_KEY));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_DIR_ITEM_KEY));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_DIR_ITEM_KEY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_IOC_CLONE(lib);
}

static int _cffi_const_BTRFS_ROOT_ITEM_KEY(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_ROOT_ITEM_KEY) && (BTRFS_ROOT_ITEM_KEY) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_ROOT_ITEM_KEY));
  else if ((BTRFS_ROOT_ITEM_KEY) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_ROOT_ITEM_KEY));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_ROOT_ITEM_KEY));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_ROOT_ITEM_KEY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_DIR_ITEM_KEY(lib);
}

static void _cffi_check_struct_btrfs_disk_key(struct btrfs_disk_key *p)
{
  /* only to generate compile-time warnings or errors */
  (void)((p->objectid) << 1);
  (void)((p->type) << 1);
  (void)((p->offset) << 1);
}
static PyObject *
_cffi_layout_struct_btrfs_disk_key(PyObject *self, PyObject *noarg)
{
  struct _cffi_aligncheck { char x; struct btrfs_disk_key y; };
  static Py_ssize_t nums[] = {
    sizeof(struct btrfs_disk_key),
    offsetof(struct _cffi_aligncheck, y),
    offsetof(struct btrfs_disk_key, objectid),
    sizeof(((struct btrfs_disk_key *)0)->objectid),
    offsetof(struct btrfs_disk_key, type),
    sizeof(((struct btrfs_disk_key *)0)->type),
    offsetof(struct btrfs_disk_key, offset),
    sizeof(((struct btrfs_disk_key *)0)->offset),
    -1
  };
  return _cffi_get_struct_layout(nums);
  /* the next line is not executed, but compiled */
  _cffi_check_struct_btrfs_disk_key(0);
}

static int _cffi_const_BTRFS_INODE_REF_KEY(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (BTRFS_INODE_REF_KEY) && (BTRFS_INODE_REF_KEY) <= LONG_MAX)
    o = PyInt_FromLong((long)(BTRFS_INODE_REF_KEY));
  else if ((BTRFS_INODE_REF_KEY) <= 0)
    o = PyLong_FromLongLong((long long)(BTRFS_INODE_REF_KEY));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(BTRFS_INODE_REF_KEY));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "BTRFS_INODE_REF_KEY", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_BTRFS_ROOT_ITEM_KEY(lib);
}

static PyObject *
_cffi_f_btrfs_stack_dir_name_len(PyObject *self, PyObject *arg0)
{
  struct btrfs_dir_item*  x0;
  unsigned long result;

  x0 = (struct btrfs_dir_item* )_cffi_to_c_pointer(arg0, _cffi_type(4));
  if (x0 == (struct btrfs_dir_item* )NULL && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = btrfs_stack_dir_name_len(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_unsigned_long(result);
}

static PyObject *_cffi_setup_custom(PyObject *lib)
{
  if (_cffi_const_BTRFS_INODE_REF_KEY(lib) < 0)
    return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef _cffi_methods[] = {
  {"_cffi_layout_struct_btrfs_timespec", _cffi_layout_struct_btrfs_timespec, METH_NOARGS},
  {"_cffi_layout_struct_btrfs_ioctl_ino_path_args", _cffi_layout_struct_btrfs_ioctl_ino_path_args, METH_NOARGS},
  {"_cffi_layout_struct_btrfs_ioctl_search_header", _cffi_layout_struct_btrfs_ioctl_search_header, METH_NOARGS},
  {"_cffi_layout_struct_btrfs_ioctl_fs_info_args", _cffi_layout_struct_btrfs_ioctl_fs_info_args, METH_NOARGS},
  {"_cffi_layout_struct_btrfs_ioctl_search_args", _cffi_layout_struct_btrfs_ioctl_search_args, METH_NOARGS},
  {"btrfs_stack_inode_ref_name_len", _cffi_f_btrfs_stack_inode_ref_name_len, METH_O},
  {"btrfs_stack_inode_size", _cffi_f_btrfs_stack_inode_size, METH_O},
  {"_cffi_layout_struct_btrfs_inode_item", _cffi_layout_struct_btrfs_inode_item, METH_NOARGS},
  {"_cffi_layout_struct_btrfs_root_item", _cffi_layout_struct_btrfs_root_item, METH_NOARGS},
  {"_cffi_layout_struct_btrfs_ioctl_ino_lookup_args", _cffi_layout_struct_btrfs_ioctl_ino_lookup_args, METH_NOARGS},
  {"_cffi_layout_struct_btrfs_file_extent_item", _cffi_layout_struct_btrfs_file_extent_item, METH_NOARGS},
  {"_cffi_layout_struct_btrfs_inode_ref", _cffi_layout_struct_btrfs_inode_ref, METH_NOARGS},
  {"_cffi_layout_struct_btrfs_dir_item", _cffi_layout_struct_btrfs_dir_item, METH_NOARGS},
  {"btrfs_stack_inode_mode", _cffi_f_btrfs_stack_inode_mode, METH_O},
  {"_cffi_layout_struct_btrfs_data_container", _cffi_layout_struct_btrfs_data_container, METH_NOARGS},
  {"btrfs_root_generation", _cffi_f_btrfs_root_generation, METH_O},
  {"btrfs_stack_file_extent_generation", _cffi_f_btrfs_stack_file_extent_generation, METH_O},
  {"_cffi_layout_struct_btrfs_ioctl_search_key", _cffi_layout_struct_btrfs_ioctl_search_key, METH_NOARGS},
  {"btrfs_stack_inode_generation", _cffi_f_btrfs_stack_inode_generation, METH_O},
  {"_cffi_layout_struct_btrfs_disk_key", _cffi_layout_struct_btrfs_disk_key, METH_NOARGS},
  {"btrfs_stack_dir_name_len", _cffi_f_btrfs_stack_dir_name_len, METH_O},
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

PyMODINIT_FUNC
init_cffi_x89e75365x62bd60ad(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi_x89e75365x62bd60ad", _cffi_methods);
  if (lib == NULL || 0 < 0)
    return;
  _cffi_init();
  return;
}
