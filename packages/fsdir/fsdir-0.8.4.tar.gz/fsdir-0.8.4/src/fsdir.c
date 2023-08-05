/*
 * Copyright: Rui Gomes, all rights reserved.
 * Distributed under GPL v2.
 */

/*rui.tech@gmail.com 
 *
 * with great speed encrease compared with a pure python version
 * Current version 0.8.3
 *
 * 2012-12-26
 * Major restructer of the code;
 * Add function that return a list 
 * of all the files that error out;
 * Add Inode information to the return;
 *
 * 2012-12-20
 * Code clean up
 *
 * 2012-12-01
 * Add error handling by errno
 * Add positional arguments and keywords
 * Add option to disable crc32 check sum 
 * Return exception if initial directory of path doesnt exist.
 *  <fsdir.erro> exception 
 * Overal code clean up. 
 *
 * * * * * * * TODO LIST ROAD MAP FOR 0.9  * * * * * * *  
 *                                                     *
 * TODO: Add option for output type List or Dict       *
 * TODO: Add callback                                  *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * 2012-01-11
 * Change the function from ftw() to nftw()
 * resolved the problem with global flag not be reseted between calls
 */

#include <Python.h>
#include "headers/fsdir.h"

/* Those are denided at analyze.c */
extern long fTotal;
extern long dTotal;
extern long sTotal;
extern PyObject *dir;
extern PyObject *errors;
extern PyObject *fsdirError;
extern int flag;
extern int flag_crc32;

//Declare function
static PyObject 
*fsdir_go(PyObject *self, PyObject *args, PyObject* keywds){

    // Keyword args
    static char *kwlist[] = {"path", "summary", "crc32", NULL};
    const char *path;
    // Set defaults 
    flag=0;
    flag_crc32=0;
 
    PyObject *set;
    set=PyDict_New();
    
    if (!PyArg_ParseTupleAndKeywords
		(args, keywds, "s|ii",kwlist, &path,&flag,&flag_crc32))
        {return NULL;}

    if(access(path, R_OK)){
        PyErr_SetString(fsdirError, "Could access path.");
        return NULL;}
    
    
    dir=PyList_New(0);
    errors=PyList_New(0);
    preAnalyze(path);
        
    if(flag){
        PyDict_SetItem(set, 
		PyString_FromString("Dirs"), PyInt_FromLong(dTotal));
        PyDict_SetItem(set, 
		PyString_FromString("Files"),PyInt_FromLong(fTotal));
        PyDict_SetItem(set, 
		PyString_FromString("Size"), PyInt_FromLong(sTotal));
        PyList_Append(dir, set);}

    //give a clean start next time.
    dTotal=fTotal=sTotal=0;

    return dir; //Return global var to python
}

static PyObject 
*fsdir_errors(PyObject *self, PyObject *args, PyObject* keywds){

    if(!errors)
        return PyList_New(0);
return errors;
}



static PyMethodDef fsdirMethods[] = {
    {"go", (PyCFunction)fsdir_go, METH_VARARGS|METH_KEYWORDS,
     "Return a list of dicts with fallow values\n"
     "[{'Owner': Username," 
     "'permGroup':'rw-', "
     "'permOwner': '-wx', "
     "'permOthers': 'r-x', "
     "'Path': 'Path of the file/dir',"
     "'Type': 'D/F', "
     "'CRC32': 'HASH'(If enabled by flag),"
     "'Inode': 'Inode int',"
     "'Size': Size in kilobytes}]\n"
     "With summary True\n"
     "[{Dir:21,Files:123,Total:3215}]"},
    {"errors", (PyCFunction)fsdir_errors, METH_VARARGS|METH_KEYWORDS,
     "Return a list with the files that error out.\n"},
    {NULL, NULL, 0, NULL} 
};

PyMODINIT_FUNC initfsdir(void){
 
    PyObject *m;
    m=Py_InitModule("fsdir", fsdirMethods);
    fsdirError = PyErr_NewException("fsdir.error", NULL, NULL);
    Py_INCREF(fsdirError);
    PyModule_AddObject(m, "__fsdirExceptions__", fsdirError);
    PyModule_AddStringConstant(m, "__version__", "0.8.4");
    PyModule_AddStringConstant(m, "__doc__", "go(path='The path',\
summary=[True|False], crc32=[True|False])\n\
    The true/false flag enable or disable the summary and crc32 mode\n\
errors()\n\
    Return the list of files that couldnt be process.");
}


int main(int argc, char *argv[]){

    Py_SetProgramName(argv[0]);
    Py_Initialize();
    initfsdir();

    return 0;
}


