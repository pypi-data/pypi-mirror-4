#include <Python.h>
#include "fnv.h"

static PyObject * fnvhash2_fnv_32a_str(PyObject *self, PyObject *args) {
  Fnv32_t fnv_32_res;
  const char *need_to_hash;
  
  if(!PyArg_ParseTuple(args, "s", &need_to_hash))
    return NULL;
  
  fnv_32_res = fnv_32a_str(need_to_hash, (Fnv32_t)0);
  return Py_BuildValue("I",fnv_32_res);
}

static PyObject * fnvhash2_fnv_64a_str(PyObject *self, PyObject *args) {
  Fnv64_t fnv_64_res;
  const char *need_to_hash;
  
  if(!PyArg_ParseTuple(args, "s", &need_to_hash))
    return NULL;
  
  fnv_64_res = fnv_64a_str(need_to_hash, (Fnv64_t)0);
  return Py_BuildValue("K",fnv_64_res);
}


static PyMethodDef fnvhash_methods[] = {
  {"fnv_32a_str", fnvhash2_fnv_32a_str, METH_VARARGS, "32bit hash function"},
  {"fnv_64a_str", fnvhash2_fnv_64a_str, METH_VARARGS, "64bit hash function"},
  {NULL, NULL, 0, NULL},
};

PyMODINIT_FUNC initfnvhash2() {
  PyObject *m;
  m = Py_InitModule("fnvhash2", fnvhash_methods);
  
}
