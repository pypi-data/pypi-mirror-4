#include <Python.h>

#include <stdio.h>
#include "math.h"
#include "structmember.h"
#include "quaternion.h"


static void Quaternion_dealloc(Quaternion* self)
{
    self->ob_type->tp_free((PyObject*)self);
}


static PyObject *
Quaternion_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Quaternion *self;

    self = (Quaternion *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->w = 0;
        self->x = 0;
        self->y = 0;
        self->z = 0;
    }

    return (PyObject *)self;
}


static int
Quaternion_init(Quaternion *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"w", "x", "y", "z", NULL};
    if (! PyArg_ParseTupleAndKeywords(args, kwds, "|dddd", kwlist, 
                                      &self->w, &self->x,
                                      &self->y, &self->z))
        return -1; 
    return 0;
}



static PyMemberDef Quaternion_members[] = {
    {"w", T_DOUBLE, offsetof(Quaternion, w), 0, "w"},
    {"x", T_DOUBLE, offsetof(Quaternion, x), 0, "x"},
    {"y", T_DOUBLE, offsetof(Quaternion, y), 0, "y"},
    {"z", T_DOUBLE, offsetof(Quaternion, z), 0, "z"},
    {NULL}  /* Sentinel */
};


void dbl2str(char *s, char *ss, double n)
{
    long d = labs((long) n);
    long f = (long) ((n - d) * 1000000);

    if (f > 0)
        sprintf(s, "%ld.%ld", d, f);
    else
        sprintf(s, "%ld", d);

    if (n >= 0)
        strcpy(ss, "+");
    else
        strcpy(ss, "-");
}


static PyObject *
Quaternion_str(Quaternion* self)
{
    static PyObject *format = NULL;
    PyObject *args, *result;

    char w[50], ws[2];
    char x[50], xs[2];
    char y[50], ys[2];
    char z[50], zs[2];

    dbl2str(w, ws, self->w);
    dbl2str(x, xs, self->x);
    dbl2str(y, ys, self->y);
    dbl2str(z, zs, self->z);

    if (strcmp(ws, "+") == 0) strcpy(ws, "");

    if (format == NULL) {
        format = PyString_FromString("(%s%s %s %si %s %sj %s %sk)");
        if (format == NULL) return NULL;
    }

    args = Py_BuildValue("ssssssss", ws, w, xs, x, ys, y, zs, z);
    if (args == NULL) return NULL;

    result = PyString_Format(format, args);
    Py_DECREF(args);
    
    return result;
}


static PyObject *
Quaternion_add(Quaternion *q1, Quaternion *q2)
{
    Quaternion *result;

    result = PyObject_New(Quaternion, &QuaternionType);
    if (result != NULL) {
        result->w = q1->w + q2->w;
        result->x = q1->x + q2->x;
        result->y = q1->y + q2->y;
        result->z = q1->z + q2->z;
    }

    return (PyObject *)result;
}


static PyObject *
Quaternion_subtract(Quaternion *q1, Quaternion *q2)
{
    Quaternion *result;

    result = PyObject_New(Quaternion, &QuaternionType);
    if (result != NULL) {
        result->w = q1->w - q2->w;
        result->x = q1->x - q2->x;
        result->y = q1->y - q2->y;
        result->z = q1->z - q2->z;
    }

    return (PyObject *)result;
}


static PyObject *
Quaternion_multiply(Quaternion *q1, Quaternion *q2)
{
    Quaternion *result;

    result = PyObject_New(Quaternion, &QuaternionType);
    if (result != NULL) {
        result->w = q1->w*q2->w - q1->x*q2->x - q1->y*q2->y - q1->z*q2->z;
        result->x = q1->w*q2->x + q1->x*q2->w + q1->y*q2->z - q1->z*q2->y;
        result->y = q1->w*q2->y - q1->x*q2->z + q1->y*q2->w + q1->z*q2->x;
        result->z = q1->w*q2->z + q1->x*q2->y - q1->y*q2->x + q1->z*q2->w;
    }

    return (PyObject *)result;
}


