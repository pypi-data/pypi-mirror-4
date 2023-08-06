#ifndef Py__LIBDNA_H_
#define Py__LIBDNA_H_

#ifdef __cplusplus
extern "C" {
#endif

/* A: 0b00, C: 0b01, G: 0b10, T: 0b11 */
/* note: the DNA complement is the bitwise not */
const unsigned char _ACGT[] = "ACGT";

/* Quick lookup based on ASCII codes. */
/* note: the lookup is case insensitive */
/* note: any character outside of ACGT is considered as an A,
 *       checks are the programmer's responsibility */
const unsigned char _ASCII_TO_BIT2[] = \
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
   0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

const int NGSP_WORD_SIZE = 4;

#define LIBDNA_BUFFERCHECK(NDIM_CHECK, ITEMSIZE)			\
  if (! ((buffer_ptr->ndim) NDIM_CHECK)) {				\
    PyErr_Format(PyExc_ValueError,					\
		 "Only accepts buffer_ptrs with ndim %s", #NDIM_CHECK); \
    PyBuffer_Release(buffer_ptr);					\
    return NULL;							\
  }									\
  if (buffer_ptr->itemsize != ITEMSIZE) {				\
    PyErr_Format(PyExc_ValueError,					\
		 "Only accepts buffer_ptrs with items of size %i", ITEMSIZE); \
    PyBuffer_Release(buffer_ptr);					\
    return NULL;							\
  }									\
  if (!PyBuffer_IsContiguous(buffer_ptr, 'A')) {			\
    PyErr_Format(PyExc_ValueError,					\
	       "Only accepts contiguous buffer_ptrs.");			\
    PyBuffer_Release(buffer_ptr);					\
  return NULL;								\
  }									\


/*
 *  AACG ACCG TTCA CGTA GCCG TAAA
 * |----|----|----|----|----|----|
 *----^ ilow = 2
 *----------------------------^ ihigh = 21
 *======^ ilow_packed = 0
 *===============================^ ihigh_packed = 6
 *    |-----------------------| len
 */
typedef struct {
  Py_ssize_t low_n_padbytes;
  int low_offset;
  Py_ssize_t high_n_padbytes;
  int high_offset;
  Py_ssize_t ilow_packed;
  Py_ssize_t ihigh_packed;
 } SliceBoundaries;


/* 
 *  AACG ACCG TTCA CGTA GCCG TAAA
 * |----|----|----|----|----|----|
 *----^  offset
 *    |-----------------------| len = 20
 * |=============================| len_packed = 6
 * offset: informs about eventual padding before the
 * beginning of the sequence (padding supposed to be all "A"s).
 * len: number of elements sequence there is an eventual padding at
 *      the end.
 */
typedef struct {
  char *dna;
  Py_ssize_t len;
  Py_ssize_t len_packed;
  short int offset;
} Packed2BitDNA;

#ifdef __cplusplus
}
#endif

#endif /* !Py__LIBDNA_H_ */

