#ifndef GEMPY_PY_ALIGNMENT
#define GEMPY_PY_ALIGNMENT
/*
 * Alignment class
 */
#include "Python.h"
#include "structmember.h"
#include "gem_tools.h"

typedef struct {
    PyObject_HEAD
    gt_alignment* alignment;
    gt_template* template;
    uint64_t index;
} Alignment;

Alignment* create_alignment(gt_alignment* alignment, gt_template* parent, uint64_t index);
void Alignment_dealloc(PyObject* self);

int Alignment_init(Alignment *self, PyObject *args, PyObject *kwds);
PyObject* Alignment_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
PyObject* Alignment_gettag(Alignment *self, void *closure);
int Alignment_settag(Alignment *self, PyObject *value, void *closure);
PyObject* Alignment_getread(Alignment *self, void *closure);
int Alignment_setread(Alignment *self, PyObject *value, void *closure);
PyObject* Alignment_getqualities(Alignment *self, void *closure);
int Alignment_setqualities(Alignment *self, PyObject *value, void *closure);
PyObject* Alignment_getmax_complete_strata(Alignment *self, void *closure);
int Alignment_setmax_complete_strata(Alignment *self, PyObject *value, void *closure);
PyObject* Alignment_get_counters(PyObject* self, PyObject* closure);
PyObject* Alignment_to_sequence(PyObject *self, PyObject *args);
char* gempy_alignment_get_tag(Alignment* self);



#endif
