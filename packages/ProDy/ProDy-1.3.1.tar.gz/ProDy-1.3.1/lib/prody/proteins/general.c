#include "Python.h"
#include "numpy/arrayobject.h"

int calc_info_entropy(char *seq, double *ent, long numseq, long lenseq);

static PyObject *parseFasta(PyObject *self, PyObject *args) {

    /* Parse sequences from *filename* into the memory pointed by the
       Numpy array passed as Python object.  This function assumes that
       the sequences are aligned, i.e. have same number of lines at equal
       lengths. */

	char *filename;
	PyObject *arrobj;
	PyArrayObject *msa;
	
	if (!PyArg_ParseTuple(args, "sO", &filename, &arrobj))
		return NULL;
	
    msa = (PyArrayObject *) 
        PyArray_ContiguousFromObject(arrobj, PyArray_CHAR, 2, 2);
    if (msa == NULL)
        return NULL;

    long i = 0, lenseq = msa->dimensions[1];
    long lenline = 0, lenlast = 0, numlines = 0; 
    long size = lenseq + 100, iline = 0;
    char line[size];

    FILE *file = fopen(filename, "r");
    while (fgets(line, size, file) != NULL) {
        if (line[0] == '>')
            continue;

        for (i = 0; i < strlen(line); i++)
            if (line[i] == ' ' || line[i] == '\n')
                break;
        lenline = i;
        lenlast = lenseq % lenline;
        numlines = (lenseq - lenlast) / lenline;
        break;
    }
    
    
    fseek(file, 0, SEEK_SET);


    int slash = 0, dash = 0, j = 0;
    long index = 0, ccount = 0;
    char *data = (char *)PyArray_DATA(msa);
    char clabel[size], ckey[size];
	PyObject *labels, *dict, *plabel, *pkey, *pcount;
	labels = PyList_New(0);
    dict = PyDict_New();

    while (fgets(line, size, file) != NULL) {
        iline++;
        if (line[0] != '>')
            continue;
        for (i = 1; i < size; i++)
            if (line[i] != ' ')
                break;
        strcpy(line, line + i);

        /* parse label */
        slash = 0;
        dash = 0;
        for (i = 0; i < size; i++)
            if (line[i] == '\n' || line[i] == ' ') 
                break;
            else if (line[i] == '/' && slash == 0 &&  dash == 0)
                slash = i;
            else if (line[i] == '-' && slash > 0 && dash == 0)
                dash = i;
        
        if (slash > 0 && dash > slash) {
            strncpy(ckey, line, slash);
            strncpy(clabel, line, i);
            
            clabel[i] = '\0';
            ckey[slash] = '\0';
            pkey = PyString_FromString(ckey);
            plabel = PyString_FromString(clabel);
            pcount = PyInt_FromLong(ccount);
            if (plabel == NULL || pcount == NULL ||
                PyList_Append(labels, plabel) < 0 ||
                PyDict_SetItem(dict, pkey, pcount)) {
                PyErr_SetString(PyExc_IOError, 
                                "failed to parse msa, at line");
                Py_DECREF(arrobj);
                Py_XDECREF(pcount);
                Py_XDECREF(plabel);
                Py_XDECREF(pkey);
                return NULL;
            }
            Py_DECREF(pkey);
            Py_DECREF(plabel);
            Py_DECREF(pcount); 
        } else {
            strncpy(clabel, line, i);
            clabel[i] = '\0';
            plabel = PyString_FromString(clabel);
            pcount = PyInt_FromLong(ccount);
            if (plabel == NULL || pcount == NULL ||
                PyList_Append(labels, plabel) < 0 ||
                PyDict_SetItem(dict, plabel, pcount)) {
                PyErr_SetString(PyExc_IOError, 
                                "failed to parse msa, at line");
                Py_DECREF(arrobj);
                Py_XDECREF(pcount);
                Py_XDECREF(plabel);
                return NULL;
            }
            Py_DECREF(plabel);
            Py_DECREF(pcount);
         }

        
        /* parse sequence */
        
        for (i = 0; i < numlines; i++) {
            if (fgets(line, size, file) == NULL) {
                PyErr_SetString(PyExc_IOError, 
                                "failed to parse msa, at line");
                Py_DECREF(arrobj);
                return NULL;
            }
            for (j = 0; j < lenline; j++)
                data[index++] = line[j];
        }
        
        if (lenlast) {
            if (fgets(line, size, file) == NULL) {
                PyErr_SetString(PyExc_IOError, 
                                "failed to parse msa, at line");
                Py_DECREF(arrobj);
                return NULL;
            }
            for (j = 0; j < lenlast; j++)
                data[index++] = line[j];
        }
        ccount++;
    }

    fclose(file);
    Py_XDECREF(arrobj);
	return Py_BuildValue("(OO)", labels, dict);
}


