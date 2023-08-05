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


static PyObject *calcShannonEntropy(PyObject *self, PyObject *args,
                                    PyObject *kwargs) {

    PyArrayObject *msa;
    int ambiguity = 1, omitgaps = 0;
    
    static char *kwlist[] = {"msa", "ambiguity", "omitgaps", NULL};
        
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|ii", kwlist,
                                     &msa, &ambiguity, &omitgaps))
        return NULL;
    
    /*if (!PyDataType_ISINTEGER(msa)) {
        PyErr_SetString(PyExc_TypeError, "msa.dtype must be integer");
        return NULL;
    } */
    
    /* make sure to have a contiguous and well-behaved array */
    msa = PyArray_GETCONTIGUOUS(msa); 

    long numseq = msa->dimensions[0], lenseq = msa->dimensions[1];
       
    double *ent = malloc(lenseq * sizeof(double));
    if (!ent)
        return PyErr_NoMemory();
        
    char *seq = (char *) PyArray_DATA(msa);

    /* start here */
    long size = numseq * lenseq; 
    double count[128]; /* number of ASCII characters*/
    double shannon = 0, probability = 0, numgap = 0, denom = numseq;
    long i = 0, j = 0;
    
    double ambiguous = 0;
    int twenty[20] = {65, 67, 68, 69, 70, 71, 72, 73, 75, 76, 
                      77, 78, 80, 81, 82, 83, 84, 86, 87, 89};
    for (i = 0; i < lenseq; i++)
        ent[j] = 0;
    for (i = 0; i < lenseq; i++) {

        /* zero counters */
        for (j = 65; j < 91; j++)
            count[j] = 0;
        for (j = 97; j < 123; j++)
            count[j] = 0;
        
        /* count characters in a column*/
        for (j = i; j < size; j += lenseq)
            count[(int) seq[j]]++;
        for (j = 65; j < 91; j++)
            count[j] += count[j + 32];
        
        /* handle ambiguous amino acids */
        if (ambiguity) {
            if (count[66]) {
                ambiguous = count[66] / 2.; /* B */
                count[66] = 0;
                count[68] += ambiguous; /* D */
                count[78] += ambiguous; /* N */
            }
            if (count[90]) {
                ambiguous = count[90] / 2.; /* Z */
                count[90] = 0;
                count[69] += ambiguous; /* E */
                count[81] += ambiguous; /* Q */
            }
            if (count[74]) {
                ambiguous = count[74] / 2.; /* J */
                count[74] = 0;
                count[73] += ambiguous; /* I */
                count[76] += ambiguous; /* L */
            }
            if (count[88]) {
                ambiguous = count[88] / 20.; /* X */
                count[88] = 0;
                for (j = 0; j < 20; j++)
                    count[twenty[j]] += ambiguous;
            }
        }
        /* non-gap counts */
        numgap = numseq;
        for (j = 65; j < 91; j++)
            numgap -= count[j];
        
        shannon = 0;
        denom = numseq;
        if (omitgaps)
            denom = numseq - numgap;
        else if (numgap > 0) {
            probability = numgap / numseq;
            shannon += probability * log(probability);
        }

        for (j = 65; j < 91; j++) {
            if (count[j] > 0) {
                probability = count[j] / denom;
                shannon += probability * log(probability);
            }
        }
        ent[i] = -shannon;
    }
    npy_intp dims[1] = {lenseq};
    PyObject *entropy = PyArray_SimpleNewFromData(1, dims, NPY_DOUBLE, ent);
    PyObject *result = Py_BuildValue("O", entropy);
    Py_DECREF(entropy);
    return result;
}


