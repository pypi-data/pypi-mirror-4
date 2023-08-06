
/* This file is part of ngs_plumbing. */

/* ngs_plumbing is free software: you can redistribute it and/or modify */
/* it under the terms of the GNU Affero General Public License as published by */
/* the Free Software Foundation, either version 3 of the License, or */
/* (at your option) any later version. */

/* ngs_plumbing is distributed in the hope that it will be useful, */
/* but WITHOUT ANY WARRANTY; without even the implied warranty of */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the */
/* GNU General Public License for more details. */

/* You should have received a copy of the GNU Affero General Public License */
/* along with ngs_plumbing.  If not, see <http://www.gnu.org/licenses/>. */

/* Copyright 2012 Laurent Gautier */

#define PY_SSIZE_T_CLEAN 
#include "Python.h"
#include "_libdna.h"

PyDoc_STRVAR(module_doc,
	     "C-level utilities to work with DNA, in particular if considering"
	     "bit-packing.");


//#define LIBDNA_DEBUG

#if (PY_VERSION_HEX < 0x03010000)
#define PyBytes PyString
#endif


#define LIBDNA_FROMBYTES(TYPENAME)					\
  Py_ssize_t n = TYPENAME ## _GET_SIZE(data_bytes);			\
  char *string = NULL; /* dummy */					\
  Py_ssize_t n_bit2 = nbytes_for_bit2(n);				\
  PyObject *bit2_a = TYPENAME ## _FromStringAndSize(string, n_bit2);	\
  bytes_to_bit2(TYPENAME ## _AS_STRING(data_bytes), n,			\
		TYPENAME ## _AS_STRING(bit2_a), n_bit2);		\
  return bit2_a;							\
  
#define LIBDNA_FROMBUFFER(TYPENAME)					\
  Py_ssize_t n = TYPENAME ## _GET_SIZE(data_bytes);			\
  char *string = NULL; /* dummy */					\
  Py_ssize_t n_bit2 = nbytes_for_bit2(n);				\
  PyObject *bit2_a = TYPENAME ## _FromStringAndSize(string, n_bit2);	\
  bytes_to_bit2((char *)(buffer_ptr->buf), buffer_ptr->len,		\
		TYPENAME ## _AS_STRING(bit2_a), n_bit2);		\

#define LIBDNA_FROMBIT2(TYPENAME)					\
  Py_ssize_t n_bit2 = TYPENAME ## _GET_SIZE(bit2_a);			\
  char *string = NULL; /* dummy */					\
  Py_ssize_t n = n_bit2 * 4;						\
  PyObject *data_bytes = TYPENAME ## _FromStringAndSize(string, n);	\
  bit2_to_bytes(TYPENAME ## _AS_STRING(bit2_a), n_bit2,			\
		TYPENAME ## _AS_STRING(data_bytes), n);			\
  return data_bytes;							\

  
#define LIBDNA_COMPLFROMBUFFER(TYPENAME)				\
  Py_ssize_t n_bit2 = TYPENAME ## _GET_SIZE(bit2_a);			\
  char *string = NULL; /* dummy */					\
  PyObject *bit2_ca = TYPENAME ## _FromStringAndSize(string, n_bit2);	\
  bit2_to_bit2compl(TYPENAME ## _AS_STRING(bit2_a), n_bit2,		\
		    TYPENAME ## _AS_STRING(bit2_ca));			\
  return bit2_ca;							\
  
#define LIBDNA_REVFROMBUFFER(TYPENAME)					\
  Py_ssize_t n_bit2 = TYPENAME ## _GET_SIZE(bit2_a);			\
  char *string = NULL; /* dummy */					\
  PyObject *bit2_ra = TYPENAME ## _FromStringAndSize(string, n_bit2);	\
  bit2_to_bit2rev(TYPENAME ## _AS_STRING(bit2_a), n_bit2,		\
		  TYPENAME ## _AS_STRING(bit2_ra));			\
  return bit2_ra;							\

#define LIBDNA_REVCOMPLFROMBUFFER(TYPENAME)				\
  Py_ssize_t n_bit2 = TYPENAME ## _GET_SIZE(bit2_a);			\
  char *string = NULL; /* dummy */					\
  PyObject *bit2_rca = TYPENAME ## _FromStringAndSize(string, n_bit2);	\
  bit2_to_bit2compl(TYPENAME ## _AS_STRING(bit2_a), n_bit2,		\
		    TYPENAME ## _AS_STRING(bit2_rca));			\
  bit2_to_bit2rev(TYPENAME ## _AS_STRING(bit2_rca), n_bit2,		\
		  TYPENAME ## _AS_STRING(bit2_rca));			\
  return bit2_rca;							\



static inline Py_ssize_t nbytes_for_bit2(Py_ssize_t n) {
  Py_ssize_t nbytes;
  nbytes = n / (int)4;
  if ((n % 4) != 0)
    nbytes++;
  return nbytes;
}

static inline void bytes_to_bit2(const char *read, const Py_ssize_t n, 
				 char *bit2_ptr, const Py_ssize_t bit2_n)
{
  Py_ssize_t i, bit2_i;
  unsigned char cur_byte;

  bit2_i = 0;
  unsigned int bitpos = 6;

  bit2_ptr[bit2_i] = 0;
  for (i=0; i < n; i++)
    {

      if (bitpos == -2) {
	bitpos = 6;
	bit2_i++;
	bit2_ptr[bit2_i] = 0;
	if (bit2_i >= bit2_n) {
	  printf("Out of range (unpacked #%zd, packed #%zd >= #%zd).\n", i, bit2_i, bit2_n);
	}
      }

      cur_byte = _ASCII_TO_BIT2[(unsigned char)read[i]];
      bit2_ptr[bit2_i] |= (cur_byte << (bitpos));

      bitpos -= 2;

    }
}

/*
 * Convert an array bit2_ptr of bit-packed DNA of length bit2_n
 * to the characters corresponding to the DNA into the buffer
 * "dna" (of length "n", specified to be able to spit an error
 * message out if inconsistency in the lengths).
 */
static inline void bit2_to_bytes(const char *bit2_ptr, const Py_ssize_t bit2_n,
				 char *dna, const Py_ssize_t n)
{
  Py_ssize_t dna_i, bit2_i;
  unsigned char cur_byte;
  int bitpos;

#ifdef LIBDNA_DEBUG
	printf("bit2_n: %zd\n", bit2_n);
#endif

  dna_i = 0;
  for (bit2_i=0; bit2_i < bit2_n; bit2_i++)
    //printf("dna_i: %zd, bit2_i: %zd\n", dna_i, bit2_i);
    {
      cur_byte = bit2_ptr[bit2_i];
      for (bitpos = 6; bitpos >= 0; bitpos -= 2) {
	if (dna_i >= n)
	  printf("Out of range (packed #%zd, unpacked #%zd >= #%zd).\n", 
		 bit2_i, dna_i, n);
	dna[dna_i] = _ACGT[(cur_byte >> (bitpos)) & 0x3];
	dna_i++;
      }
    }
}





PyDoc_STRVAR(bit2_frombytes_doc,
"Takes a bytes object and returns a bytes object"
"with the DNA values encoded on 2 bits.\n");
static PyObject* bit2_frombytes(PyObject *self, PyObject *data_bytes)
{
  if (PyBytes_Check(data_bytes)) {
    LIBDNA_FROMBYTES(PyBytes);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be a string (bytes).");
    return NULL;
  }
}

PyDoc_STRVAR(bit2_frombytearray_doc,
"Takes a bytearray object and returns a bytearray"
"with the DNA values encoded on 2 bits.\n");
static PyObject* bit2_frombytearray(PyObject *self, PyObject *data_bytes)
{
  if (PyByteArray_Check(data_bytes)) {
    LIBDNA_FROMBYTES(PyByteArray);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be an array of bytes (bytearray).");
    return NULL;
  }
}

PyDoc_STRVAR(bit2_frombuffer_doc,
"Takes a buffer-implementing object and returns a bytearray"
"with the DNA values encoded on 2 bits.\n");
static PyObject* bit2_frombuffer(PyObject *self, PyObject *data_bytes)
{
  Py_buffer buffer;
  Py_buffer *buffer_ptr = &buffer;
  int err_buf = PyObject_GetBuffer(data_bytes, buffer_ptr, PyBUF_SIMPLE);
  if (err_buf == 0) {
    LIBDNA_BUFFERCHECK( < 2, 1);
    LIBDNA_FROMBUFFER(PyByteArray);
    PyBuffer_Release(buffer_ptr);
    return bit2_a;
  } else {
    return NULL;
  }
}

PyDoc_STRVAR(byte_frombit2bytearray_doc,
"Takes a bytearray object with 2-bit packed DNA values and returns a bytearray with DNA");
static PyObject* byte_frombit2bytearray(PyObject *self, PyObject *bit2_a)
{
  if (PyByteArray_Check(bit2_a)) {
    LIBDNA_FROMBIT2(PyByteArray);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be an array of bytes (bytearray).");
    return NULL;
  }
}

PyDoc_STRVAR(byte_frombit2bytes_doc,
"Takes a bytes object with 2-bit packed DNA values and returns bytes with the DNA");
static PyObject* byte_frombit2bytes(PyObject *self, PyObject *bit2_a)
{
  if (PyBytes_Check(bit2_a)) {
    LIBDNA_FROMBIT2(PyBytes);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be bytes.");
    return NULL;
  }
}


static inline void bit2_to_bit2compl(const char *bit2_ptr, 
				     const Py_ssize_t bit2_n,
				     char *bit2compl_prt)
{
  Py_ssize_t bit2_i;
  unsigned char cur_byte;

  #ifdef LIBDNA_DEBUG
  printf("bit2_n: %zd\n", bit2_n);
  #endif

  for (bit2_i=0; bit2_i < bit2_n; bit2_i++)
    {
      cur_byte = bit2_ptr[bit2_i];
      bit2compl_prt[bit2_i] = ~ cur_byte;
    }
}


PyDoc_STRVAR(bit2complement_frombit2bytes_doc,
"Takes a bytes object with 2-bit packed DNA values and returns bytes with the DNA complement");
static PyObject* bit2complement_frombit2bytes(PyObject *self, PyObject *bit2_a)
{
  if (PyBytes_Check(bit2_a)) {
    LIBDNA_COMPLFROMBUFFER(PyBytes);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be bytes.");
    return NULL;
  }
}
PyDoc_STRVAR(bit2complement_frombit2bytearray_doc,
"Takes a bytearray object with 2-bit packed DNA values and returns the DNA complement still packed.");
static PyObject* bit2complement_frombit2bytearray(PyObject *self, 
						  PyObject *bit2_a)
{
  if (PyByteArray_Check(bit2_a)) {
    LIBDNA_COMPLFROMBUFFER(PyByteArray);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be bytearray.");
    return NULL;
  }
}

static inline void bit2_to_bit2rev(const char *bit2_ptr, 
				   const Py_ssize_t bit2_n,
				   char *bit2rev_prt)
{
  Py_ssize_t bit2_i;
  unsigned char lcur_byte, rcur_byte;
  int bitpos;

#ifdef LIBDNA_DEBUG
  printf("bit2_n: %zd\n", bit2_n);
#endif

  const Py_ssize_t half = bit2_n / 2;

  for (bit2_i=0; bit2_i < half; bit2_i++)
    {
      lcur_byte = 0;//bit2_ptr[bit2_i];
      rcur_byte = 0;//bit2_ptr[bit2_n - bit2_i - 1];
      for (bitpos = 6; bitpos >= 0; bitpos -= 2) {
	lcur_byte |= ((bit2_ptr[bit2_i] >> (bitpos)) & 0x3) << (6-bitpos);
	rcur_byte |= ((bit2_ptr[bit2_n - bit2_i - 1] >> (bitpos)) & 0x3) << (6-bitpos);
      }
      bit2rev_prt[bit2_n - bit2_i - 1] = lcur_byte;
      bit2rev_prt[bit2_i] = rcur_byte;
    }

  if ((bit2_n & 0x1) == 1) {
    lcur_byte = 0;
    for (bitpos = 6; bitpos >= 0; bitpos -= 2) {
      lcur_byte |= ((bit2_ptr[half] >> (bitpos)) & 0x3) << (6-bitpos);
    }
    bit2rev_prt[half] = lcur_byte;
  }
}
PyDoc_STRVAR(bit2rev_frombit2bytes_doc,
"Takes a bytes object with 2-bit packed DNA values and returns the reverse sequence.");
static PyObject* bit2rev_frombit2bytes(PyObject *self, 
				       PyObject *bit2_a)
{
  if (PyBytes_Check(bit2_a)) {
    LIBDNA_REVFROMBUFFER(PyBytes);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be bytes.");
    return NULL;
  }
}
PyDoc_STRVAR(bit2rev_frombit2bytearray_doc,
"Takes a bytearray object with 2-bit packed DNA values and returns the reverse sequence.");
static PyObject* bit2rev_frombit2bytearray(PyObject *self, 
					   PyObject *bit2_a)
{
  if (PyByteArray_Check(bit2_a)) {
    LIBDNA_REVFROMBUFFER(PyByteArray);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be bytearray.");
    return NULL;
  }
}

PyDoc_STRVAR(bit2revcompl_frombit2bytes_doc,
"Takes a bytes object with 2-bit packed DNA values and returns the reverse complement sequence still packed.");
static PyObject* bit2revcompl_frombit2bytes(PyObject *self, 
					    PyObject *bit2_a)
{
  if (PyBytes_Check(bit2_a)) {
    LIBDNA_REVCOMPLFROMBUFFER(PyBytes);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be bytes.");
    return NULL;
  }
}
PyDoc_STRVAR(bit2revcompl_frombit2bytearray_doc,
"Takes a bytearray object with 2-bit packed DNA values and returns the reverse complement sequence still packed.");
static PyObject* bit2revcompl_frombit2bytearray(PyObject *self, 
						PyObject *bit2_a)
{
  if (PyByteArray_Check(bit2_a)) {
    LIBDNA_REVCOMPLFROMBUFFER(PyByteArray);
  } else {
    PyErr_Format(PyExc_TypeError, "Parameter must be bytearray.");
    return NULL;
  }
}


/* Convenience function (could be a macro) */
static inline void make_sliceboundaries(const Py_ssize_t ilow, 
					const Py_ssize_t ihigh, 
					SliceBoundaries *slbo)
{
  /* */
  slbo->low_n_padbytes = ((ilow % NGSP_WORD_SIZE) == 0) ? 0 : NGSP_WORD_SIZE - (ilow % NGSP_WORD_SIZE);
  slbo->low_offset = (slbo->low_n_padbytes == 0)?0:1;
  slbo->high_n_padbytes = ihigh % NGSP_WORD_SIZE;
  slbo->high_offset = (slbo->high_n_padbytes == 0)?0:1;
  slbo->ilow_packed = ilow / NGSP_WORD_SIZE; /* lowest packed index */
  slbo->ihigh_packed = (ihigh - 1) / NGSP_WORD_SIZE + 1;// - (high_n_padbytes == 0 ? 1 : 0); /* highest packed index */
}



static inline void packeddna_fromslice(const Py_ssize_t ilow, 
				       const Py_ssize_t ihigh,
				       Packed2BitDNA *packeddna)
{
  packeddna->len = ihigh - ilow;
  packeddna->len_packed = ((ihigh - 1) / NGSP_WORD_SIZE + 1) - ilow / NGSP_WORD_SIZE;
  packeddna->offset = ((ilow % NGSP_WORD_SIZE) == 0) ? 0 : NGSP_WORD_SIZE - (ilow % NGSP_WORD_SIZE);
}



PyDoc_STRVAR(slicebit2_frombit2bytes_doc,
"Takes a bytes object with 2-bit packed DNA values, a slice with coordinates on the unpacked sequence, and returns a 2-bit packed slice. As with other Python slices the last element is not included.");
static PyObject* slicebit2_frombit2bytes(PyObject *self, PyObject *args)
{

  Py_ssize_t ilow, ihigh;
  PyObject *packed_bytes;
  if (!PyArg_ParseTuple(args, "O!nn", &PyBytes_Type, &packed_bytes, 
			&ilow, &ihigh)) { 
    return NULL; 
  }

  if (ilow < 0) {
    PyErr_Format(PyExc_IndexError, 
		 "Lowest limit for the slice must be positive");
    return NULL;
  }
  if (ihigh < ilow) {
    PyErr_Format(PyExc_IndexError, 
		 "Lowest index must be lower than the highest.");
    return NULL;
  }

  const Py_ssize_t n_p = PyBytes_GET_SIZE(packed_bytes);
  unsigned char *packed = (unsigned char*) PyBytes_AS_STRING(packed_bytes);

  const Py_ssize_t ilow_p = ilow / NGSP_WORD_SIZE;
  const Py_ssize_t ihigh_p = (ihigh / NGSP_WORD_SIZE) + ((ihigh % 4 == 0) ? 0 : 1);
  //FIXME: test >0
  const int shiftlow = ilow % NGSP_WORD_SIZE;
  const int shifthigh = NGSP_WORD_SIZE - shiftlow;
  //printf("shiftlow: %i\n", shiftlow);

  if (ihigh_p > n_p) {
    PyErr_Format(PyExc_IndexError,
		 "Highest limit for the interval out of bound "
		 "(requesting %zd while length is %zd)", ihigh_p, n_p);
    return NULL;
  }

  //const Py_ssize_t n_slicepacked = ihigh_p - ilow_p; 
  const Py_ssize_t padding_size = (ihigh - ilow) % NGSP_WORD_SIZE;
  const Py_ssize_t n_slicepacked = ((ihigh - ilow) / NGSP_WORD_SIZE) + \
    (padding_size==0 ? 0 : 1); 
  char *string = NULL;
  PyObject *slice_bytes = PyBytes_FromStringAndSize(string, n_slicepacked);
  unsigned char *slicepacked = (unsigned char*) PyBytes_AS_STRING(slice_bytes);
  Py_ssize_t i_res;
  for (i_res = 0; i_res < n_slicepacked; i_res++) {
    slicepacked[i_res] = (packed[ilow_p + i_res] << (shiftlow * 2));
    if ((shiftlow != 0) && (i_res < (n_slicepacked + 1)) && (ilow_p + i_res + 1 < n_p)) {
      slicepacked[i_res] |= (packed[ilow_p + i_res + 1] >> (shifthigh*2));
    }
  }
  /* by convention pad with trailing 'A's the remaining bases */
  if (padding_size != 0) {
    const Py_ssize_t right_padding = NGSP_WORD_SIZE - padding_size;
    slicepacked[n_slicepacked-1] &= (0xff << (right_padding * 2));
  }
  return slice_bytes;
}



PyDoc_STRVAR(slice_frombit2bytes_doc,
"Takes a bytes object with 2-bit packed DNA values, a slice, and returns the DNA segment in the slice as bytes. As with other Python slices the last element is not included.");
static PyObject* slice_frombit2bytes(PyObject *self, PyObject *args)
{

  Py_ssize_t ilow, ihigh;
  PyObject *packed_bytes;
  if (!PyArg_ParseTuple(args, "O!nn", &PyBytes_Type, &packed_bytes, 
			&ilow, &ihigh)) { 
    return NULL; 
  }

  if (ilow < 0) {
    PyErr_Format(PyExc_IndexError, 
		 "Lowest limit for the slice must be positive");
    return NULL;
  }
  if (ihigh < ilow) {
    PyErr_Format(PyExc_IndexError, 
		 "Lowest index must be lower than the highest.");
    return NULL;
  }

  const Py_ssize_t n_p = PyBytes_GET_SIZE(packed_bytes);
  unsigned char *packed = (unsigned char*) PyBytes_AS_STRING(packed_bytes);

  const Py_ssize_t ilow_p = ilow / NGSP_WORD_SIZE;
  const Py_ssize_t ihigh_p = (ihigh / NGSP_WORD_SIZE) + ((ihigh % 4 == 0) ? 0 : 1);
  
  if (ihigh_p > (n_p+1)) {
    PyErr_Format(PyExc_IndexError,
		 "Highest limit for the interval out of bound "
		 "(requesting %zd while length is %zd)", ihigh_p, n_p);
    return NULL;
  }

  const int lpadding_size = (ilow % NGSP_WORD_SIZE) == 0 ? 0 : (NGSP_WORD_SIZE - ilow % NGSP_WORD_SIZE);
  const int rpadding_size = ihigh % NGSP_WORD_SIZE;
  const Py_ssize_t n_sliceunpacked = ihigh - ilow; 
  char *string = NULL;
  PyObject *slice_bytes = PyBytes_FromStringAndSize(string, n_sliceunpacked);
  char *sliceunpacked = PyBytes_AS_STRING(slice_bytes);

  Py_ssize_t i_res;
  int bitpos;
  for (i_res = 0; i_res < lpadding_size; i_res++) {
    bitpos = i_res * 2;
    sliceunpacked[lpadding_size - i_res - 1] = \
      _ACGT[(packed[ilow_p] >> bitpos) & 0x3];
  }
  
  const Py_ssize_t ilow_offset = (lpadding_size != 0) ? 1 : 0;
  const Py_ssize_t ihigh_offset = (rpadding_size != 0) ? 1 : 0;
  bit2_to_bytes((char *)&packed[ilow_p + ilow_offset], 
		ihigh_p - ihigh_offset - ilow_p - ilow_offset, 
  		&sliceunpacked[i_res], ihigh - ilow - lpadding_size - rpadding_size);

  for (i_res = 0; i_res < rpadding_size; i_res++) {
    bitpos = 6 - i_res * 2;
    sliceunpacked[i_res + ihigh - ilow - rpadding_size] = \
      _ACGT[(packed[ihigh_p-1] >> bitpos) & 0x3];
  }

  return slice_bytes;
}



PyDoc_STRVAR(slice_frombit2bytearray_doc,
"Takes a bytearray object with 2-bit packed DNA values, a slice, and returns a 2-bit packed slice based on the unpacked indices. As with other Python slices the last element is not included.");
static PyObject* slice_frombit2bytearray(PyObject *self, PyObject *args)
{

  Py_ssize_t ilow, ihigh;
  PyObject *packed_bytes;
  const int NGSP_WORD_SIZE = 4;
  if (!PyArg_ParseTuple(args, "O!nn", &PyByteArray_Type, &packed_bytes, 
			&ilow, &ihigh)) { 
    return NULL; 
  }

  if (ilow < 0) {
    PyErr_Format(PyExc_IndexError, 
		 "Lowest limit for the slice must be positive");
    return NULL;
  }
  if (ihigh < ilow) {
    PyErr_Format(PyExc_IndexError, 
		 "Lowest index must be, well, lower that the highest.");
    return NULL;
  }

  Py_ssize_t n = PyBytes_GET_SIZE(packed_bytes);

  /* Offset if boundaries of the slice not multiple of NGSP_WORD_SIZE */
  Py_ssize_t low_n_padbytes = ((ilow % NGSP_WORD_SIZE) == 0) ? 0 : NGSP_WORD_SIZE - (ilow % NGSP_WORD_SIZE);
  int low_offset = (low_n_padbytes == 0)?0:1;
  Py_ssize_t high_n_padbytes = ihigh % NGSP_WORD_SIZE;
  int high_offset = (high_n_padbytes == 0)?0:1;
  Py_ssize_t ilow_packed = ilow / NGSP_WORD_SIZE; /* lowest packed index */
  Py_ssize_t ihigh_packed = (ihigh - 1) / NGSP_WORD_SIZE + 1;// - (high_n_padbytes == 0 ? 1 : 0); /* highest packed index */
  int k;

  if (ihigh_packed >= n) {
    PyErr_Format(PyExc_IndexError, 
		 "Highest limit for the interval out of bound.");
    return NULL;
  }

  Py_ssize_t n_up = ihigh - ilow;
  char *string = NULL;
  PyObject *buf_bytes = PyByteArray_FromStringAndSize(string, n_up);
  char *unpacked = PyByteArray_AS_STRING(buf_bytes);

  char *packed = PyByteArray_AS_STRING(packed_bytes);

  if ( ilow_packed+low_offset < ihigh_packed ) {
    bit2_to_bytes(&(packed[ilow_packed+low_offset]),
		  (ihigh_packed - ilow_packed - low_offset - high_offset),
		  &(unpacked[low_n_padbytes]), 
		  ihigh - ilow);
  }
  char padbytes[NGSP_WORD_SIZE];

  /* if offset on lower end, now take care of sub word-sized segment */
  if (low_offset) {
    int foo = 0;
    bit2_to_bytes(&(packed[ilow_packed - foo]), 1,
		  (char *)(&padbytes), NGSP_WORD_SIZE);
    for (k = 0; k < low_n_padbytes; k++) {
      unpacked[k] = padbytes[NGSP_WORD_SIZE - low_n_padbytes + k];
    }
  }

  /* if offset on higher end, now take care of sub word-sized segment */
  if (high_offset) {
    bit2_to_bytes(&(packed[ihigh_packed-1]), 1, // 10/3
		  (char *)(&padbytes), NGSP_WORD_SIZE);
    for (k = 0; k < high_n_padbytes; k++) {
      unpacked[ihigh - ilow - high_n_padbytes + k] = padbytes[k];
    }
    
  }
  return buf_bytes;
}



static PyMethodDef libxsq_methods[] = {
  {"bit2_frombytes", (PyCFunction)bit2_frombytes,  METH_O,
   bit2_frombytes_doc},
  {"bit2_frombytearray", (PyCFunction)bit2_frombytearray,  METH_O,
   bit2_frombytearray_doc},
  {"bit2_frombuffer", (PyCFunction)bit2_frombuffer,  METH_O,
   bit2_frombuffer_doc},
  {"byte_frombit2bytes", (PyCFunction)byte_frombit2bytes,  METH_O,
   byte_frombit2bytes_doc},
  {"byte_frombit2bytearray", (PyCFunction)byte_frombit2bytearray,  METH_O,
   byte_frombit2bytearray_doc},
  {"slice_frombit2bytes", (PyCFunction)slice_frombit2bytes,  METH_VARARGS,
   slice_frombit2bytes_doc},
  {"slice_frombit2bytearray", (PyCFunction)slice_frombit2bytearray,  METH_VARARGS,
   slice_frombit2bytearray_doc},
  {"slicebit2_frombit2bytes", (PyCFunction)slicebit2_frombit2bytes,  METH_VARARGS,
   slicebit2_frombit2bytes_doc},
  {"bit2complement_frombit2bytes", (PyCFunction)bit2complement_frombit2bytes,  METH_O,
   bit2complement_frombit2bytes_doc},
  {"bit2complement_frombit2bytearray", (PyCFunction)bit2complement_frombit2bytearray,  METH_O,
   bit2complement_frombit2bytearray_doc},
  {"bit2reverse_frombit2bytes", (PyCFunction)bit2rev_frombit2bytes,  METH_O,
   bit2rev_frombit2bytes_doc},
  {"bit2reverse_frombit2bytearray", (PyCFunction)bit2rev_frombit2bytearray,  METH_O,
   bit2rev_frombit2bytearray_doc},
  {"bit2reversecomplement_frombit2bytes", (PyCFunction)bit2revcompl_frombit2bytes,  METH_O,
   bit2revcompl_frombit2bytes_doc},
  {"bit2reversecomplement_frombit2bytearray", (PyCFunction)bit2revcompl_frombit2bytearray,  METH_O,
   bit2revcompl_frombit2bytearray_doc},
  {NULL,                NULL}           /* sentinel */
};



#if (PY_VERSION_HEX < 0x03010000)
#else
static struct PyModuleDef libdnamodule = {
   PyModuleDef_HEAD_INIT,
   "_libdna",           /* name of module */
   module_doc,               /* module documentation, may be NULL */
   -1,                     /* size of per-interpreter state */
   libxsq_methods       /* method table */
 };
#endif

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC
#if (PY_VERSION_HEX < 0x03010000)
init_libdna(void)
#else
PyInit__libdna(void)
#endif
{
  /* Finalize the type object including setting type of the new type
         * object; doing it here is required for portability to Windows 
         * without requiring C++. */

  PyObject *m;
  /* *d; */
  //  static void *PyRinterface_API[PyRinterface_API_pointers];
  //PyObject *c_api_object;

#if (PY_VERSION_HEX < 0x03010000)
  m = Py_InitModule3("_libdna", libxsq_methods, module_doc);
#else
  m = PyModule_Create(&libdnamodule);
#endif
  if (m == NULL) {
#if (PY_VERSION_HEX < 0x03010000)
    return;
#else
    return NULL;
#endif
  }

/*   /\* Initialize the C API pointer array *\/ */
/*   PyRinterface_API[ PyRinterface_IsInitialized_NUM ] =	\ */
/*     (void *)PyRinterface_IsInitialized; */
/*   PyRinterface_API[ PyRinterface_FindFun_NUM ] =	\ */
/*     (void *)PyRinterface_FindFun; */
/*   /\* Create a Capsule containing the API pointer array's address *\/ */
/*   c_api_object = PyCapsule_New((void *)PyRinterface_API,  */
/* 			       PyRinterface_API_NAME, NULL); */
/*   if (c_api_object == NULL) { */
/* #if (PY_VERSION_HEX < 0x03010000) */
/*     return; */
/* #else */
/*     return NULL; */
/* #endif */
/*   } else { */
/*     PyModule_AddObject(m, "_C_API", c_api_object); */
/*   } */
/*  d = PyModule_GetDict(m); */

#if (PY_VERSION_HEX < 0x03010000)
#else
  return m;
#endif
}

