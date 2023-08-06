
#include <Python.h>
#include <stddef.h>

#ifdef MS_WIN32
#include <malloc.h>   /* for alloca() */
typedef __int8 int8_t;
typedef __int16 int16_t;
typedef __int32 int32_t;
typedef __int64 int64_t;
typedef unsigned __int8 uint8_t;
typedef unsigned __int16 uint16_t;
typedef unsigned __int32 uint32_t;
typedef unsigned __int64 uint64_t;
typedef unsigned char _Bool;
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
#endif

#define _cffi_from_c_double PyFloat_FromDouble
#define _cffi_from_c_float PyFloat_FromDouble
#define _cffi_from_c_long PyInt_FromLong
#define _cffi_from_c_ulong PyLong_FromUnsignedLong
#define _cffi_from_c_longlong PyLong_FromLongLong
#define _cffi_from_c_ulonglong PyLong_FromUnsignedLongLong

#define _cffi_to_c_double PyFloat_AsDouble
#define _cffi_to_c_float PyFloat_AsDouble

#define _cffi_from_c_SIGNED(x, type)                                     \
    (sizeof(type) <= sizeof(long) ? PyInt_FromLong(x) :                  \
                                    PyLong_FromLongLong(x))
#define _cffi_from_c_UNSIGNED(x, type)                                   \
    (sizeof(type) < sizeof(long) ? PyInt_FromLong(x) :                   \
     sizeof(type) == sizeof(long) ? PyLong_FromUnsignedLong(x) :         \
                                    PyLong_FromUnsignedLongLong(x))

