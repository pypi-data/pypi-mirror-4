
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
	     "C-level utilities to work with DNA + quality "
	     "(so mostly read-based sequencing).");


//#define LIBDNA_DEBUG

#if (PY_VERSION_HEX < 0x03010000)
#define PyBytes PyString
#endif

static inline void basequal_to_bit2(const unsigned char *base_ptr, 
				    const unsigned char *qual_ptr,
				    const Py_ssize_t n,
				    unsigned char *bit2)
{
  /* build the bit-packed values from the bases and corresponding qualities. */
  Py_ssize_t i;
  for (i=0; i<n; i++)
    {
      bit2[i] = _ASCII_TO_BIT2[base_ptr[i]] & 0x3;
      bit2[i] = bit2[i] | (qual_ptr[i] << 2);
    }
}

PyDoc_STRVAR(bit2bytes_frombasequal_doc,
"bit2bytes_frombasequal(bases, qualities) -> bit2packed_bytes."
"\nTakes two bytes object with DNA and quality and returned 2-bit packed bytes");
static PyObject* bit2bytes_frombasequal(PyObject *self, PyObject *args)
{
  Py_ssize_t n;
  PyObject *base_bytes, *qual_bytes;
  if (!PyArg_ParseTuple(args, "O!O!", &PyBytes_Type, &base_bytes,
			&PyBytes_Type, &qual_bytes)) { 
    return NULL; 
  }

  n = PyBytes_GET_SIZE(base_bytes);
  if (n != PyBytes_GET_SIZE(qual_bytes)) {
    PyErr_Format(PyExc_ValueError, 
		 "Bases and qualities must have the same length.");
  }
  char *string = NULL;
  PyObject *packed_bytes = PyBytes_FromStringAndSize(string, n);
  char *packed_ptr = PyBytes_AS_STRING(packed_bytes);
  char *base_ptr = PyBytes_AS_STRING(base_bytes);
  char *qual_ptr = PyBytes_AS_STRING(qual_bytes);
  basequal_to_bit2((unsigned char*)base_ptr, 
		   (unsigned char *)qual_ptr, n, 
		   (unsigned char *)packed_ptr);
  return packed_bytes;
}



/* PyDoc_STRVAR(qualbins_doc, */
/* "Count binned quality values. " */
/* "\nqualbins(qual, counts)"); */
/* static PyObject* qualbins(PyObject *self, PyObject *args) */
/* { */
/*   PyObject *qual_bytes, *counts; */
/*   Py_ssize_t qual_min, qual_max; */
/*   if (!PyArg_ParseTuple(args, "O!Onn", &PyBytes_Type, &qual_bytes,  */
/* 			&counts, &qual_min, &qual_max)) { */
/*     return NULL; */
/*   } */
/*   Py_ssize_t counts_i, qual_j; */
/*   Py_ssize_t qual_size = PyBytes_GET_SIZE(qual); */
/*   if (counts_size == -1) { */
/*     PyErr_Format(PyExc_TypeError, */
/* 		 "Counts must be a sequence (and have a length)"); */
/*     return NULL; */
/*   } */
/*   Py_buffer buffer; */
/*   Py_buffer *buffer_ptr = &buffer; */
/*   int err_buf = PyObject_GetBuffer(counts, buffer_ptr, PyBUF_SIMPLE); */
/*   if (err_buf == 0) { */
/*     LIBDNA_BUFFERCHECK( == 2, (int)sizeof(Py_ssize_t)); */
/*     Py_ssize_t strides = buffer_ptr->strides[0]; */
/*     for (counts_i = 0; counts_i < counts_size; counts_i++) { */
/*       for (qual_j = 0; qual_j < strides; qual_j++) { */
/* 	((Py_ssize_t *)(buffer_ptr->buf))[counts_i + strides * qual[qual_j]]++; */
/*       } */
/*     } */
/*     PyBuffer_Release(buffer_ptr); */
/*     Py_INCREF(Py_None); */
/*     return Py_None; */
/*   } else { */
/*     return NULL; */
/*   } */
/* } */


static PyMethodDef libdnaqual_methods[] = {
  /*  {"qualbins",   (PyCFunction)qualbins,  METH_VARARGS,
      qualbins_doc}, */
  {"bit2bytes_frombasequal",   
   (PyCFunction)bit2bytes_frombasequal,  METH_VARARGS,
   bit2bytes_frombasequal_doc},
  {NULL,                NULL}           /* sentinel */
};


#if (PY_VERSION_HEX < 0x03010000)
#else
static struct PyModuleDef libdnaqualmodule = {
   PyModuleDef_HEAD_INIT,
   "_libdnaqual",           /* name of module */
   module_doc,               /* module documentation, may be NULL */
   -1,                     /* size of per-interpreter state */
   libdnaqual_methods       /* method table */
 };
#endif

#ifndef PyMODINIT_FUNC  /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC
#if (PY_VERSION_HEX < 0x03010000)
init_libdnaqual(void)
#else
PyInit__libdnaqual(void)
#endif
{
  /* Finalize the type object including setting type of the new type
         * object; doing it here is required for portability to Windows 
         * without requiring C++. */

  PyObject *m;
  /* *d; */

#if (PY_VERSION_HEX < 0x03010000)
  m = Py_InitModule3("_libdnaqual", libdnaqual_methods, module_doc);
#else
  m = PyModule_Create(&libdnaqualmodule);
#endif
  if (m == NULL) {
#if (PY_VERSION_HEX < 0x03010000)
    return;
#else
    return NULL;
#endif
  }

#if (PY_VERSION_HEX < 0x03010000)
#else
  return m;
#endif
}