static void sortJoint(double **joint) {
    
    /* Sort probability of ambiguous amino acids. */
    
    int k, l, t;
    double *jrow, jp, *krow;
    
    /* X */
    jrow = joint[24];
    /* XX */ 
    jp = jrow[24];
    if (jp > 0) {
        jp = jp / 400;
        for (k = 0; k < 20; k++) {
            t = twenty[k];
            krow = joint[t];
            for (l = 0; l < 20; l++)
                joint[t][twenty[l]] += jp;
        }
        jrow[24] = 0;
    }
    /* XB */ 
    jp = jrow[2]; 
    if (jp > 0) {
        jp = jp / 40;
        for (k = 0; k < 20; k++) {
            krow = joint[twenty[k]];
            krow[4] += jp; 
            krow[14] += jp;
        }    
        jrow[2] = 0;
    }
    /* XJ */ 
    jp = jrow[10]; 
    if (jp > 0) {
        jp = jp / 40;
        for (k = 0; k < 20; k++) {
            krow = joint[twenty[k]];
            krow[9] += jp; 
            krow[12] += jp;
        }    
        jrow[10] = 0;
    }
    /* XZ */ 
    jp = jrow[26]; 
    if (jp > 0) {
        jp = jp / 40;
        for (k = 0; k < 20; k++) {
            krow = joint[twenty[k]];
            krow[5] += jp; 
            krow[17] += jp;
        }    
        jrow[26] = 0;
    }

    /* B */
    jrow = joint[2];
    /* BB */ 
    jp = jrow[2];
    if (jp > 0) {
        jp = jp / 4;
        joint[4][4] += jp; 
        joint[4][14] += jp;
        joint[14][4] += jp; 
        joint[14][14] += jp;
        jrow[2] = 0;
    }    
    /* BX */ 
    jp = jrow[24]; 
    if (jp > 0) {
        jp = jp / 40;
        for (k = 0; k < 20; k++) {
            t = twenty[k];
            joint[4][t] += jp; 
            joint[14][t] += jp;
        }    
        jrow[24] = 0;
    }
    /* BJ */  
    jp = jrow[10]; 
    if (jp > 0) {
        jp = jp / 4;
        joint[4][9] += jp;
        joint[4][12] += jp; 
        joint[14][9] += jp;
        joint[14][12] += jp;
        jrow[10] = 0;
    }    
    /* BZ */
    jp = jrow[26]; 
    if (jp > 0) {
        jp = jp / 4;
        joint[4][5] += jp;
        joint[4][17] += jp; 
        joint[14][5] += jp; 
        joint[14][17] += jp;
        jrow[26] = 0;
    }  
    
    /* Z */
    jrow = joint[26];
    /* ZZ */ 
    jp = jrow[26];
    if (jp > 0) {
        jp = jp / 4;
        joint[5][5] += jp;
        joint[5][17] += jp;
        joint[17][5] += jp;
        joint[17][17] += jp;
        jrow[26] = 0;
    }
    /* ZX */ 
    jp = jrow[24]; 
    if (jp > 0) {
        jp = jp / 40;
        for (k = 0; k < 20; k++) {
            t = twenty[k];
            joint[5][t] += jp; 
            joint[17][t] += jp;
        }    
        jrow[24] = 0;
    }
    /* ZJ */  
    jp = jrow[10]; 
    if (jp > 0) {
        jp = jp / 4;
        joint[5][9] += jp; 
        joint[5][12] += jp;
        joint[17][9] += jp;
        joint[17][12] += jp;
        jrow[10] = 0;
    }    
    /* ZB */
    jp = jrow[2]; 
    if (jp > 0) {
        jp = jp / 4;
        joint[5][4] += jp; 
        joint[5][14] += jp;
        joint[17][4] += jp;
        joint[17][14] += jp;
        jrow[2] = 0;
    }  
    
    /* J */
    jrow = joint[10];
    /* JJ */
    jp = jrow[10]; 
    if (jp > 0) {
        jp = jp / 4;
        joint[9][9] += jp;
        joint[9][12] += jp; 
        joint[12][9] += jp;
        joint[12][12] += jp;
        joint[10][10] = 0;
    }
    /* JX */ 
    jp = jrow[24]; 
    if (jp > 0) {
        jp = jp / 40;
        for (k = 0; k < 20; k++) {
            t = twenty[k];
            joint[9][t] += jp; 
            joint[12][t] += jp;
        }    
        jrow[24] = 0;
    }
    /* JB */
    jp = jrow[2]; 
    if (jp > 0) {
        jp = jp / 4;
        joint[9][4] += jp; 
        joint[9][14] += jp;
        joint[12][4] += jp;
        joint[12][14] += jp;
        jrow[2] = 0;
    }
    /* BZ */
    jp = jrow[26]; 
    if (jp > 0) {
        jp = jp / 4;
        joint[9][5] += jp; 
        joint[9][17] += jp;
        joint[12][5] += jp;
        joint[12][17] += jp;
        jrow[26] = 0;
    }  
    
    /*for (k = 0; k < NUMCHARS; k++) {*/
    for (t = 0; t < 23; t++) {
        k = unambiguous[t];
        jrow = joint[k]; 
        
        /* B */
        jp = jrow[2];   
        if (jp > 0) {
            jp = jp / 2; 
            jrow[4] += jp; 
            jrow[14] += jp;
            jrow[2] = 0;
        }
        jp = joint[2][k]; 
        if (jp > 0) {
            jp  = jp / 2;
            joint[4][k] += jp; 
            joint[14][k] += jp;
            joint[2][k] = 0;
        }
        
        /* J */
        jp = jrow[10];  
        if (jp > 0) {
            jp  = jp / 2;
            jrow[9] += jp; 
            jrow[12] += jp;
            jrow[10] = 0;
        }
        jp = joint[10][k]; 
        if (jp > 0) {
            jp = jp / 2;
            joint[9][k] += jp; 
            joint[12][k] += jp;
            joint[10][k] = 0;
        }
        
        /* Z */
        jp = jrow[26];  
        if (jp > 0) {
            jp = jp / 2;
            jrow[5] += jp;
            jrow[17] += jp;
            jrow[26] = 0;
        }
        jp = joint[26][k]; 
        if (jp > 0) {
            jp = jp / 2;
            joint[5][k] += jp; 
            joint[17][k] += jp;
            joint[26][k] = 0;
        }
        
        /* X */
        jp = jrow[24];  
        if (jp > 0) {
            jp = jp / 20.;
            for (l = 0; l < 20; l++)
                jrow[twenty[l]] += jp;    
            jrow[24] = 0;
        }
        jp = joint[24][k]; 
        if (jp > 0) {
            jp = jp / 20.;
            for (l = 0; l < 20; l++)
                joint[twenty[l]][k] += jp;    
            joint[24][k] = 0;
        }
    }
    
}


