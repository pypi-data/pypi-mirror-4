/*
    Program:    buildHistogram.c
    Author:     Christopher Hanley
    Purpose:    Populate a 1 dimensional python object to create a histogram

*/
#include <Python.h>
#include "numpy/arrayobject.h"

#include <string.h>
#include <stdio.h>

int populate1DHist_(float *image, int image_elements, 
		    unsigned int *histogram, int histogram_elements,
                    float minValue, float maxValue, float binWidth)
{
    int i, index=0;
    for (i = 0; i < image_elements; i++) {
        if ( (image[i] >= minValue) && (image[i] < maxValue) ) {
            index = (int)((double)(image[i] - minValue) / binWidth );

            /* Handle histogram population for floating point errors at end points */
            /* Case 1: Populating below index 0.*/
            if ( index < 0 ) {
                histogram[0] += 1;
            }
            /* Case 2: Populating above the maximum index value*/
            else if (index >= histogram_elements ) {
                histogram[histogram_elements - 1] +=1;
            }
            /* Case 3: Normal Case - Population of histogram occurs as expected in valid index range */
            else {
                histogram[ index ] += 1;    
            }
        } 
    }
    return 1;
}

static PyObject * populate1DHist(PyObject *obj, PyObject *args)
{
    PyObject *oimage, *ohistogram;
    PyArrayObject *image, *histogram;
    float minValue, maxValue, binWidth;
    int status=0;

    if (!PyArg_ParseTuple(args,"OOfff:populate1DHist",&oimage,&ohistogram,&minValue,&maxValue,&binWidth))
	    return NULL;

    image = (PyArrayObject *)PyArray_ContiguousFromObject(oimage, PyArray_FLOAT32, 1, 2);

    if (!image) return NULL;

	histogram = (PyArrayObject *)PyArray_ContiguousFromObject(ohistogram, PyArray_UINT32, 1, 1);

    if (!histogram) return NULL;
    
    status = populate1DHist_((float *)image->data, PyArray_Size((PyObject*)image),
			     (unsigned int *)histogram->data, PyArray_Size((PyObject*)histogram),
			     minValue, maxValue, binWidth);

    Py_XDECREF(image);
    Py_XDECREF(histogram);

    return Py_BuildValue("i",status);
}

static PyMethodDef buildHistogram_methods[] =
{
    {"populate1DHist",  populate1DHist, METH_VARARGS, 
        "populate1Dhist(image, histogram, minValue, maxValue, binWidth)"},
    {0,            0}                             /* sentinel */
};

void initbuildHistogram(void) {
    Py_InitModule("buildHistogram", buildHistogram_methods);
    import_array();

}

