#define PY_SSIZE_T_CLEAN
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <Python.h>
#include "structmember.h"

static int cast_to_c(PyObject*, double**, int*, int*);
static int cast_to_py(PyObject**, double*, int, int);
static int validate(PyObject*); 
static void split_lines(char*, char*);

static int validate(PyObject *pyArray) 
{
    int i_size, j_size;
    i_size = PyList_Size(pyArray);
    PyObject *list = PyList_GetItem(pyArray, 0);
    if (list != NULL) {
        j_size = PyList_Size(list);
    } else {
        PyErr_SetString(PyExc_IndexError,
                        "Values list is empty");
        Py_XDECREF(list);
        return -1;        
    }

    for (int i = 0; i < i_size; i++) {
        PyObject *list = PyList_GetItem(pyArray, i);
        if (PyList_Size(list) != j_size) {
            PyErr_SetString(PyExc_RuntimeError,
                            "Lists have to be same size");
            // Py_XDECREF(list);
            return -1; 
        }
    }

    return 0;
}

static int cast_to_c(PyObject *pyArray, double **cArray, int *i_size, int *j_size) 
{   
    if (validate(pyArray)) return -1;
    
    *i_size = PyList_Size(pyArray);
    PyObject *list = PyList_GetItem(pyArray, 0);
    if (list != NULL) {
        *j_size = PyList_Size(list);
    } else {
        PyErr_SetString(PyExc_IndexError,
                        "Values list is empty");
        Py_XDECREF(list);
        return -1;        
    }

    *cArray = (double *) realloc(*cArray, sizeof(double ) * (*i_size) * (*j_size));
    if (*cArray == NULL) {
        PyErr_SetString(PyExc_MemoryError,
                        "Error allocating memory");
        return -1;
    }

    for (int i = 0; i < *i_size; i++) {
        PyObject *list = PyList_GetItem(pyArray, i);

        for (int j = 0; j < *j_size; j++) {
            PyObject *elem = PyList_GetItem(list, j);
            double value = 0;
            if (elem != NULL) {
                if (PyFloat_Check(elem)) {
                    value = PyFloat_AsDouble(elem);
                } else if (PyLong_Check(elem)) {
                    value = PyLong_AsDouble(elem);
                } else {
                    PyErr_SetString(PyExc_TypeError,
                            "Values can be only integer or float");
                }
                (*cArray)[i * (*j_size) + j] = value;
            }

        }

    }

    return 0;
}

static int cast_to_py(PyObject **pyArray, double *cArray, int i_size, int j_size) 
{
    PyObject *new_list = PyList_New(i_size);
    if (new_list == NULL) {
        PyErr_SetString(PyExc_MemoryError,
                "Error allocating memory");
        Py_XDECREF(new_list);
        return -1;
    }
    for (int i = 0; i < i_size; i++) {
        PyObject *new_elem = PyList_New(j_size);
        if (new_list == NULL) {
            PyErr_SetString(PyExc_MemoryError,
                "Error allocating memory");
            Py_XDECREF(new_list);
            Py_XDECREF(new_elem);
            return -1;
        }
        for (int j = 0; j < j_size; j++) {
            PyObject *value = Py_BuildValue("d", cArray[i * (j_size) + j]);
            if (PyList_SetItem(new_elem, j, value)) {
                Py_XDECREF(new_list);
                Py_XDECREF(new_elem);
                return -1;
            }
        }
        if (PyList_SetItem(new_list, i, new_elem)) {
            Py_XDECREF(new_list);
            Py_XDECREF(new_elem);
            return -1;
        }
    }
    // PyObject *tmp = pyArray;
    // Py_INCREF(new_list);
    (*pyArray) = new_list;
    // Py_XDECREF(tmp);

    return 0;
}


typedef struct {
    PyObject_HEAD
    PyObject *values; 
    //PyObject *last;  /* last name */
    int i_size;
    int j_size;
    double* cvalues;
} MatrixObject;

static void
Matrix_dealloc(MatrixObject *self)
{
    Py_XDECREF(self->values);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *
Matrix_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    MatrixObject *self;
    self = (MatrixObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
        self->values = PyList_New(0);
        if (self->values == NULL) {
            Py_DECREF(self);
            return NULL;
        }
        self->cvalues = NULL;
    }
    return (PyObject *) self;
}