static void zeroJoint(double **joint) {

    /* Fill NUMCHARSxNUMCHARS joint array with zeros. */
    
    int k, l;
    double *jrow;        
    for (k = 0; k < NUMCHARS; k++) {
        jrow = joint[k];
        for (l = 0; l < NUMCHARS; l++)
            jrow[l] = 0;
    }
}


static double calcMI(double **joint, double **probs, long i, long j, int dbg) {

    /* Calculate mutual information for a pair of columns in MSA. */
    
    int k, l;
    double *jrow, *iprb = probs[i], *jprb = probs[j], jp, mi = 0, inside;
    /*double isum = 0, jsum = 0, sum = 0;*/
    for (k = 0; k < NUMCHARS; k++) {
        jrow = joint[k];
        /*isum += iprb[k];
        jsum += jprb[k];*/
        for (l = 0; l < NUMCHARS; l++) {
            jp = jrow[l];
            /*sum += jp;*/
            if (jp > 0) {
                inside = jp / iprb[k] / jprb[l];
                if (inside != 1)
                    mi += jp * log(inside);
            }
            /*if (dbg && jp > 0)
                printf("(%li,%li) %c%c %.4f / %.4f / %.4f\n", 
                        i, j, (char)k+64, (char)l+64, jp, iprb[k], jprb[l]);*/
        }
    }
    /*if (dbg)
        if (sum != 1.00000 || isum != 1.00000 || jsum != 1.00000)
            printf("(%li,%li) %f/%f/%f\n", i, j, sum, isum, jsum);*/
    return mi;
}

static double jointEntropy(double **joint){
    
    double ent = 0.0, prob;
    double *row;
    int i, j;
    for (i = 0; i < NUMCHARS; i++) {
        row = joint[i];
        for (j = 0; j < NUMCHARS; j++) {
            prob = row[j];
            if (prob)
                ent -= prob * log(prob); 
        }   
    }
    return ent;   
}


