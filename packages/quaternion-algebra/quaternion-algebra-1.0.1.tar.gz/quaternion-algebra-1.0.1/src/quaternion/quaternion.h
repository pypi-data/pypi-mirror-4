#ifndef __QUATERNION_H__
#define __QUATERNION_H__

typedef struct {
    PyObject_HEAD
    double w;
    double x;
    double y;
    double z;
} Quaternion;

static PyTypeObject QuaternionType;

#endif