static int
Matrix_init(MatrixObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"values", NULL};
    PyObject *values = NULL, *tmp;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &values))
        return -1;

    if (values) {
        tmp = self->values;
        Py_INCREF(values);
        self->values = values;
        Py_XDECREF(tmp);

        if (cast_to_c(self->values, &(self->cvalues), 
                      &(self->i_size), &(self->j_size)))
            return -1;

        // if (cast_to_py(self->values, self->cvalues, 
        //               self->i_size, self->j_size))
        //     return -1;
    }

    return 0;
}

static PyMemberDef Matrix_members[] = {
    // {"values", T_OBJECT_EX, offsetof(MatrixObject, values), 0,
    //  "matrix values"},
    {NULL}  /* Sentinel */
};

static PyObject *
Matrix_getvalues(MatrixObject *self, void *closure)
{
    Py_INCREF(self->values);
    return self->values;
}

static int
Matrix_setvalues(MatrixObject *self, PyObject *value, void *closure)
{   
    PyObject *tmp;
    if (value == NULL) {
        PyErr_SetString(PyExc_TypeError, "Cannot delete the values attribute");
        return -1;
    }
    if (!PyList_Check(value)) {
        PyErr_SetString(PyExc_TypeError,
                        "The first attribute value must be a list");
        return -1;
    }

    if (validate(value)) return -1;

    tmp = self->values;
    Py_INCREF(value);
    self->values = value;
    Py_DECREF(tmp);
    
    if (cast_to_c(self->values, &(self->cvalues), 
                      &(self->i_size), &(self->j_size)))
            return -1;

    return 0;
}

static PyGetSetDef Matrix_getsetters[] = {
    {"values", (getter) Matrix_getvalues, (setter) Matrix_setvalues,
     "matrix values", NULL},
    {NULL}  /* Sentinel */
};

static PyObject * 
Matrix_repr(MatrixObject *self)
{
    PyObject* str = PyObject_Str(self->values);
    // const char* s = PyString_AsString(objectsRepresentation);
    return PyUnicode_FromFormat("Matrix(%S)", str);
}

static void split_lines(char* result, char* str)
{
    int len = strlen(str);
    result[0] = str[0];
    result[1] = str[1];
    char ppr = str[0], pr = str[1];
    int j = 2;
    for (int i = 2; i < len; i++) {
        if (ppr == ']' && pr == ',') {
            result[j] = '\n';
            j++;
        }
        result[j] = str[i];
        ppr = pr;
        pr = str[i];
        j++;
    }
    result[j] = '\0';
}

static PyObject * 
Matrix_str(MatrixObject *self)
{
    PyObject* repr = PyObject_Repr(self->values);
    PyObject* str = PyUnicode_AsEncodedString(repr, "utf-8", "strict");
    char* raw_result = PyBytes_AsString(str);
    Py_XDECREF(repr);
    Py_XDECREF(str);
    int num_lines = PyList_Size(self->values);
    int len = strlen(raw_result);
    char result[len + num_lines];
    split_lines(result, raw_result);
    return PyUnicode_FromString(result);
}

static PyObject *
Matrix_subscription(MatrixObject *self, PyObject *key)
{
    if (!PyTuple_CheckExact(key) || (PyTuple_Size(key) != 2)) {
        PyErr_SetString(PyExc_TypeError,
                "Not a tuple of 2 elements");
        return NULL;
    }
    PyObject *i_obj, *j_obj;
    i_obj = PyTuple_GetItem(key, 0);
    j_obj = PyTuple_GetItem(key, 1);

    Py_ssize_t i, j;
    i = PyLong_AsSsize_t(i_obj);
    j = PyLong_AsSsize_t(j_obj);
    Py_XDECREF(i_obj);
    Py_XDECREF(j_obj);

    PyObject *list = PyList_GetItem(self->values, i);
    if (list != NULL) {
        PyObject *elem = PyList_GetItem(list, j);
        // Py_XDECREF(list);
        return elem;
    } else {
        PyErr_SetString(PyExc_IndexError, "list index out of range");
    }

    Py_RETURN_NONE;
}

static PyMappingMethods Matrix_mapping = {
        (lenfunc)0,                      /* mp_length */
        (binaryfunc)Matrix_subscription, /* mp_subscript */
        (objobjargproc)0,                /* mp_ass_subscript */
};