static PyObject *parseSelex(PyObject *self, PyObject *args) {

    /* Parse sequences from *filename* into the the memory pointed by the
       Numpy array passed as Python object.  This function assumes that
       the sequences are aligned, i.e. start and end at the same column. */

	char *filename;
	PyObject *arrobj;
	PyArrayObject *msa;
	
	if (!PyArg_ParseTuple(args, "sO", &filename, &arrobj))
		return NULL;

    msa = (PyArrayObject *) 
        PyArray_ContiguousFromObject(arrobj, PyArray_CHAR, 2, 2);
    if (msa == NULL)
        return NULL;

    long i = 0, beg = 0, end = 0, lenseq = msa->dimensions[1]; 
    long size = lenseq + 100, iline = 0;
    char line[size];

    FILE *file = fopen(filename, "r");
    while (fgets(line, size, file) != NULL) {
        iline++;
        if (line[0] == '#' || line[0] == '/' || line[0] == '%')
            continue;

        for (i = 0; i < size; i++)
            if (line[i] == ' ')
                break;
        for (; i < size; i++)
            if (line[i] != ' ')
                break;
        beg = i;
        end = beg + lenseq;
        break;
    }
    iline--;
    fseek(file, - strlen(line), SEEK_CUR);

    int slash = 0, dash = 0;
    long index = 0, ccount = 0;
    char *data = (char *)PyArray_DATA(msa);
    char clabel[beg], ckey[beg];
	PyObject *labels, *dict, *plabel, *pkey, *pcount;
	labels = PyList_New(0);
    dict = PyDict_New();

    int space = beg - 1; /* index of space character before sequence */
    while (fgets(line, size, file) != NULL) {
        iline++;
        if (line[0] == '#' || line[0] == '/' || line[0] == '%')
            continue;
            
        if (line[space] != ' ') {
            PyErr_SetString(PyExc_IOError, 
                            "failed to parse msa, at line");
            return NULL;
        } 

        /* parse label */
        
        slash = 0;
        dash = 0;
        for (i = 0; i < size; i++)
            if (line[i] == ' ') 
                break;
            else if (line[i] == '/' && slash == 0 &&  dash == 0)
                slash = i;
            else if (line[i] == '-' && slash > 0 && dash == 0)
                dash = i;
        if (slash > 0 && dash > slash) {
            strncpy(ckey, line, slash);
            strncpy(clabel, line, i);
            clabel[i] = '\0';
            ckey[slash] = '\0';
            pkey = PyString_FromString(ckey);
            plabel = PyString_FromString(clabel);
            pcount = PyInt_FromLong(ccount);
            if (plabel == NULL || pcount == NULL ||
                PyList_Append(labels, plabel) < 0 ||
                PyDict_SetItem(dict, pkey, pcount)) {
                PyErr_SetString(PyExc_IOError, 
                                "failed to parse msa, at line");
                Py_DECREF(arrobj);
                Py_XDECREF(pcount);
                Py_XDECREF(plabel);
                Py_XDECREF(pkey);
                return NULL;
            }
            Py_DECREF(pkey);
            Py_DECREF(plabel);
            Py_DECREF(pcount);            
        } else {
            strncpy(clabel, line, i);
            clabel[i] = '\0';
            plabel = PyString_FromString(clabel);
            pcount = PyInt_FromLong(ccount);
            if (plabel == NULL || pcount == NULL ||
                PyList_Append(labels, plabel) < 0 ||
                PyDict_SetItem(dict, plabel, pcount)) {
                PyErr_SetString(PyExc_IOError, 
                                "failed to parse msa, at line");
                Py_DECREF(arrobj);
                Py_XDECREF(pcount);
                Py_XDECREF(plabel);
                return NULL;
            }
            Py_DECREF(plabel);
            Py_DECREF(pcount);
         }
        
        /* parse sequence */
        for (i = beg; i < end; i++)
            data[index++] = line[i];
        ccount++;
    }
    fclose(file);
    Py_XDECREF(arrobj);
	return Py_BuildValue("(OO)", labels, dict);
}