static void printJoint(double **joint, long k, long l) {

    /* Print joint probability matrix for debugging purposes. */

    int i, j;
    double csum[NUMCHARS], rsum, sum = 0, *row;
    printf("\nJoint probability matrix (%li,%li)\n", k, l);    
    printf("  ");
    for (i = 0; i < NUMCHARS; i++) {
        printf("%c_%-2i ", i + 64, i);
        csum[i] = 0;
    }
    printf("\n");
    for (i = 0; i < NUMCHARS; i++) {
        rsum = 0;
        printf("%c ", i + 64);
        row = joint[i];
        for (j = 0; j < NUMCHARS; j++) {
            printf("%.2f ", row[j]*10);
            rsum += row[j];
            csum[j] += row[j];
            sum += row[j];          
        }
        printf("%.2f\n", rsum * 10);
    }
    printf("+ ");
    for (i = 0; i < NUMCHARS; i++)
        printf("%.2f ", csum[i] * 10);
    printf("%.2f\n", sum);
}


static void printProbs(double **probs, long lenseq) {

    /* Print probability matrix for debugging purposes. */
    
    int i, j;
    double sum;
    double *row;
    printf("\nProbability matrix\n");    
    for (i = 0; i < NUMCHARS; i++)
        printf("%c_%-2i ", i + 64, i);
    printf("SUM\n");
    for (i = 0; i < lenseq; i++) {
        sum = 0;
        row = probs[i];
        for (j = 0; j < NUMCHARS; j++) {
            printf("%.2f ", row[j] * 10);
            sum += row[j];
        }
        printf("%.2f\n", sum);
    }
}