static PyObject *
Matrix_print_values(MatrixObject *self, PyObject *Py_UNUSED(ignored))
{
    // return self->values;
    // return PyUnicode_FromString("PLS");
    for(int i = 0; i < self->i_size * self->j_size; i++) {
        printf("%lf ", self->cvalues[i]);
    }
    printf("\n");

    Py_RETURN_NONE;
}


static PyMethodDef Matrix_methods[] = {
    {"print_values", (PyCFunction) Matrix_print_values, METH_NOARGS,
     "Return the values of matrix (kekw)"
    },
    {NULL}  /* Sentinel */
};

static void dot_product(double *a1, double *a2, double *res, 
                        int i_size_1, int j_size_1, int i_size_2, int j_size_2) {
    for (int i = 0; i < i_size_1; i++) {
        for (int j = 0; j < j_size_2; j++) {
            res[i * (j_size_1) + j] = 0;
            for (int k = 0; k < i_size_2; k++) {
                 res[i * (j_size_2) + j] += a1[i * (j_size_1) + k] 
                                          * a2[k * (j_size_2) + j];
            }
        }
    }
}

static MatrixObject * 
Matrix_mul(PyObject* obj1, PyObject* obj2) 
{
    MatrixObject* self;
    if (PyLong_Check(obj1)) {
        self = (MatrixObject*) obj2;
        double value = PyLong_AsDouble(obj1);
        double* new_cvalues = (double *)malloc(sizeof(double )*self->i_size * self->j_size);
        for(int i = 0; i < self->i_size * self->j_size; i++) {
            new_cvalues[i] = self->cvalues[i] * value;
        }

        MatrixObject* result = (MatrixObject*) Py_TYPE(obj2)->tp_new(Py_TYPE(obj2), NULL, NULL);
        result->values = PyList_New(0);
        cast_to_py(&(result->values), new_cvalues, self->i_size, self->j_size);
        result->cvalues = new_cvalues;
        result->i_size = self->i_size;
        result->j_size = self->j_size;

        return result;
    }

    if (PyLong_Check(obj2)) {
        self = (MatrixObject*) obj1;
        double value = PyLong_AsDouble(obj2); 
        double* new_cvalues = (double *)malloc(sizeof(double )*self->i_size * self->j_size);
        for(int i = 0; i < self->i_size * self->j_size; i++) {
            new_cvalues[i] = self->cvalues[i] * value;
        }

        MatrixObject* result = (MatrixObject*) Py_TYPE(obj1)->tp_new(Py_TYPE(obj1), NULL, NULL);
        result->values = PyList_New(0);
        cast_to_py(&(result->values), new_cvalues, self->i_size, self->j_size);
        result->cvalues = new_cvalues;
        result->i_size = self->i_size;
        result->j_size = self->j_size;

        return result;
    }

    if (Py_TYPE(obj1) == Py_TYPE(obj2)) { // matrices multiplication
        MatrixObject* m1 = (MatrixObject*) obj1;
        MatrixObject* m2 = (MatrixObject*) obj2;
        
        if (m1->j_size != m2->i_size) {
            PyErr_SetString(PyExc_TypeError,
                        "Invalid matrixes sizes");
            return NULL;
        }
        double* new_cvalues = (double *)malloc(sizeof(double )*m1->i_size * m2->j_size);
        dot_product(m1->cvalues, m2->cvalues, new_cvalues, 
                    m1->i_size, m1->j_size, m2->i_size, m2->j_size);

        // for(int i = 0; i < m1->i_size * m2->j_size; i++) {
        //     printf("%ld ", new_cvalues[i]);
        // }
        
        MatrixObject* result = (MatrixObject*) Py_TYPE(obj1)->tp_new(Py_TYPE(obj1), NULL, NULL);
        result->values = PyList_New(0);
        cast_to_py(&(result->values), new_cvalues, m1->i_size, m2->j_size);
        result->cvalues = new_cvalues;
        result->i_size = m1->i_size;
        result->j_size = m2->j_size;

        return result;
    }

    PyErr_SetString(PyExc_TypeError,
                        "Invalid types");
    return NULL;

}