#define _cffi_to_c_SIGNED(o, type)                                       \
    (sizeof(type) == 1 ? _cffi_to_c_i8(o) :                              \
     sizeof(type) == 2 ? _cffi_to_c_i16(o) :                             \
     sizeof(type) == 4 ? _cffi_to_c_i32(o) :                             \
     sizeof(type) == 8 ? _cffi_to_c_i64(o) :                             \
     (Py_FatalError("unsupported size for type " #type), 0))
#define _cffi_to_c_UNSIGNED(o, type)                                     \
    (sizeof(type) == 1 ? _cffi_to_c_u8(o) :                              \
     sizeof(type) == 2 ? _cffi_to_c_u16(o) :                             \
     sizeof(type) == 4 ? _cffi_to_c_u32(o) :                             \
     sizeof(type) == 8 ? _cffi_to_c_u64(o) :                             \
     (Py_FatalError("unsupported size for type " #type), 0))

#define _cffi_to_c_i8                                                    \
                 ((int(*)(PyObject *))_cffi_exports[1])
#define _cffi_to_c_u8                                                    \
                 ((int(*)(PyObject *))_cffi_exports[2])
#define _cffi_to_c_i16                                                   \
                 ((int(*)(PyObject *))_cffi_exports[3])
#define _cffi_to_c_u16                                                   \
                 ((int(*)(PyObject *))_cffi_exports[4])
#define _cffi_to_c_i32                                                   \
                 ((int(*)(PyObject *))_cffi_exports[5])
#define _cffi_to_c_u32                                                   \
                 ((unsigned int(*)(PyObject *))_cffi_exports[6])
#define _cffi_to_c_i64                                                   \
                 ((long long(*)(PyObject *))_cffi_exports[7])
#define _cffi_to_c_u64                                                   \
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
#define _cffi_to_c__Bool                                                 \
    ((_Bool(*)(PyObject *))_cffi_exports[22])
#define _cffi_prepare_pointer_call_argument                              \
    ((Py_ssize_t(*)(CTypeDescrObject *, PyObject *, char **))_cffi_exports[23])
#define _cffi_convert_array_from_object                                  \
    ((int(*)(char *, CTypeDescrObject *, PyObject *))_cffi_exports[24])
#define _CFFI_NUM_EXPORTS 25

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


#include <sodium.h>

static int _cffi_const_crypto_box_BEFORENMBYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_box_BEFORENMBYTES) && (crypto_box_BEFORENMBYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_box_BEFORENMBYTES));
  else if ((crypto_box_BEFORENMBYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_box_BEFORENMBYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_box_BEFORENMBYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_box_BEFORENMBYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_crypto_box_BOXZEROBYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_box_BOXZEROBYTES) && (crypto_box_BOXZEROBYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_box_BOXZEROBYTES));
  else if ((crypto_box_BOXZEROBYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_box_BOXZEROBYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_box_BOXZEROBYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_box_BOXZEROBYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_box_BEFORENMBYTES(lib);
}

static int _cffi_const_crypto_box_NONCEBYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_box_NONCEBYTES) && (crypto_box_NONCEBYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_box_NONCEBYTES));
  else if ((crypto_box_NONCEBYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_box_NONCEBYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_box_NONCEBYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_box_NONCEBYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_box_BOXZEROBYTES(lib);
}

static int _cffi_const_crypto_box_PUBLICKEYBYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_box_PUBLICKEYBYTES) && (crypto_box_PUBLICKEYBYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_box_PUBLICKEYBYTES));
  else if ((crypto_box_PUBLICKEYBYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_box_PUBLICKEYBYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_box_PUBLICKEYBYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_box_PUBLICKEYBYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_box_NONCEBYTES(lib);
}

static int _cffi_const_crypto_box_SECRETKEYBYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_box_SECRETKEYBYTES) && (crypto_box_SECRETKEYBYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_box_SECRETKEYBYTES));
  else if ((crypto_box_SECRETKEYBYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_box_SECRETKEYBYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_box_SECRETKEYBYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_box_SECRETKEYBYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_box_PUBLICKEYBYTES(lib);
}

static int _cffi_const_crypto_box_ZEROBYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_box_ZEROBYTES) && (crypto_box_ZEROBYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_box_ZEROBYTES));
  else if ((crypto_box_ZEROBYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_box_ZEROBYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_box_ZEROBYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_box_ZEROBYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_box_SECRETKEYBYTES(lib);
}

static int _cffi_const_crypto_hash_BYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_hash_BYTES) && (crypto_hash_BYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_hash_BYTES));
  else if ((crypto_hash_BYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_hash_BYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_hash_BYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_hash_BYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_box_ZEROBYTES(lib);
}

static int _cffi_const_crypto_hash_sha256_BYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_hash_sha256_BYTES) && (crypto_hash_sha256_BYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_hash_sha256_BYTES));
  else if ((crypto_hash_sha256_BYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_hash_sha256_BYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_hash_sha256_BYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_hash_sha256_BYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_hash_BYTES(lib);
}

static int _cffi_const_crypto_hash_sha512_BYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_hash_sha512_BYTES) && (crypto_hash_sha512_BYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_hash_sha512_BYTES));
  else if ((crypto_hash_sha512_BYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_hash_sha512_BYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_hash_sha512_BYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_hash_sha512_BYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_hash_sha256_BYTES(lib);
}

static int _cffi_const_crypto_secretbox_BOXZEROBYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_secretbox_BOXZEROBYTES) && (crypto_secretbox_BOXZEROBYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_secretbox_BOXZEROBYTES));
  else if ((crypto_secretbox_BOXZEROBYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_secretbox_BOXZEROBYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_secretbox_BOXZEROBYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_secretbox_BOXZEROBYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_hash_sha512_BYTES(lib);
}

static int _cffi_const_crypto_secretbox_KEYBYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_secretbox_KEYBYTES) && (crypto_secretbox_KEYBYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_secretbox_KEYBYTES));
  else if ((crypto_secretbox_KEYBYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_secretbox_KEYBYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_secretbox_KEYBYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_secretbox_KEYBYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_secretbox_BOXZEROBYTES(lib);
}

static int _cffi_const_crypto_secretbox_NONCEBYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_secretbox_NONCEBYTES) && (crypto_secretbox_NONCEBYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_secretbox_NONCEBYTES));
  else if ((crypto_secretbox_NONCEBYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_secretbox_NONCEBYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_secretbox_NONCEBYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_secretbox_NONCEBYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_secretbox_KEYBYTES(lib);
}

static int _cffi_const_crypto_secretbox_ZEROBYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_secretbox_ZEROBYTES) && (crypto_secretbox_ZEROBYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_secretbox_ZEROBYTES));
  else if ((crypto_secretbox_ZEROBYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_secretbox_ZEROBYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_secretbox_ZEROBYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_secretbox_ZEROBYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_secretbox_NONCEBYTES(lib);
}

static int _cffi_const_crypto_sign_BYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_sign_BYTES) && (crypto_sign_BYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_sign_BYTES));
  else if ((crypto_sign_BYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_sign_BYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_sign_BYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_sign_BYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_secretbox_ZEROBYTES(lib);
}

static int _cffi_const_crypto_sign_PUBLICKEYBYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_sign_PUBLICKEYBYTES) && (crypto_sign_PUBLICKEYBYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_sign_PUBLICKEYBYTES));
  else if ((crypto_sign_PUBLICKEYBYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_sign_PUBLICKEYBYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_sign_PUBLICKEYBYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_sign_PUBLICKEYBYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_sign_BYTES(lib);
}

static int _cffi_const_crypto_sign_SECRETKEYBYTES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (crypto_sign_SECRETKEYBYTES) && (crypto_sign_SECRETKEYBYTES) <= LONG_MAX)
    o = PyInt_FromLong((long)(crypto_sign_SECRETKEYBYTES));
  else if ((crypto_sign_SECRETKEYBYTES) <= 0)
    o = PyLong_FromLongLong((long long)(crypto_sign_SECRETKEYBYTES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(crypto_sign_SECRETKEYBYTES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "crypto_sign_SECRETKEYBYTES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_crypto_sign_PUBLICKEYBYTES(lib);
}

static PyObject *
_cffi_f_crypto_box_afternm(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned char const *  x1;
  unsigned long long x2;
  unsigned char const *  x3;
  unsigned char const *  x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:crypto_box_afternm", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(1), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_UNSIGNED(arg2, unsigned long long);
  if (x2 == (unsigned long long)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(1), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(1), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_box_afternm(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_crypto_box_beforenm(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned char const *  x1;
  unsigned char const *  x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:crypto_box_beforenm", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(1), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(1), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_box_beforenm(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_crypto_box_keypair(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned char*  x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:crypto_box_keypair", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(0), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_box_keypair(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_crypto_box_open_afternm(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned char const *  x1;
  unsigned long long x2;
  unsigned char const *  x3;
  unsigned char const *  x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:crypto_box_open_afternm", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(1), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_UNSIGNED(arg2, unsigned long long);
  if (x2 == (unsigned long long)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(1), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(1), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_box_open_afternm(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_crypto_hash(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned char const *  x1;
  unsigned long long x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:crypto_hash", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(1), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_UNSIGNED(arg2, unsigned long long);
  if (x2 == (unsigned long long)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_hash(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_crypto_hash_sha256(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned char const *  x1;
  unsigned long long x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:crypto_hash_sha256", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(1), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_UNSIGNED(arg2, unsigned long long);
  if (x2 == (unsigned long long)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_hash_sha256(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_crypto_hash_sha512(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned char const *  x1;
  unsigned long long x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:crypto_hash_sha512", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(1), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_UNSIGNED(arg2, unsigned long long);
  if (x2 == (unsigned long long)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_hash_sha512(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_crypto_scalarmult_curve25519_base(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned char const *  x1;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:crypto_scalarmult_curve25519_base", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(1), arg1) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_scalarmult_curve25519_base(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_crypto_secretbox(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned char const *  x1;
  unsigned long long x2;
  unsigned char const *  x3;
  unsigned char const *  x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:crypto_secretbox", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(1), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_UNSIGNED(arg2, unsigned long long);
  if (x2 == (unsigned long long)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(1), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(1), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_secretbox(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_crypto_secretbox_open(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned char const *  x1;
  unsigned long long x2;
  unsigned char const *  x3;
  unsigned char const *  x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:crypto_secretbox_open", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(1), arg1) < 0)
      return NULL;
  }

  x2 = _cffi_to_c_UNSIGNED(arg2, unsigned long long);
  if (x2 == (unsigned long long)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg3, (char **)&x3);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x3 = alloca(datasize);
    memset((void *)x3, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x3, _cffi_type(1), arg3) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(1), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_secretbox_open(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_crypto_sign(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned long long*  x1;
  unsigned char const *  x2;
  unsigned long long x3;
  unsigned char const *  x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:crypto_sign", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(2), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(1), arg2) < 0)
      return NULL;
  }

  x3 = _cffi_to_c_UNSIGNED(arg3, unsigned long long);
  if (x3 == (unsigned long long)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(1), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_sign(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_crypto_sign_open(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned long long*  x1;
  unsigned char const *  x2;
  unsigned long long x3;
  unsigned char const *  x4;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;
  PyObject *arg4;

  if (!PyArg_ParseTuple(args, "OOOOO:crypto_sign_open", &arg0, &arg1, &arg2, &arg3, &arg4))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(2), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(2), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(1), arg2) < 0)
      return NULL;
  }

  x3 = _cffi_to_c_UNSIGNED(arg3, unsigned long long);
  if (x3 == (unsigned long long)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg4, (char **)&x4);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x4 = alloca(datasize);
    memset((void *)x4, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x4, _cffi_type(1), arg4) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_sign_open(x0, x1, x2, x3, x4); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_crypto_sign_seed_keypair(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned char*  x1;
  unsigned char*  x2;
  Py_ssize_t datasize;
  int result;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;

  if (!PyArg_ParseTuple(args, "OOO:crypto_sign_seed_keypair", &arg0, &arg1, &arg2))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg1, (char **)&x1);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x1 = alloca(datasize);
    memset((void *)x1, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x1, _cffi_type(0), arg1) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg2, (char **)&x2);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x2 = alloca(datasize);
    memset((void *)x2, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x2, _cffi_type(0), arg2) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = crypto_sign_seed_keypair(x0, x1, x2); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_SIGNED(result, int);
}

static PyObject *
_cffi_f_randombytes(PyObject *self, PyObject *args)
{
  unsigned char*  x0;
  unsigned long long x1;
  Py_ssize_t datasize;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:randombytes", &arg0, &arg1))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    if (datasize < 0)
      return NULL;
    x0 = alloca(datasize);
    memset((void *)x0, 0, datasize);
    if (_cffi_convert_array_from_object((char *)x0, _cffi_type(0), arg0) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_UNSIGNED(arg1, unsigned long long);
  if (x1 == (unsigned long long)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { randombytes(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *_cffi_setup_custom(PyObject *lib)
{
  if (_cffi_const_crypto_sign_SECRETKEYBYTES(lib) < 0)
    return NULL;
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef _cffi_methods[] = {
  {"crypto_box_afternm", _cffi_f_crypto_box_afternm, METH_VARARGS},
  {"crypto_box_beforenm", _cffi_f_crypto_box_beforenm, METH_VARARGS},
  {"crypto_box_keypair", _cffi_f_crypto_box_keypair, METH_VARARGS},
  {"crypto_box_open_afternm", _cffi_f_crypto_box_open_afternm, METH_VARARGS},
  {"crypto_hash", _cffi_f_crypto_hash, METH_VARARGS},
  {"crypto_hash_sha256", _cffi_f_crypto_hash_sha256, METH_VARARGS},
  {"crypto_hash_sha512", _cffi_f_crypto_hash_sha512, METH_VARARGS},
  {"crypto_scalarmult_curve25519_base", _cffi_f_crypto_scalarmult_curve25519_base, METH_VARARGS},
  {"crypto_secretbox", _cffi_f_crypto_secretbox, METH_VARARGS},
  {"crypto_secretbox_open", _cffi_f_crypto_secretbox_open, METH_VARARGS},
  {"crypto_sign", _cffi_f_crypto_sign, METH_VARARGS},
  {"crypto_sign_open", _cffi_f_crypto_sign_open, METH_VARARGS},
  {"crypto_sign_seed_keypair", _cffi_f_crypto_sign_seed_keypair, METH_VARARGS},
  {"randombytes", _cffi_f_randombytes, METH_VARARGS},
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

PyMODINIT_FUNC
init_cffi__x89766aa6x20a28d1e(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__x89766aa6x20a28d1e", _cffi_methods);
  if (lib == NULL || 0 < 0)
    return;
  _cffi_init();
  return;
}