static PyObject *buildMutinfoMatrix(PyObject *self, PyObject *args,
                                    PyObject *kwargs) {

    PyArrayObject *msa;
    int ambiguity = 1, turbo = 1, debug = 0, norm = 0;
    
    static char *kwlist[] = {"msa", "ambiguity", "turbo", "norm", 
                             "debug", NULL};
        
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|iiii", kwlist, &msa, 
                                     &ambiguity, &turbo, &norm, &debug))
        return NULL;

    /* make sure to have a contiguous and well-behaved array */
    msa = PyArray_GETCONTIGUOUS(msa); 

    /* check dimensions */
    long numseq = msa->dimensions[0], lenseq = msa->dimensions[1];
    
    /* get pointers to data */
    char *seq = (char *) PyArray_DATA(msa); /*size: numseq x lenseq */
    

    long i, j;
    /* allocate memory */
    double *mut = malloc(lenseq * lenseq * sizeof(double));
    if (!mut)
        return PyErr_NoMemory();

    unsigned char *iseq = malloc(numseq * sizeof(unsigned char));
    if (!iseq) {
        free(mut);
        return PyErr_NoMemory();
    }
        
    
    /* hold transpose of the sorted character array */
    unsigned char **trans = malloc(lenseq * sizeof(unsigned char *));
    if (!trans) {
        turbo = 0;
    }
    
    if (turbo) {
        /* allocate rows that will store columns of MSA */
        trans[0] = iseq;
        for (i = 1; i < lenseq; i++) {
            trans[i] = malloc(numseq * sizeof(unsigned char));
            if (!trans[i]) {
                for (j = 1; j < i; j++)
                    free(trans[j]);
                free(trans);
                turbo = 0;
            }
        }
    }
    unsigned char *jseq = iseq; /* so that we don't get uninitialized warning*/
    
    /* lenseq*27, a row for each column in the MSA */
    double **probs = malloc(lenseq * sizeof(double *)), *prow;
    if (!probs) {
        free(mut);
        if (turbo)
            for (j = 1; j < lenseq; j++)
                free(trans[j]);
        free(trans);
        free(iseq);
        return PyErr_NoMemory();
    }

    /* 27x27, alphabet characters and a gap*/
    double **joint = malloc(NUMCHARS * sizeof(double *)), *jrow;
    if (!joint) {
        free(mut);
        if (turbo)
            for (j = 1; j < lenseq; j++)
                free(trans[j]);
        free(trans);
        free(iseq);
        free(probs);
        return PyErr_NoMemory();
    }
    
    for (i = 0; i < lenseq; i++) {
        prow = malloc(NUMCHARS * sizeof(double));
        if (!prow) {
            free(mut);
            for (j = 0; j < i; j++)
                free(probs[j]);
            free(probs);
            free(joint);
            if (turbo)
                for (j = 1; j < lenseq; j++)
                    free(trans[j]);
            free(trans);
            free(iseq);
            return PyErr_NoMemory();
        }
        probs[i] = prow; 
        for (j = 0; j < NUMCHARS; j++)
            prow[j] = 0;
    }

    for (i = 0; i < NUMCHARS; i++)  {
        joint[i] = malloc(NUMCHARS * sizeof(double));  
        if (!joint[i]) {
            free(mut);
            for (j = 0; j < i; j++)
                free(joint[j]);
            free(joint);
            for (j = 0; j < lenseq; j++)
                free(probs[j]);
            free(probs);
            if (turbo)
                for (j = 1; j < lenseq; j++)
                    free(trans[j]);
            free(trans);
            free(iseq);
            return PyErr_NoMemory();
        }
    }
    
    if (debug)
        printProbs(probs, lenseq);

    unsigned char a, b;
    long k, l, diff, offset;
    double p_incr = 1. / numseq, prb = 0;
    prow = probs[0];
    
    /* zero mut array */
    for (i = 0; i < lenseq; i++) {
        jrow = mut + i * lenseq;
        for (j = 0; j < lenseq; j++)
            jrow[j] = 0;
    }
    
    i = 0;
    /* calculate first row of MI matrix and all column probabilities */
    for (j = 1; j < lenseq; j++) {
        jrow = probs[j];
        zeroJoint(joint);
        diff = j - 1;
        if (turbo)
            jseq = trans[j]; 
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
                prow[a] += p_incr;
            }
            
            b = (unsigned char) seq[offset + j];
            if (b > 90)
                b -= 96;
            else
                b -= 64;
            if (b < 1 || b > 26)
                b = 0; /* gap character */
            if (turbo)
                jseq[k] = b;
            joint[a][b] += p_incr;
            jrow[b] += p_incr;
        }
        
        if (ambiguity) {

            if (debug)
                printProbs(probs, lenseq);
            if (diff)
                k = j;
            else
                k = 0;
            for (; k <= j; k++) {
                prow = probs[k];
                prb = prow[2];
                if (prb > 0) { /* B -> D, N  */
                    prb = prb / 2.;
                    prow[4] += prb;
                    prow[14] += prb;
                    prow[2] = 0;
                }
                prb = prow[10];
                if (prb > 0) { /* J -> I, L  */
                    prb = prb / 2.;
                    prow[9] += prb; 
                    prow[12] += prb;
                    prow[10] = 0;
                }
                prb = prow[26]; 
                if (prb > 0) { /* Z -> E, Q  */
                    prb = prb / 2.;
                    prow[5] += prb;
                    prow[17] += prb;
                    prow[26] = 0;
                }
                if (prow[24] > 0) { /* X -> 20 AA */
                    prb = prow[24] / 20.; 
                    for (l = 0; l < 20; l++)
                        prow[twenty[l]] += prb;
                    prow[24] = 0;
                }
            }

            if (debug)
                printProbs(probs, lenseq);
            if (debug)
                printJoint(joint, i, j);
            sortJoint(joint);
            if (debug)
                printJoint(joint, i, j);
        }
        if (norm)
            mut[j] = mut[lenseq * j] = calcMI(joint, probs, i, j, debug) / 
                                      jointEntropy(joint);
        else
            mut[j] = mut[lenseq * j] = calcMI(joint, probs, i, j, debug);
    }
    if (debug)
        printProbs(probs, lenseq);
    if (turbo)
        free(iseq);

    
    /* calculate rest of MI matrix */
    long ioffset;
    for (i = 1; i < lenseq; i++) {
        ioffset = i * lenseq;
        if (turbo)
            iseq = trans[i];
            
        for (j = i + 1; j < lenseq; j++) {
            zeroJoint(joint);

            if (turbo) {
                jseq = trans[j];
                for (k = 0; k < numseq; k++)
                    joint[iseq[k]][jseq[k]] += p_incr;
                    
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
                    joint[a][b] += p_incr;
                }
            }
            if (ambiguity)
                sortJoint(joint);
        if (norm)
            mut[ioffset + j] = mut[i + lenseq * j] = 
                calcMI(joint, probs, i, j, debug) / jointEntropy(joint);
        else
            mut[ioffset + j] = mut[i + lenseq * j] = 
                calcMI(joint, probs, i, j, debug);
        }
    }

    /* free memory */
    for (i = 0; i < lenseq; i++){  
        free(probs[i]);
    }  
    free(probs);
    for (i = 0; i < NUMCHARS; i++){  
        free(joint[i]);
    }  
    free(joint);
    if (turbo)
        for (j = 1; j < lenseq; j++)
            free(trans[j]);
    free(trans);

    npy_intp dims[2] = {lenseq, lenseq};
    PyObject *mutinfo = PyArray_SimpleNewFromData(2, dims, NPY_DOUBLE, mut);
    PyObject *result = Py_BuildValue("O", mutinfo);
    Py_DECREF(mutinfo);
    return result;
}