static PyObject *
Quaternion_divide(Quaternion *q1, Quaternion *q2)
{
    Quaternion *result;
    double s = q2->w*q2->w + q2->x*q2->x + q2->y*q2->y + q2->z*q2->z;

    result = PyObject_New(Quaternion, &QuaternionType);
    if (result != NULL) {
        result->w = (  q1->w*q2->w + q1->x*q2->x + q1->y*q2->y + q1->z*q2->z) / s;
        result->x = (- q1->w*q2->x + q1->x*q2->w + q1->y*q2->z - q1->z*q2->y) / s;
        result->y = (- q1->w*q2->y - q1->x*q2->z + q1->y*q2->w + q1->z*q2->x) / s;
        result->z = (- q1->w*q2->z + q1->x*q2->y - q1->y*q2->x + q1->z*q2->w) / s;
    }

    return (PyObject *)result;
}


static PyObject *
Quaternion_absolute(Quaternion *q)
{
    double result;
    result = sqrt(q->w*q->w + q->x*q->x + q->y*q->y + q->z*q->z);
    return Py_BuildValue("d", result);
}


static PyMethodDef Quaternion_methods[] = {
    {NULL}  /* Sentinel */
};


static PyNumberMethods Quaternion_as_number = {
    (binaryfunc)Quaternion_add,       /* nb_add */
    (binaryfunc)Quaternion_subtract,  /* nb_subtract */
    (binaryfunc)Quaternion_multiply,  /* nb_multiply */
    (binaryfunc)Quaternion_divide,    /* nb_divide */
    0,                                /* nb_remainder */
    0,                                /* nb_divmod */
    0,                                /* nb_power */
    0,                                /* nb_negative */
    0,                                /* nb_positive */
    (unaryfunc)Quaternion_absolute,   /* nb_absolute */
    0,                                /* nb_nonzero */
    0,                                /* nb_invert */
    0,                                /* nb_lshift */
    0,                                /* nb_rshift */
    0,                                /* nb_and */
    0,                                /* nb_xor */
    0,                                /* nb_or */
    0,                                /* nb_coerce */
    0,                                /* nb_int */
    0,                                /* nb_long */
    0,                                /* nb_float */
    0,                                /* nb_oct */
    0,                                /* nb_hex */
    0,                                /* nb_inplace_add */
    0,                                /* nb_inplace_subtract */
    0,                                /* nb_inplace_multiply */
    0,                                /* nb_inplace_divide */
    0,                                /* nb_inplace_remainder */
    0,                                /* nb_inplace_power */
    0,                                /* nb_inplace_lshift */
    0,                                /* nb_inplace_rshift */
    0,                                /* nb_inplace_and */
    0,                                /* nb_inplace_xor */
    0,                                /* nb_inplace_or */
    0,                                /* nb_floor_divide */
    0,                                /* nb_true_divide */
    0,                                /* nb_inplace_floor_divide */
    0,                                /* nb_inplace_true_divide */
    0,                                /* nb_index */
};


static PyTypeObject QuaternionType = {
    PyObject_HEAD_INIT(NULL)
    0,                              /* ob_size */
    "_quaternion.Quaternion",       /* tp_name */
    sizeof(Quaternion),             /* tp_basicsize */
    0,                              /* tp_itemsize */
    (destructor)Quaternion_dealloc, /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_compare */
    0,                              /* tp_repr */
    &Quaternion_as_number,           /* tp_as_number */
    0,                              /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    (reprfunc)Quaternion_str,       /* tp_str */
    0,                              /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "Quaternion object",            /* tp_doc */
    0,		                    /* tp_traverse */
    0,		                    /* tp_clear */
    0,		                    /* tp_richcompare */
    0,		                    /* tp_weaklistoffset */
    0,		                    /* tp_iter */
    0,		                    /* tp_iternext */
    Quaternion_methods,             /* tp_methods */
    Quaternion_members,             /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    (initproc)Quaternion_init,      /* tp_init */
    0,                              /* tp_alloc */
    Quaternion_new,                 /* tp_new */
};


static PyMethodDef quaternion_funcs[] = {
    {NULL}
};


PyMODINIT_FUNC
init_quaternion(void)
{
    PyObject* m;

    if (PyType_Ready(&QuaternionType) < 0) return;

    m = Py_InitModule("_quaternion", quaternion_funcs);

    if (m == NULL) return;

    Py_INCREF(&QuaternionType);
    PyModule_AddObject(m, "Quaternion", (PyObject *)&QuaternionType);
}
