#include <Python.h>
#include <pwd.h>
#include <stdio.h>
#include <string.h>
#include <ftw.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/param.h>
#include <stdint.h>
#include <errno.h>
#include <string.h>
#include "headers/crc32.h"


/*
 * Copyright: Rui Gomes, all rights reserved.
 * Distributed under GPL v2.
 */

/*rui.tech@gmail.com 2012 - 12 - 01
 *
 * with great speed encrease compared with a pure python version
 * Current version 0.8
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
 * TODO: Return a second list with the error output    *
 *                                                     *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * 2012-01-11
 * Change the function from ftw() to nftw()
 * resolved the problem with global flag not be reseted between calls
 */
 
#define FD_LIMIT 1024

//Declare function
int nftw(const char *path, int (*fn)(const char *, const struct stat *, int, struct FTW *), int depth, int flags);

//Global variables 
PyObject *dir;
static PyObject *fsdirError;

int flag;
int flag_crc32;
long fTotal=0;
long dTotal=0;
long sTotal=0;

//Function that get the total size
int sum(const char * fpath, const struct stat *fss, int typeflag, struct FTW *ftwbuf){

        //Aux vars
        PyObject *set;
        PyObject *type;
        int crc32rv=0;

        char permOwner[4]="";
        char permGroup[4]="";
        char permOthers[4]="";
        int  userName;

        set=PyDict_New();

    switch(typeflag){
        case FTW_SL: return 0;
        case FTW_F:
            if(!flag) {
                if (S_ISSOCK(fss->st_mode)){
                    printf("File %s is a socket\n",fpath);
                    return 0;
                }
                if (S_ISFIFO(fss->st_mode)) {
                    printf("Is fifo %s\n",fpath);
                    return 0;
                }

                type=PyString_FromString("F");
                if ((fss->st_blocks*512)!=0 && flag_crc32){
                    crc32rv=crc32Digest(fpath);
                }else {
                    crc32rv=0;
                }
            }else{fTotal++;}
            break;
        case FTW_D:
            if(!flag){type=PyString_FromString("D");
            }else{dTotal++;}
            break;
        case FTW_DNR:
            printf("Cant read %s\n%s\n",fpath,strerror(errno) );
            return 0;
        case FTW_NS:
            printf("Cant read %s\n%s\n",fpath,strerror(errno));
            return 0;
        default:
            return 0;
    }

    if (flag)
        {sTotal+=(fss->st_blocks*512)/1024;}
    else{

      if((fss->st_mode&S_IRUSR)==S_IRUSR)
        {strcat(permOwner,"r");}
      else{strcat(permOwner,"-");}		
      if((fss->st_mode&S_IWUSR)==S_IWUSR)
          {strcat(permOwner,"w");}
      else{strcat(permOwner,"-");}	
      if((fss->st_mode&S_IXUSR)==S_IXUSR)
          {strcat(permOwner,"x");}
      else{strcat(permOwner,"-");}
      if((fss->st_mode&S_IRGRP)==S_IRGRP)
          {strcat(permGroup,"r");}
      else{strcat(permGroup,"-");}
      if((fss->st_mode&S_IWGRP)==S_IWGRP)
          {strcat(permGroup,"w");}
      else{strcat(permGroup,"-");}
      if((fss->st_mode&S_IXGRP)==S_IXGRP)
          {strcat(permGroup,"x");}
      else{strcat(permGroup,"-");}   
      if((fss->st_mode&S_IROTH)==S_IROTH)
          {strcat(permOthers,"r");}
      else{strcat(permOthers,"-");}
      if((fss->st_mode&S_IWOTH)==S_IWOTH)
          {strcat(permOthers,"w");}
      else{strcat(permOthers,"-");}
       
      if((fss->st_mode&S_IXOTH)==S_IXOTH)
           {strcat(permOthers,"x");}
      else{strcat(permOthers,"-");}


      userName=fss->st_uid;

      PyDict_SetItem(set, PyString_FromString("Path"),PyString_FromString(fpath));//Add the path to the array/list
      PyDict_SetItem(set, PyString_FromString("Size"),PyInt_FromSsize_t((fss->st_blocks*512)/1024) );//add the size to the array/list
      PyDict_SetItem(set, PyString_FromString("Type"), type);//add the type to the array/list
      PyDict_SetItem(set, PyString_FromString("Owner"), PyInt_FromSsize_t(userName));
      PyDict_SetItem(set, PyString_FromString("permOwner"), PyString_FromString(permOwner));
      PyDict_SetItem(set, PyString_FromString("permGroup"), PyString_FromString(permGroup));
      PyDict_SetItem(set, PyString_FromString("permOthers"), PyString_FromString(permOthers));

      if(S_ISREG(fss->st_mode) && flag_crc32) 
           {PyDict_SetItem(set, PyString_FromString("CRC32"), PyInt_FromLong(crc32rv));}

    	PyList_Append(dir, set);//add the first array to the second array
    	Py_XDECREF(set);    // Do some clean up so we dont fill the memory :)
    	Py_XDECREF(type);   //

    }//Here ends the if for the Flag
     //If the flag is false none of this will be executed

    return 0;
}



static PyObject *fsdir_go(PyObject *self, PyObject *args, PyObject* keywds){
    
    const char *command;
    int options=FTW_PHYS;

    // Keyword args
    static char *kwlist[] = {"path", "summary", "crc32", NULL};
    char *path;
    int summary;
    int crc32;
    // --

    // Set defaults 
    flag=1;
    flag_crc32=0;
    // --
 
    PyObject *set;
    set=PyDict_New();
    
    if (!PyArg_ParseTupleAndKeywords(args, keywds, "s|ii",kwlist, &path,&summary,&crc32))
        return NULL;
   
    command=path;
    flag=summary;
    flag_crc32=crc32;

    if(access(path, R_OK)){
        PyErr_SetString(fsdirError, "Could access path.");
        return NULL;
   }
    

    dir=PyList_New(0);
    nftw(command, &sum, 1,options);//nftw call the sum function 
    
    if(flag){
        PyDict_SetItem(set, PyString_FromString("Dirs"), PyInt_FromLong(dTotal));
        PyDict_SetItem(set, PyString_FromString("Files"),PyInt_FromLong(fTotal));
        PyDict_SetItem(set, PyString_FromString("Size"), PyInt_FromLong(sTotal));
        PyList_Append(dir, set);
    }

    //Odd but needed, reset the global flags
    //give a clean start next time.
    dTotal=0;
    fTotal=0;
    sTotal=0;

    return dir; //Return global var to python
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
     "'Size': Size in kilobytes}]\n"
     "With summary True\n"
     "[{Dir:21,Files:123,Total:3215}]"},
    {NULL, NULL, 0, NULL} 
};

PyMODINIT_FUNC initfsdir(void){
 
    PyObject *m;
    m=Py_InitModule("fsdir", fsdirMethods);
    
    fsdirError = PyErr_NewException("fsdir.error", NULL, NULL);
    Py_INCREF(fsdirError);
    PyModule_AddObject(m, "error", fsdirError);

    PyModule_AddStringConstant(m, "__version__", "0.8");
    PyModule_AddStringConstant(m, "__doc__", "go(path='The path',summary=[True|False], crc32=[True|False])\n\
            The true/false flag enable or disable the summary and crc32 mode");
}


int main(int argc, char *argv[]){

    Py_SetProgramName(argv[0]);
    Py_Initialize();
    initfsdir();

    return 0;
}