static PyObject *calcMSAOccupancy(PyObject *self, PyObject *args, 
                                  PyObject *kwargs) {

    PyArrayObject *msa;
    int dim;
    int count = 0;

    static char *kwlist[] = {"msa", "dim", "count", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Oi|i", kwlist, 
                                     &msa, &dim, &count))
        return NULL;
    
    long numseq = msa->dimensions[0], lenseq = msa->dimensions[1];
    long *cnt = malloc(msa->dimensions[dim] * sizeof(long));

    if (!cnt)
        return PyErr_NoMemory();
        
    char *seq = (char *) PyArray_DATA(msa), *row, ch;
    
    long i, j, *k;  
    if (dim)
        k = &j;
    else
        k = &i;
    
    for (i = 0; i < msa->dimensions[dim]; i++)
        cnt[i] = 0;

    for (i = 0; i < numseq; i++) {
        row = seq + i * lenseq;
        for (j = 0; j < lenseq; j++) {
            ch = row[j];
            if ((64 < ch && ch < 91) || (96 < ch && ch < 123))
                cnt[*k]++;
        }
    }
    
    npy_intp dims[1] = {msa->dimensions[dim]};
    if (count) {
        return PyArray_SimpleNewFromData(1, dims, NPY_LONG, cnt);       
    } else {
        double divisor;
        if (dim)
            divisor = 1. * numseq;
        else 
            divisor = 1. * lenseq;
        double *occ = malloc(msa->dimensions[dim] * sizeof(double));
        for (i = 0; i < msa->dimensions[dim]; i++)
            occ[i] = cnt[i] / divisor;
        free(cnt);
        return PyArray_SimpleNewFromData(1, dims, NPY_DOUBLE, occ);
    }
}


static PyMethodDef msatools_methods[] = {

    {"calcShannonEntropy",  (PyCFunction)calcShannonEntropy, 
     METH_VARARGS | METH_KEYWORDS, 
     "Calculate information entropy for given character array into given \n"
     "double array."},

    {"buildMutinfoMatrix",  (PyCFunction)buildMutinfoMatrix, 
     METH_VARARGS | METH_KEYWORDS, 
     "Calculate mutual information for given character array into given \n"
     "2D double array, and return True if turbo mode was used."},
     
    {"calcMSAOccupancy",  (PyCFunction)calcMSAOccupancy, 
     METH_VARARGS | METH_KEYWORDS,
     "Return occupancy (or count) array calculated for MSA rows or columns."},

    {NULL, NULL, 0, NULL}
};



#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef msatools = {
        PyModuleDef_HEAD_INIT,
        "msatools",
        "Multiple sequence alignment analysis tools.",
        -1,
        msatools_methods,
};
PyMODINIT_FUNC PyInit_msatools(void) {
    import_array();
    return PyModule_Create(&msatools);
}
#else
PyMODINIT_FUNC initmsatools(void) {

    Py_InitModule3("msatools", msatools_methods,
        "Multiple sequence alignment analysis tools.");
        
    import_array();
}
#endif