static PyObject *calcInfoEntropy(PyObject *self, PyObject *args) {

	PyObject *arrobj, *result;
	PyArrayObject *msa, *entropy;
	
	if (!PyArg_ParseTuple(args, "OO", &arrobj, &result))
		return NULL;
    
    msa = (PyArrayObject *) 
        PyArray_ContiguousFromObject(arrobj, PyArray_CHAR, 2, 2);
    if (msa == NULL)
        return NULL;
    
    entropy = (PyArrayObject *) 
        PyArray_ContiguousFromObject(result, PyArray_DOUBLE, 1, 1);
    if (entropy == NULL)
        return NULL;

    long numseq = msa->dimensions[0], lenseq = msa->dimensions[1];
    long lenent = entropy->dimensions[0];
    
    if (lenent != lenseq) {
        Py_XDECREF(arrobj);
        Py_XDECREF(result);
        PyErr_SetString(PyExc_IOError, 
                        "msa and entropy array shapes do not match");
        return NULL;
    }
    
    char *seq = (char *)PyArray_DATA(msa);
    double *ent = (double *)PyArray_DATA(entropy);

/*  Given a MSA matrix (all_seq), along with the length of the sequences 
    (lenseq, the number of columns of the matrix) and the number of sequences
    (numseq, the number of lines in the matrix), this function calculates the
    Shannon entropy of each position in the sequence. This function calls the
    CalcProbAmino function. 
*/
    double calc_info_entropy(char *all_seq,double *ent,long numseq,long lenseq)
    {
        int i=0,j=0,k=0;
        long size;
        double prob=0, S=0;
        char *one_seq;
        char amino[20]="GAVILFPMWCSTNQYHDEKR";
        char amino1, tmp[10];

/* Handle input arguments: */
        strcpy(tmp,argv[3]);
        numseq = atof(tmp);
        strcpy(tmp,argv[4]);
        lenseq = atof(tmp);


/* Allocate memory for the all_seq, one_seq and ent vectors: */
        size = numseq*lenseq;
        all_seq = (char *) malloc((size)*sizeof(char));
        one_seq = (char *) malloc((numseq)*sizeof(char));
        ent = (double *) malloc((lenseq)*sizeof(double));

/* In case of memory allocation failure, exit: */
        if (all_seq == NULL){ 
            printf ("Error: Can't allocate memory for all_seq.\n");
            exit(5);
        }
        if (one_seq == NULL){ 
            printf ("Error: Can't allocate memory for one_seq.\n");
            exit(5);
        }
        if (ent == NULL){ 
            printf ("Error: Can't allocate memory for ent.\n");
        exit(5);
        }

/* Initialize vectors all_seq and one_seq: */
        for (i=0;i<size;i++)
            all_seq[i]=0;
        for (i=0;i<numseq;i++)
            one_seq[i]=0;
        for (i=0;i<lenseq;i++)
            ent[i]=0;

/* Calculate probability of each aminoacid in each location of a sequence.
   Read one column at a time, write it to the one_seq vector, 
   and calculate the probability of occurrence (in that column)
   of each of the 20 aminoacids; repeat for all columns: */
        for ( j=0; j<lenseq; j++) {
            S=0;
            for ( i=0; i<numseq; i++) 
                one_seq[i]=all_seq[lenseq*i+j];
            for ( k=0; k<20; k++ ) {
                amino1=amino[k];
                prob = CalcProbAmino(one_seq,numseq,amino1);
                S = S + prob * log(prob);
            }

/* Write entropy vector: the i^th element of the vector represents 
   the information entropy (amino-acid variability) of the i^th 
   element in the sequence: */
            ent[j]=-S;
        }

/* Free memory: */
        free( all_seq );
        free( one_seq );
        return(0);
    }

/*  Given a vector (one_seq) containing the amino-acids found in a certain 
    location of a sequence, the length of such vector (numseq), and a specific
    amino-acid (amino), this function calculates the probability of finding
    that amino-acid in that location. This is used to calculate the Shannon 
    entropy of a given sequence location. 
*/
    double CalcProbAmino(char *one_seq, long numseq, char amino)
    {
        int i=0;
        float count=0;
        double prob=0;
        while ( i < numseq ) {
/*  if both sequences have the appropriate aminoacid, assign a count of 1;
    if one has the right one and the other a gap (- or .), assign 1/20=0.05;
    if both have a gap, assign 1/20*1/20 = 0.0025: */
            if ( toupper(seq_one[i]) == amino1 ) {
                if ( toupper(seq_two[i]) == amino2 ) 
                    count=count+1;
                else if ( toupper(seq_two[i]) == 45 || toupper(seq_two[i]) == 46 )
                    count=count+0.05;
            }
            if ( toupper(seq_one[i]) == 45 || toupper(seq_one[i]) == 46 ) {
                if ( toupper(seq_two[i]) == amino2 ) 
                    count=count+0.05;
                else if ( toupper(seq_two[i]) == 45 || toupper(seq_two[i]) == 46 )
                    count=count+0.0025;
            }
            i=i+1;
        }

        prob=count/i;

/*  If prob_pair (call it x) is zero, we wo't be able to take its log; it's 
    going to be nan. But since the formula is ~ x ln x, we can assign a very
    small value to x when it is zero. In that case, we'll have x ln x, which
    goes to zero as x --> 0, as we want. */

        if ( prob == 0 )
            prob = 1E-50;

        return(prob);
    }

    Py_XDECREF(arrobj);
    Py_XDECREF(result);
    return Py_BuildValue("");

}

