 #include <Python.h>
#include <datetime.h>
#include <cairo.h>
#include <stdio.h>

int width = 709;
int height = 358;

static PyObject *ArgumentError;

static double line1color[] = {
    0.89,
    0.40,
    0.38
};

static double line2color[] = {
    0.70,
    0.80,
    0.45
};

static double line3color[] = {
    0.28,
    0.70,
    0.80
};

int checkForLegends(PyObject *lines)
{
    int hasLegends = 1;
    PyObject * key = PyString_FromString("legend");

    PyObject *iterator = PyObject_GetIter(lines);
    PyDictObject *item;

    while (item = PyIter_Next(iterator)) {
        if(!PyDict_Contains(item, key)) {
            hasLegends = 0;
        }

        /* release reference when done */
        Py_DECREF(item);
    }

    Py_DECREF(iterator);

    return hasLegends;
}

static PyObject * plotLinechart(PyObject *self, PyObject *args)
{
    PyDictObject *dict;
    PyDictObject *size;
    long maxX, maxY, minX, minY, xSteps, ySteps, _xSteps, _ySteps;
    char *path;

    if(!PyArg_ParseTuple(args, "OOlllls", &dict, &size, &maxX, &maxY, &minX, &minY, &path))
        return NULL;

    xSteps = maxX - minX;
    _xSteps = xSteps;
    int xFactor = 1;

    while (xSteps > 20) {
        xFactor += 10;
        xSteps = xSteps / xFactor;
    }

    int yFactor = 1;
    ySteps = maxY - minY;
    _ySteps = ySteps;

    int percentage = 0;
    PyObject *key = PyString_FromString("type");
    if (PyDict_Contains(dict, key)) {
        char *type = PyString_AsString(PyDict_GetItem(dict, key));

        if (strcmp(type, "percentage") == 0) {
            percentage = 1;
            ySteps = 4;
            yFactor = 25;
        }
    }

    if (!percentage) {
        while (ySteps > 20) {
            yFactor += 10;
            ySteps = ySteps / yFactor;
            if (ySteps % yFactor) {
                ySteps++;
            }
        }
    }


    PyObject *lines = PyDict_GetItemString(dict, "lines");

    // Drawing the legend
    cairo_text_extents_t te;

    cairo_surface_t *surface =
    cairo_image_surface_create (CAIRO_FORMAT_ARGB32, width, height);
    cairo_t *cr =
    cairo_create (surface);

    cairo_select_font_face (cr, "Lucida", CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_BOLD);
    cairo_set_font_size (cr, 11.0);

    //Drawing the legends
    if (checkForLegends(lines)) {
        double initialLegendX = 70.0;

        int count = 0;
        PyObject *iterator = PyObject_GetIter(lines);
        PyDictObject *item;

        while (item = PyIter_Next(iterator)) {
            char *legend = PyString_AsString(PyDict_GetItemString(item, "legend"));
            PyObject *color = PyDict_GetItemString(item, "color");

            double r = PyFloat_AsDouble(PyTuple_GetItem(color, 0));
            double g = PyFloat_AsDouble(PyTuple_GetItem(color, 1));
            double b = PyFloat_AsDouble(PyTuple_GetItem(color, 2));

            cairo_set_source_rgb (cr, r, g, b);
            cairo_move_to (cr, initialLegendX, 10.0);
            cairo_show_text (cr, legend);

            cairo_text_extents(cr, legend, &te);

            cairo_rectangle(cr, initialLegendX - 15.0, 2.0, 10.0, 10.0);
            cairo_fill(cr);

            initialLegendX += 40.0 + te.width;
            count++;
            /* release reference when done */
            Py_DECREF(item);
        }

        Py_DECREF(iterator);
    }

    // Drawing the grid
    double bottomGridX = 50.0;
    double bottomGridY = height - 50.0;
    double graphWidth = width - 100.0;
    double graphHeight = height - 80.0;

    cairo_set_source_rgb (cr, 0.38, 0.38, 0.38);

    cairo_move_to(cr, bottomGridX, bottomGridY);
    cairo_line_to(cr, bottomGridX, 30.0);
    cairo_stroke(cr);

    cairo_move_to(cr, bottomGridX, bottomGridY);
    cairo_line_to(cr, graphWidth + 50, bottomGridY);
    cairo_stroke(cr);

    char stepLabel[60];

    printf("y steps: %d\n", ySteps);

    int i;
    double step = graphHeight / ySteps;
    double currentLine = bottomGridY;
    for(i = 0; i <= ySteps; i++) {
        if (currentLine != bottomGridY) {
            cairo_set_source_rgb (cr, 0.80, 0.80, 0.80);
            cairo_move_to(cr, bottomGridX, currentLine);
            cairo_line_to(cr, graphWidth + 50.0, currentLine);
            cairo_stroke(cr);
        }

        char mask[4] = "%d";
        char percentage_mask[5] = "%d%%";

        sprintf(stepLabel, percentage ? percentage_mask : mask, yFactor * i + minY);

        cairo_set_source_rgb (cr, 0.20, 0.38, 0.67);
        cairo_text_extents(cr, stepLabel, &te);
        cairo_move_to(cr, bottomGridX - 5 - te.width, currentLine + te.height / 2);
        cairo_show_text(cr, stepLabel);

        currentLine -= step;
    }

    step = graphWidth / xSteps;
    currentLine = bottomGridX;
    for(i = minX; i <= maxX; i ++) {
        if (currentLine != bottomGridX) {
            cairo_set_source_rgb (cr, 0.80, 0.80, 0.80);
            cairo_move_to(cr, currentLine, bottomGridY);
            cairo_line_to(cr, currentLine, 30.0);
            cairo_stroke(cr);
        }

        sprintf(stepLabel, "%d", i * xFactor + minX);

        cairo_set_source_rgb (cr, 0.20, 0.38, 0.67);
        cairo_text_extents(cr, stepLabel, &te);
        cairo_move_to(cr, currentLine - te.width / 2, bottomGridY + 20.0);
        cairo_show_text(cr, stepLabel);

        currentLine += step;
    }

    PyObject *iterator = PyObject_GetIter(lines);
    PyDictObject *item;

    while (item = PyIter_Next(iterator)) {
        PyObject *color = PyDict_GetItemString(item, "color");

        double r = PyFloat_AsDouble(PyTuple_GetItem(color, 0));
        double g = PyFloat_AsDouble(PyTuple_GetItem(color, 1));
        double b = PyFloat_AsDouble(PyTuple_GetItem(color, 2));

        cairo_set_source_rgb (cr, r, g, b);

        PyObject * values = PyDict_GetItemString(item, "values");

        PyObject *v_iterator = PyObject_GetIter(values);
        PyObject *val;

        double prevX, prevY;
        int first = 1;

        while (val = PyIter_Next(v_iterator)) {
            double x = PyFloat_AsDouble(PyTuple_GetItem(val, 0));
            double y = PyFloat_AsDouble(PyTuple_GetItem(val, 1));

            x = x *  (graphWidth / _xSteps) + bottomGridX;
            y = bottomGridY - (y - minY) *  (graphHeight / _ySteps);

            if (!first) {
                cairo_line_to(cr, x, y);
                cairo_stroke(cr);
            }

            cairo_move_to(cr, x, y);

            first = 0;

            /* release reference when done */
            Py_DECREF(val);
        }

        Py_DECREF(v_iterator);

        /* release reference when done */
        Py_DECREF(item);
    }

    Py_DECREF(iterator);

    cairo_destroy (cr);
    cairo_surface_write_to_png (surface, path);
    cairo_surface_destroy (surface);

    Py_RETURN_TRUE;
}

static PyMethodDef PlottingMethods[] = {
    { "plot_linechart", plotLinechart, METH_VARARGS,
      "Generates a linechart." },
      { NULL, NULL, 0, NULL }  /* Sentinel */
};

PyMODINIT_FUNC
init_charting (void)
{
    PyObject *m;

    m = Py_InitModule("_charting", PlottingMethods);
    if (m == NULL)
        return;

    ArgumentError = PyErr_NewException("charting.error", NULL, NULL);
    Py_INCREF(ArgumentError);
    PyModule_AddObject(m, "error", ArgumentError);
}
