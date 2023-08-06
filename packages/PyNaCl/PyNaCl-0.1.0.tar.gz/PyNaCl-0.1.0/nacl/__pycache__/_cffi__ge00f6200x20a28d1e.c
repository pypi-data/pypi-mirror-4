
#include <stdio.h>
#include <stddef.h>
#include <stdarg.h>
#include <errno.h>
#include <sys/types.h>   /* XXX for ssize_t on some platforms */

#ifdef _WIN32
#  include <Windows.h>
#  define snprintf _snprintf
typedef __int8 int8_t;
typedef __int16 int16_t;
typedef __int32 int32_t;
typedef __int64 int64_t;
typedef unsigned __int8 uint8_t;
typedef unsigned __int16 uint16_t;
typedef unsigned __int32 uint32_t;
typedef unsigned __int64 uint64_t;
typedef SSIZE_T ssize_t;
typedef unsigned char _Bool;
#else
#  include <stdint.h>
#endif

#include <sodium.h>
int _cffi_const_crypto_box_BEFORENMBYTES(long long *out_value)
{
  *out_value = (long long)(crypto_box_BEFORENMBYTES);
  return (crypto_box_BEFORENMBYTES) <= 0;
}

int _cffi_const_crypto_box_BOXZEROBYTES(long long *out_value)
{
  *out_value = (long long)(crypto_box_BOXZEROBYTES);
  return (crypto_box_BOXZEROBYTES) <= 0;
}

int _cffi_const_crypto_box_NONCEBYTES(long long *out_value)
{
  *out_value = (long long)(crypto_box_NONCEBYTES);
  return (crypto_box_NONCEBYTES) <= 0;
}

int _cffi_const_crypto_box_PUBLICKEYBYTES(long long *out_value)
{
  *out_value = (long long)(crypto_box_PUBLICKEYBYTES);
  return (crypto_box_PUBLICKEYBYTES) <= 0;
}

int _cffi_const_crypto_box_SECRETKEYBYTES(long long *out_value)
{
  *out_value = (long long)(crypto_box_SECRETKEYBYTES);
  return (crypto_box_SECRETKEYBYTES) <= 0;
}

int _cffi_const_crypto_box_ZEROBYTES(long long *out_value)
{
  *out_value = (long long)(crypto_box_ZEROBYTES);
  return (crypto_box_ZEROBYTES) <= 0;
}

int _cffi_const_crypto_hash_BYTES(long long *out_value)
{
  *out_value = (long long)(crypto_hash_BYTES);
  return (crypto_hash_BYTES) <= 0;
}

int _cffi_const_crypto_hash_sha256_BYTES(long long *out_value)
{
  *out_value = (long long)(crypto_hash_sha256_BYTES);
  return (crypto_hash_sha256_BYTES) <= 0;
}

int _cffi_const_crypto_hash_sha512_BYTES(long long *out_value)
{
  *out_value = (long long)(crypto_hash_sha512_BYTES);
  return (crypto_hash_sha512_BYTES) <= 0;
}

int _cffi_const_crypto_secretbox_BOXZEROBYTES(long long *out_value)
{
  *out_value = (long long)(crypto_secretbox_BOXZEROBYTES);
  return (crypto_secretbox_BOXZEROBYTES) <= 0;
}

int _cffi_const_crypto_secretbox_KEYBYTES(long long *out_value)
{
  *out_value = (long long)(crypto_secretbox_KEYBYTES);
  return (crypto_secretbox_KEYBYTES) <= 0;
}

int _cffi_const_crypto_secretbox_NONCEBYTES(long long *out_value)
{
  *out_value = (long long)(crypto_secretbox_NONCEBYTES);
  return (crypto_secretbox_NONCEBYTES) <= 0;
}

int _cffi_const_crypto_secretbox_ZEROBYTES(long long *out_value)
{
  *out_value = (long long)(crypto_secretbox_ZEROBYTES);
  return (crypto_secretbox_ZEROBYTES) <= 0;
}

int _cffi_const_crypto_sign_BYTES(long long *out_value)
{
  *out_value = (long long)(crypto_sign_BYTES);
  return (crypto_sign_BYTES) <= 0;
}

int _cffi_const_crypto_sign_PUBLICKEYBYTES(long long *out_value)
{
  *out_value = (long long)(crypto_sign_PUBLICKEYBYTES);
  return (crypto_sign_PUBLICKEYBYTES) <= 0;
}

int _cffi_const_crypto_sign_SECRETKEYBYTES(long long *out_value)
{
  *out_value = (long long)(crypto_sign_SECRETKEYBYTES);
  return (crypto_sign_SECRETKEYBYTES) <= 0;
}

int _cffi_f_crypto_box_afternm(unsigned char * x0, unsigned char const * x1, unsigned long long x2, unsigned char const * x3, unsigned char const * x4)
{
  return crypto_box_afternm(x0, x1, x2, x3, x4);
}

int _cffi_f_crypto_box_beforenm(unsigned char * x0, unsigned char const * x1, unsigned char const * x2)
{
  return crypto_box_beforenm(x0, x1, x2);
}

int _cffi_f_crypto_box_keypair(unsigned char * x0, unsigned char * x1)
{
  return crypto_box_keypair(x0, x1);
}

int _cffi_f_crypto_box_open_afternm(unsigned char * x0, unsigned char const * x1, unsigned long long x2, unsigned char const * x3, unsigned char const * x4)
{
  return crypto_box_open_afternm(x0, x1, x2, x3, x4);
}

int _cffi_f_crypto_hash(unsigned char * x0, unsigned char const * x1, unsigned long long x2)
{
  return crypto_hash(x0, x1, x2);
}

int _cffi_f_crypto_hash_sha256(unsigned char * x0, unsigned char const * x1, unsigned long long x2)
{
  return crypto_hash_sha256(x0, x1, x2);
}

int _cffi_f_crypto_hash_sha512(unsigned char * x0, unsigned char const * x1, unsigned long long x2)
{
  return crypto_hash_sha512(x0, x1, x2);
}

int _cffi_f_crypto_scalarmult_curve25519_base(unsigned char * x0, unsigned char const * x1)
{
  return crypto_scalarmult_curve25519_base(x0, x1);
}

int _cffi_f_crypto_secretbox(unsigned char * x0, unsigned char const * x1, unsigned long long x2, unsigned char const * x3, unsigned char const * x4)
{
  return crypto_secretbox(x0, x1, x2, x3, x4);
}

int _cffi_f_crypto_secretbox_open(unsigned char * x0, unsigned char const * x1, unsigned long long x2, unsigned char const * x3, unsigned char const * x4)
{
  return crypto_secretbox_open(x0, x1, x2, x3, x4);
}

int _cffi_f_crypto_sign(unsigned char * x0, unsigned long long * x1, unsigned char const * x2, unsigned long long x3, unsigned char const * x4)
{
  return crypto_sign(x0, x1, x2, x3, x4);
}

int _cffi_f_crypto_sign_open(unsigned char * x0, unsigned long long * x1, unsigned char const * x2, unsigned long long x3, unsigned char const * x4)
{
  return crypto_sign_open(x0, x1, x2, x3, x4);
}

int _cffi_f_crypto_sign_seed_keypair(unsigned char * x0, unsigned char * x1, unsigned char * x2)
{
  return crypto_sign_seed_keypair(x0, x1, x2);
}

void _cffi_f_randombytes(unsigned char * x0, unsigned long long x1)
{
  randombytes(x0, x1);
}