int calc_info_entropy(char *seq, double *ent, long numseq, long lenseq) {
    
    /* seq has length numseq * lenseq
       ent has length lenseq
    */
    

    return 0;
}

static PyObject *calcMutualInfo(PyObject *self, PyObject *args) {

	PyObject *arrobj, *result;
	PyArrayObject *msa, *mutualinfo;
	
	if (!PyArg_ParseTuple(args, "OO", &arrobj, &result))
		return NULL;
    
    msa = (PyArrayObject *) 
        PyArray_ContiguousFromObject(arrobj, PyArray_CHAR, 2, 2);
    if (msa == NULL)
        return NULL;
    
    mutualinfo = (PyArrayObject *) 
        PyArray_ContiguousFromObject(result, PyArray_DOUBLE, 2, 2);
    if (mutualinfo == NULL)
        return NULL;

    long numseq = msa->dimensions[0], lenseq = msa->dimensions[1];
    long lenmutual = mutualinfo->dimensions[0];
    long lenmutual2 = mutualinfo->dimensions[1];
    
    if (lenmutual != lenseq || lenmutual2 != lenseq) {
        Py_XDECREF(arrobj);
        Py_XDECREF(result);
        PyErr_SetString(PyExc_IOError, 
                        "msa and mutualinfo array shapes do not match");
        return NULL;
    }
    
    char *seq = (char *)PyArray_DATA(msa);
    double *mutual = (double *)PyArray_DATA(mutualinfo);

////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
    int calc_mutual_info(char *seq,double *mutual,long numseq,long lenseq) {
    {
        int i=0,j=0,jp=0,k=0,kp=0;
        long lenseq2=0, size=0;
        double prob_1=0, prob_2=0, prob_12=0, S=0;
        double *mutual_apc, *mutual_ave;
        double mutual_total_ave=0;
        char *all_seq, *seq_one, *seq_two;
        char amino[20]="GAVILFPMWCSTNQYHDEKR";
        char amino1, amino2;
        char tmp[100];

/* Allocate memory for all_seq, seq_one, seq_two and mutual arrays: */
        size = numseq*lenseq;
        lenseq2=lenseq*lenseq;
        all_seq = (char *) malloc((size)*sizeof(char));
        seq_one = (char *) malloc((numseq)*sizeof(char));
        seq_two = (char *) malloc((numseq)*sizeof(char));
        mutual = (double *) malloc((lenseq2)*sizeof(double));
        mutual_apc = (double *) malloc((lenseq2)*sizeof(double));
        mutual_ave = (double *) malloc((lenseq)*sizeof(double));

/* In case of memory allocation failure, exit: */
        if (all_seq == NULL){	
            printf ("Error: Can't allocate memory for all_seq\n");
            exit(5);
        }
        if (seq_one == NULL){
            printf ("Error: Can't allocate memory for seq_one\n");
            exit(5);
        }
        if (seq_two == NULL){
            printf ("Error: Can't allocate memory for seq_two\n");
            exit(5);
        }
        if (mutual == NULL){
            printf ("Error: Can't allocate memory for mutual\n");
            exit(5);
        }
        if (mutual_apc == NULL){
            printf ("Error: Can't allocate memory for mutual_apc\n");
            exit(5);
        }
        if (mutual_ave == NULL){
            printf ("Error: Can't allocate memory for mutual_ave\n");
            exit(5);
        }

/* Initialize arrays: */
        for (i=0;i<size;i++) {
            all_seq[i]=0;
        }
        for (i=0;i<lenseq2;i++) {
            mutual[i]=0;
            mutual_apc[i]=0;
        }   
        for (i=0;i<numseq;i++) {
            seq_one[i]=0;
            seq_two[i]=0;
        }
        for (i=0;i<lenseq;i++) {
            mutual_ave[i]=0;
        }

/* Calculate probability of each aminoacid in each location of a sequence 
and probability of each pair of aminoacids in each pair of location. These 
values are needed for the mutual information matrix. Read a pair of columns 
at a time, writing them to seq_one and seq_two vectors, and then calculate 
the mentioned probabilities. Notice that mutual(i,j) = mutual(j,i) -it's a 
symmetric matrix and we don't care about the diagonal values; in fact, we'll 
do only the upper-right part of the matrix: */
        for ( j=0; j<(lenseq-1); j++) {
            for ( jp=(j+1); jp<lenseq; jp++) {
                for ( i=0; i<numseq; i++) {
                    seq_one[i]=all_seq[lenseq*i+j];
                    seq_two[i]=all_seq[lenseq*i+jp];
                }
                for ( k=0; k<20; k++ ) {
                    amino1=amino[k];
                    for ( kp=0; kp<20; kp++ ) {
                        amino2=amino[kp];
/* Probability of finding amino[k]  in location j  of sequence: */
                        prob_1 = CalcProbAmino(seq_one,numseq,amino1);
/* Probability of finding amino[kp] in location jp of sequence: */
                        prob_2 = CalcProbAmino(seq_two,numseq,amino2);
/* Probability of finding amino[k] and amino[kp] in locations j and jp of sequence: */
                        prob_12 = CalcProbPairAmino(seq_one,seq_two,numseq,amino1,amino2); 

                        mutual[lenseq*j+jp] = mutual[lenseq*j+jp] + prob_12 * log( prob_12/(prob_1*prob_2) );
                    }
                }
            }
        }

/* Complete the lower-left part of the matrix by symmetrization: */
        for ( j=1; j<lenseq; j++) {
            for ( jp=0; jp<j; jp++) {
                mutual[lenseq*j+jp] = mutual[lenseq*jp+j];
            }
        }

/* Add correction to remove shared ancenstry - Calculate <mutual(j)> (average
of jth column) and <mutual> (average of all elements), as needed for the 
Average Product Correction (APC): */
        for ( j=0; j<lenseq; j++) {
            for ( jp=0; jp<lenseq; jp++) {
/* Add up the elements of the line, <mutual(j)>: */
                mutual_ave[j] = mutual_ave[j] + mutual[lenseq*j+jp]; 
            }
/* Add up all the elements of all the lines, <mutual>: */
            mutual_total_ave = mutual_total_ave + mutual_ave[j];  
/* The -1 below is because we don't want to count the diagonal element: */
            mutual_ave[j] = mutual_ave[j] / (lenseq - 1);
        }
        mutual_total_ave = mutual_total_ave / (lenseq*(lenseq-1));

/* Finally, apply the correction to the upper-right part of the matrix: */
        for ( j=0; j<(lenseq-1); j++) {
            for ( jp=(j+1); jp<lenseq; jp++) {
                mutual_apc[lenseq*j+jp] = mutual[lenseq*j+jp] - mutual_ave[j] * mutual_ave[jp] / mutual_total_ave;
            }
        }

/* Complete the lower-left part of the matrix by symmetrization: */
        for ( j=1; j<lenseq; j++) {
            for ( jp=0; jp<j; jp++) {
                mutual_apc[lenseq*j+jp] = mutual_apc[lenseq*jp+j];
            }
        }

/* Free memory: */
        free(all_seq);
        free(seq_one);
        free(seq_two);
        free(mutual);
        free(mutual_apc);
        free(mutual_ave);
        return(0);
    }

/*  Given a vector (one_seq) containing the amino-acids found in a certain 
    location of a sequence, the length of such vector (numseq), and a specific
    amino-acid (amino), this function calculates the probability of finding
    that amino-acid in that location. This is used to calculate the mutual
    information of a given pair of sequence locations. 
*/
    double CalcProbAmino(char *seq, long numseq, char amino)
    {
        int i=0;
        float count=0;
        double prob=0;
        while ( i < numseq ) {
/*  if both sequences have the appropriate aminoacid, assign a count of 1;
    if one has the right one and the other a gap (- or .), assign 1/20=0.05;
    if both have a gap, assign 1/20*1/20 = 0.0025: */
            if ( toupper(seq_one[i]) == amino1 ) {
                if ( toupper(seq_two[i]) == amino2 ) 
                    count=count+1;
                else if ( toupper(seq_two[i]) == 45 || toupper(seq_two[i]) == 46 )
                    count=count+0.05;
            }
            if ( toupper(seq_one[i]) == 45 || toupper(seq_one[i]) == 46 ) {
                if ( toupper(seq_two[i]) == amino2 ) 
                    count=count+0.05;
                else if ( toupper(seq_two[i]) == 45 || toupper(seq_two[i]) == 46 )
                    count=count+0.0025;
            }
            i=i+1;
        }

        prob=count/i;

/*  If prob_pair (call it x) is zero, we wo't be able to take its log; it's 
    going to be nan. But since the formula is ~ x ln x, we can assign a very
    small value to x when it is zero. In that case, we'll have x ln x, which
    goes to zero as x --> 0, as we want. */
        if ( prob == 0 )
            prob = 1E-50;

        return(prob);
    }

/*  Given two vectors (seq_one and seq_two) containing each the aminoacids 
    found in two certain locations of a MSA, the length of those vectors 
    (numseq) and two specific aminoacids (amino1 and amino2), this function 
    calculates the probability of finding those two aminoacids in the pair 
    of locations represented by the two vectors. This is needed to calculate 
    the mutual information of a given pair of sequence locations.
*/
    double CalcProbPairAmino(char *seq_one,char *seq_two,long numseq,char amino1,char amino2)
    {
        int i=0;
        double count=0, prob_pair=0;
        while ( i < numseq ) {
/*  if both sequences have the appropriate aminoacid, assign a count of 1;
    if one has the correct one and the other a gap (- or .), assign 1/20=0.05;
    if both have a gap, assign 1/20*1/20 = 0.0025: */
            if ( seq_one[i] == amino1 ) {
                if ( seq_two[i] == amino2 ) 
                    count=count+1;
                else if ( seq_two[i] == 45 || seq_two[i] == 46 )
                    count=count+0.05;
            }
            if ( seq_one[i] == 45 || seq_one[i] == 46 ) {
                if ( seq_two[i] == amino2 ) 
                    count=count+0.05;
                else if ( seq_two[i] == 45 || seq_two[i] == 46 )
                    count=count+0.0025;
            }
            i=i+1;
        }
        prob_pair=count/i;

/*  If prob_pair (call it x) is zero, we wo't be able to take its log; it's 
    going to be nan. But since the formula is ~ x ln x, we can assign a very
    small value to x when it is zero. In that case, we'll have x ln x, which
    goes to zero as x --> 0, as we want. */
        if ( prob_pair == 0 )
            prob_pair = 1E-50;

        return(prob_pair);
    }
    
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
    
    Py_XDECREF(arrobj);
    Py_XDECREF(result);
    return Py_BuildValue("");

}

int calc_mutual_info(char *seq, double *mutual, long numseq, long lenseq) {
    
    /* seq has length numseq * lenseq
       ent has length lenseq
    */
    

    return 0;
}

static PyMethodDef msatools_methods[] = {

	{"parseSelex",  (PyCFunction)parseSelex, METH_VARARGS, 
	 "Return list of labels and a dictionary mapping labels to sequences \n"
	 "after parsing the sequences into empty numpy character array."},

	{"parseFasta",  (PyCFunction)parseFasta, METH_VARARGS, 
	 "Return list of labels and a dictionary mapping labels to sequences \n"
	 "after parsing the sequences into empty numpy character array."},

	{"calcInfoEntropy",  (PyCFunction)calcInfoEntropy, METH_VARARGS, 
	 "Calculate information entrpoy for given character array into given \n"
     "double array."},

	{NULL, NULL, 0, NULL}
	
};


PyMODINIT_FUNC initmsatools(void) {

	Py_InitModule3("msatools", msatools_methods,
	    "Multiple sequence alignment IO and analysis tools.");
	    
    import_array();
}
