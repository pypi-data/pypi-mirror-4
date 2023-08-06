/* ProDy: A Python Package for Protein Dynamics Analysis
 *
 * Copyright (C) 2010-2012 Ahmet Bakan
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *  
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>
 *
 * Author: Ahmet Bakan
 * Copyright (C) 2010-2012 Ahmet Bakan
 */

#include "Python.h"
#include "numpy/arrayobject.h"
#define NUMCHARS 27
const int twenty[20] = {1, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 
                        14, 16, 17, 18, 19, 20, 22, 23, 25};
const int unambiguous[23] = {0, 1, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 
                             15, 16, 17, 18, 19, 20, 21, 22, 23, 25};
                             
static PyObject *buildMutinfoMatrix(PyObject *self, PyObject *args,
                                    PyObject *kwargs) {

    PyArrayObject *msa;
    int unique = 0, turbo = 1;
    
    static char *kwlist[] = {"msa", "turbo", NULL};
        
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|i", kwlist, &msa, 
                                     &turbo))
        return NULL;

    /* make sure to have a contiguous and well-behaved array */
    msa = PyArray_GETCONTIGUOUS(msa);

    /* get dimensions */
    long numseq = msa->dimensions[0], lenseq = msa->dimensions[1];
    
    /* get pointers to data */
    char *iraw, *jraw, *raw = (char *) PyArray_DATA(msa); /* numseq x lenseq */

    long i, j;
    /* allocate memory */
    
    void *result;
    if (unique) {
        npy_intp dims[1] = {numseq};
        PyObject *simarr = PyArray_SimpleNew(2, dims, NPY_DOUBLE, mut);
        result = (_Bool *) PyArray_DATA(simarr);
    } else {
        npy_intp dims[2] = {numseq, numseq};
        PyObject *simarr = PyArray_SimpleNew(2, dims, NPY_DOUBLE, mut);
        result = (double *) PyArray_DATA(simarr);
    }
    
    _Bool *result = malloc(numseq * sizeof(_Bool));
    double *result = malloc(numseq * numseq * sizeof(double));   
     
    if (!simarr)
        return PyErr_NoMemory();

    /* arrays to store refined sequences*/
    unsigned char *iseq = malloc(lenseq * sizeof(unsigned char));
    if (!iseq) {
        free(result);
        return PyErr_NoMemory();
    }
    
    unsigned char **seq = malloc(lenseq * sizeof(unsigned char *));
    if (!seq) {
            turbo = 0;
    }
    
    if (turbo) {
        /* allocate rows that will store columns of MSA */
        seq[0] = iseq;
        for (i = 1; i < lenseq; i++) {
            seq[i] = malloc(lenseq * sizeof(unsigned char));
            if (!seq[i]) {
                for (j = 1; j < i; j++)
                    free(seq[j]);
                free(seq);
                turbo = 0;
            }
        }
    }
    /* initialize jses, so that we don't get uninitialized warning */
    unsigned char *jseq = iseq; 
    
    unsigned char a, b;
    long k, l, diff;
    
    /* zero result array */
    if (unique) {
        for (i = 0; i < lenseq; i++)
            result[i] = 0;
    } else {   
        for (i = 0; i < lenseq; i++) {
            jrow = result + i * lenseq;
            for (j = 0; j < lenseq; j++)
                jrow[j] = 0;
        }
    }
    
    double length, score; 
    
    /* START calculation */    
    /* calculate first row of MI matrix and all column probabilities */
    i = 0;
    iraw = raw;
    for (j = 1; j < lenseq; j++) {
        length = score = 0;
        jraw = raw + lenseq * j;
        diff = j - 1;
        if (turbo) /* in turbo mode, there is a row for refined sequences */
            jseq = seq[j];
        for (k = 0; k < lenseq; k++) {
            if (diff) {
                a = iseq[k];
            } else {
                a = (unsigned char) iraw[k];
                if (a > 90)
                    a -= 96;
                else
                    a -= 64;
                if (a < 1 || a > 26)
                    a = 0; /* gap character */
                iseq[k] = a;
            }
            
            b = (unsigned char) jraw[k];
            if (b > 90)
                b -= 96;
            else
                b -= 64;
            if (b < 1 || b > 26)
                b = 0; /* gap character */
            if (turbo)  /* we keep the refined chars for all sequences*/
                jseq[k] = b;
            
            if (a || b) {
                length++;
                if (a == b)
                    score++;
            }
        }

        if (unique)
            result[j] = 0;
        else
            if (length)
                result[j] = result[numseq * j] = score / length;
        
    }

    if (turbo)
        free(iseq);
    
    /* calculate rest of identities */
    for (i = 1; i < lenseq; i++) {
        length = score = 0;

        if (turbo)
            iseq = seq[i];
            
        for (j = i + 1; j < lenseq; j++) {

            if (turbo) {
                jseq = seq[j];
                for (k = 0; k < numseq; k++) {
                    a = iseq[k];
                    b = bseq[k];
                    if (a || b) {
                        length++;
                        if (a == b)
                            score++;
                    }
                }
            } else {         
                diff = j - i - 1;
                for (k = 0; k < numseq; k++) {
                    offset = k * lenseq;
                    if (diff) {
                        a = iseq[k];
                    } else {
                        a = (unsigned char) seq[offset + i];
                        if (a > 90)
                            a -= 96;
                        else
                            a -= 64;
                        if (a < 1 || a > 26)
                            a = 0; /* gap character */
                        iseq[k] = a;
                    }
                    
                    b = (unsigned char) seq[offset + j];
                    if (b > 90)
                        b -= 96;
                    else
                        b -= 64;
                    if (b < 1 || b > 26)
                        b = 0; /* gap character */
                }
            }

        if (unique)
            result[j] = 0;
        else
            if (length)
                result[j] = result[numseq * j] = score / length;
    }

    /* free memory */

    if (turbo)
        for (j = 1; j < lenseq; j++)
            free(trans[j]);
    free(trans);

    PyObject *result = Py_BuildValue("O", mutinfo);
    Py_DECREF(mutinfo);
    return result;
}

static PyMethodDef seqtools_methods[] = {

    {"buildSeqidMatrix",  (PyCFunction)buildSeqidMatrix, 
     METH_VARARGS | METH_KEYWORDS, 
     "Return sequence identity matrix calculated for given character \n"
     "array that contains an MSA."},

    {NULL, NULL, 0, NULL}
};



#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef seqtools = {
        PyModuleDef_HEAD_INIT,
        "seqtools",
        "Sequence similarity/identity analysis tools.",
        -1,
        seqtools_methods,
};
PyMODINIT_FUNC PyInit_seqtools(void) {
    import_array();
    return PyModule_Create(&seqtools);
}
#else
PyMODINIT_FUNC initmsatools(void) {

    Py_InitModule3("seqtools", seqtools_methods,
        "Sequence similarity/identity analysis tools.");
        
    import_array();
}
#endif
