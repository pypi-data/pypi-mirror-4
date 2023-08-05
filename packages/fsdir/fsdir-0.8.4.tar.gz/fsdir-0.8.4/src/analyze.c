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
#include "headers/fsdir.h"


#define FD_LIMIT 1024

PyObject *dir;
PyObject *errors;
PyObject *fsdirError;
int flag;
int flag_crc32;
long fTotal=0;
long dTotal=0;
long sTotal=0;

int analyze
(const char * fpath, const struct stat *fss, 
int typeflag, struct FTW *ftwbuf){

    //Aux vars
	PyObject *type;
    PyObject *tmpErrors;
    tmpErrors=PyList_New(0);

	char permOwner[4]="";
	char permGroup[4]="";
	char permOthers[4]="";
	int  userName;
	int crc32rv=0;
        

    switch(typeflag){
        case FTW_SL:
            PyList_Append(tmpErrors, 
                PyString_FromString(fpath));
            PyList_Append(tmpErrors, 
                PyString_FromString("Is a Symlink"));
            PyList_Append(errors, tmpErrors);

            return 0;
        case FTW_F:
            if(!flag) {
                if (S_ISSOCK(fss->st_mode)){
                    PyList_Append(tmpErrors, 
                    PyString_FromString(fpath));
                    PyList_Append(tmpErrors, 
                    PyString_FromString("Is a Socket"));
                    PyList_Append(errors, tmpErrors);
                    return 0;}
                if (S_ISFIFO(fss->st_mode)){
                    PyList_Append(tmpErrors, 
                    PyString_FromString(fpath));
                    PyList_Append(tmpErrors, 
                    PyString_FromString("Is a fifo"));
                    PyList_Append(errors, tmpErrors);
 
                    return 0;}

                type=PyString_FromString("F");
                if ((fss->st_blocks*512)!=0 && flag_crc32){
                    crc32rv=crc32Digest(fpath);
                }else {
                    crc32rv=0;}
            }else{fTotal++;}
            break;
        case FTW_D:
            if(!flag){type=PyString_FromString("D");
            }else{dTotal++;}
            break;
        case FTW_DNR:
            PyList_Append(tmpErrors, 
            PyString_FromString(fpath));
            PyList_Append(tmpErrors, 
            PyString_FromString(strerror(errno)));
            PyList_Append(errors, tmpErrors);
 
            return 0;
        case FTW_NS:
            PyList_Append(tmpErrors, 
            PyString_FromString(fpath));
            PyList_Append(tmpErrors, 
            PyString_FromString(strerror(errno)));
            PyList_Append(errors, tmpErrors);
 
            return 0;
        default:
            return 0;
    }

    if (flag)
	/* If get the size of the file and keep going */
        {sTotal+=(fss->st_blocks*512)/1024;}
    else{
      //Return dictunary 
      PyObject *set;
      set=PyDict_New();

    /* Set owner premissions string */
    strcat(permOwner, ((fss->st_mode&S_IRUSR)==S_IRUSR) ? "r":"-");
    strcat(permOwner, ((fss->st_mode&S_IWUSR)==S_IWUSR) ? "w":"-");
    strcat(permOwner, ((fss->st_mode&S_IXUSR)==S_IXUSR) ? "x":"-");  
    /* Set group premissions string */
    strcat(permGroup,((fss->st_mode&S_IRGRP)==S_IRGRP) ? "r":"-");
    strcat(permGroup,((fss->st_mode&S_IWGRP)==S_IWGRP) ? "w":"-");
    strcat(permGroup,((fss->st_mode&S_IXGRP)==S_IXGRP) ? "x":"-");
    /* Set others  premissions string */
    strcat(permOthers,((fss->st_mode&S_IROTH)==S_IROTH) ? "r":"-");
    strcat(permOthers,((fss->st_mode&S_IWOTH)==S_IWOTH) ? "w":"-");
    strcat(permOthers,((fss->st_mode&S_IXOTH)==S_IXOTH) ? "x":"-");

    userName=fss->st_uid;

    PyDict_SetItem(set, 
	PyString_FromString("Path"),PyString_FromString(fpath));
    PyDict_SetItem(set, 
    PyString_FromString("Size"),PyInt_FromLong((fss->st_blocks*512)/1024));
    PyDict_SetItem(set, 
    PyString_FromString("Type"), type);//add the type to the array/list
    PyDict_SetItem(set, 
    PyString_FromString("Owner"), PyInt_FromLong(userName));
    PyDict_SetItem(set, 
	PyString_FromString("permOwner"), PyString_FromString(permOwner));
    PyDict_SetItem(set, 
	PyString_FromString("permGroup"), PyString_FromString(permGroup));
    PyDict_SetItem(set, 
	PyString_FromString("permOthers"), PyString_FromString(permOthers));
	PyDict_SetItem(set, 
    PyString_FromString("Inode"),PyInt_FromLong(fss->st_ino));
    if(S_ISREG(fss->st_mode) && flag_crc32) 
    	{PyDict_SetItem(set, 
		 PyString_FromString("CRC32"), PyInt_FromLong(crc32rv));}

    PyList_Append(dir, set);//add the first array to the second array
    Py_XDECREF(set);    // Do some clean up so we dont fill the memory :)
    Py_XDECREF(type);   //
    return 0;

    }//Here ends the if for the Flag

    return 0;
    }


int preAnalyze(const char *path){
    
    int options=FTW_PHYS;
    nftw(path, &analyze, 1,options);//nftw call the analyze

return 0;}