static MatrixObject * 
Matrix_add(PyObject* obj1, PyObject* obj2) 
{
    MatrixObject* self;
    if (PyLong_Check(obj1)) {
        self = (MatrixObject*) obj2;
        double value = PyLong_AsDouble(obj1);
        double* new_cvalues = (double *)malloc(sizeof(double )*self->i_size * self->j_size);
        for(int i = 0; i < self->i_size * self->j_size; i++) {
            new_cvalues[i] = self->cvalues[i] + value;
        }

        MatrixObject* result = (MatrixObject*) Py_TYPE(obj2)->tp_new(Py_TYPE(obj2), NULL, NULL);
        result->values = PyList_New(0);
        cast_to_py(&(result->values), new_cvalues, self->i_size, self->j_size);
        result->cvalues = new_cvalues;
        result->i_size = self->i_size;
        result->j_size = self->j_size;

        return result;
    }

    if (PyLong_Check(obj2)) {
        self = (MatrixObject*) obj1;
        double value = PyLong_AsDouble(obj2); 
        double* new_cvalues = (double *)malloc(sizeof(double )*self->i_size * self->j_size);
        for(int i = 0; i < self->i_size * self->j_size; i++) {
            new_cvalues[i] = self->cvalues[i] + value;
        }

        MatrixObject* result = (MatrixObject*) Py_TYPE(obj1)->tp_new(Py_TYPE(obj1), NULL, NULL);
        result->values = PyList_New(0);
        cast_to_py(&(result->values), new_cvalues, self->i_size, self->j_size);
        result->cvalues = new_cvalues;
        result->i_size = self->i_size;
        result->j_size = self->j_size;

        return result;
    }

    if (Py_TYPE(obj1) == Py_TYPE(obj2)) { // matrices multiplication
        MatrixObject* m1 = (MatrixObject*) obj1;
        MatrixObject* m2 = (MatrixObject*) obj2;
        
        if ((m1->i_size != m2->i_size) || (m1->j_size != m2->j_size)) {
            PyErr_SetString(PyExc_TypeError,
                        "Invalid matrixes sizes");
            return NULL;
        }
        double* new_cvalues = (double *)malloc(sizeof(double )*m1->i_size * m2->i_size);

        for(int i = 0; i < m1->i_size * m2->j_size; i++) {
            new_cvalues[i] = m1->cvalues[i] + m2->cvalues[i];
        }
        
        MatrixObject* result = (MatrixObject*) Py_TYPE(obj1)->tp_new(Py_TYPE(obj1), NULL, NULL);
        result->values = PyList_New(0);
        cast_to_py(&(result->values), new_cvalues, m1->i_size, m2->j_size);
        result->cvalues = new_cvalues;
        result->i_size = m1->i_size;
        result->j_size = m2->j_size;

        return result;
    }

    PyErr_SetString(PyExc_TypeError,
                        "Invalid types");
    return NULL;

}

static MatrixObject * 
Matrix_sub(PyObject* obj1, PyObject* obj2) 
{
    MatrixObject* self;
    if (PyLong_Check(obj1)) {
        self = (MatrixObject*) obj2;
        double value = PyLong_AsDouble(obj1);
        double* new_cvalues = (double *)malloc(sizeof(double )*self->i_size * self->j_size);
        for(int i = 0; i < self->i_size * self->j_size; i++) {
            new_cvalues[i] = self->cvalues[i] - value;
        }

        MatrixObject* result = (MatrixObject*) Py_TYPE(obj2)->tp_new(Py_TYPE(obj2), NULL, NULL);
        result->values = PyList_New(0);
        cast_to_py(&(result->values), new_cvalues, self->i_size, self->j_size);
        result->cvalues = new_cvalues;
        result->i_size = self->i_size;
        result->j_size = self->j_size;

        return result;
    }

    if (PyLong_Check(obj2)) {
        self = (MatrixObject*) obj1;
        double value = PyLong_AsDouble(obj2); 
        double* new_cvalues = (double *)malloc(sizeof(double )*self->i_size * self->j_size);
        for(int i = 0; i < self->i_size * self->j_size; i++) {
            new_cvalues[i] = self->cvalues[i] - value;
        }

        MatrixObject* result = (MatrixObject*) Py_TYPE(obj1)->tp_new(Py_TYPE(obj1), NULL, NULL);
        result->values = PyList_New(0);
        cast_to_py(&(result->values), new_cvalues, self->i_size, self->j_size);
        result->cvalues = new_cvalues;
        result->i_size = self->i_size;
        result->j_size = self->j_size;

        return result;
    }

    if (Py_TYPE(obj1) == Py_TYPE(obj2)) { // matrices multiplication
        MatrixObject* m1 = (MatrixObject*) obj1;
        MatrixObject* m2 = (MatrixObject*) obj2;
        
        if ((m1->i_size != m2->i_size) || (m1->j_size != m2->j_size)) {
            PyErr_SetString(PyExc_TypeError,
                        "Invalid matrixes sizes");
            return NULL;
        }
        double* new_cvalues = (double *)malloc(sizeof(double )*m1->i_size * m2->i_size);

        for(int i = 0; i < m1->i_size * m2->j_size; i++) {
            new_cvalues[i] = m1->cvalues[i] - m2->cvalues[i];
        }
        
        MatrixObject* result = (MatrixObject*) Py_TYPE(obj1)->tp_new(Py_TYPE(obj1), NULL, NULL);
        result->values = PyList_New(0);
        cast_to_py(&(result->values), new_cvalues, m1->i_size, m2->j_size);
        result->cvalues = new_cvalues;
        result->i_size = m1->i_size;
        result->j_size = m2->j_size;

        return result;
    }

    PyErr_SetString(PyExc_TypeError,
                        "Invalid types");
    return NULL;

}

static MatrixObject * 
Matrix_div(PyObject* obj1, PyObject* obj2) 
{
    MatrixObject* self;
    if (PyLong_Check(obj1)) {
        self = (MatrixObject*) obj2;
        double value = PyLong_AsDouble(obj1);
        double* new_cvalues = (double *)malloc(sizeof(double )*self->i_size * self->j_size);
        for(int i = 0; i < self->i_size * self->j_size; i++) {
            new_cvalues[i] = self->cvalues[i] / value;
        }

        MatrixObject* result = (MatrixObject*) Py_TYPE(obj2)->tp_new(Py_TYPE(obj2), NULL, NULL);
        result->values = PyList_New(0);
        cast_to_py(&(result->values), new_cvalues, self->i_size, self->j_size);
        result->cvalues = new_cvalues;
        result->i_size = self->i_size;
        result->j_size = self->j_size;

        return result;
    }

    if (PyLong_Check(obj2)) {
        self = (MatrixObject*) obj1;
        double value = PyLong_AsDouble(obj2); 
        double* new_cvalues = (double *)malloc(sizeof(double )*self->i_size * self->j_size);
        for(int i = 0; i < self->i_size * self->j_size; i++) {
            new_cvalues[i] = self->cvalues[i] / value;
        }

        MatrixObject* result = (MatrixObject*) Py_TYPE(obj1)->tp_new(Py_TYPE(obj1), NULL, NULL);
        result->values = PyList_New(0);
        cast_to_py(&(result->values), new_cvalues, self->i_size, self->j_size);
        result->cvalues = new_cvalues;
        result->i_size = self->i_size;
        result->j_size = self->j_size;

        return result;
    }
    PyErr_SetString(PyExc_TypeError,
                        "Invalid types");
    return NULL;

}

static PyNumberMethods Matrix_num_methods = {
    .nb_multiply = (binaryfunc)Matrix_mul,
    .nb_add = (binaryfunc)Matrix_add,
    .nb_subtract = (binaryfunc)Matrix_sub,
    .nb_true_divide = (binaryfunc)Matrix_div,
};

static PyTypeObject MatrixType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "matrix.Matrix",
    .tp_doc = "Matrix objects",
    .tp_basicsize = sizeof(MatrixObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Matrix_new,
    .tp_init = (initproc) Matrix_init,
    .tp_dealloc = (destructor) Matrix_dealloc,
    .tp_members = Matrix_members,
    .tp_methods = Matrix_methods,
    .tp_as_mapping = &Matrix_mapping,
    .tp_as_number = &Matrix_num_methods,
    .tp_getset = Matrix_getsetters,
    .tp_repr = (reprfunc) Matrix_repr,
    .tp_str = (reprfunc) Matrix_str,
};

static PyModuleDef matrixmodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "matrix",
    .m_doc = "Simple matrix operations.",
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit_matrix(void)
{
    PyObject *m;
    if (PyType_Ready(&MatrixType) < 0)
        return NULL;

    m = PyModule_Create(&matrixmodule);
    if (m == NULL)
        return NULL;

    Py_INCREF(&MatrixType);
    if (PyModule_AddObject(m, "Matrix", (PyObject *) &MatrixType) < 0) {
        Py_DECREF(&MatrixType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}