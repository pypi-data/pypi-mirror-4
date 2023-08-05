#include "Python.h"

#include "parser.h"

#include <stdlib.h>

int parser_rd_source_init(parser_t *self, PyObject *source);

typedef struct _rd_source {
    PyObject* obj;
    PyObject* buffer;
    size_t position;
} rd_source;

#define RDS(source) ((rd_source *)source)

rd_source* new_rd_source(PyObject *obj) {
    rd_source *rds = (rd_source *) malloc(sizeof(rd_source));

    /* hold on to this object */
    Py_INCREF(obj);
    rds->obj = obj;
    rds->buffer = NULL;
    rds->position = 0;

    return rds;
}

void del_rd_source(void *rds) {
    Py_XDECREF(RDS(rds)->obj);
    Py_XDECREF(RDS(rds)->buffer);
    free(rds);
}

int parser_rd_source_init(parser_t *self, PyObject *source) {
    self->sourcetype = 'R';
    self->source = new_rd_source(source);
    return 0;
}


int buffer_rd_bytes(parser_t *self, size_t nbytes) {
    PyGILState_STATE state;
    PyObject *result, *func, *args, *i;
    size_t length;
    rd_source *src = RDS(self->source);

    /* delete old object */
    Py_XDECREF(src->buffer);
    args = Py_BuildValue("(i)", nbytes);
    /* printf("%s\n", PyBytes_AsString(PyObject_Repr(args))); */

    func = PyObject_GetAttrString(src->obj, "read");

    state = PyGILState_Ensure();
    result = PyObject_CallObject(func, args);
    PyGILState_Release(state);

    Py_XDECREF(args);
    Py_XDECREF(func);

    /* TODO: more error handling */
    length = PySequence_Length(result);
    self->datalen = length;
    self->data = PyBytes_AsString(result);
    src->buffer = result;

    src->position += self->datalen;

    if (!PyBytes_Check(result)) {
        self->error_msg = (char*) malloc(100);
        sprintf(self->error_msg, ("File-like object must be in binary "
                                  "(bytes) mode"));
        return -1;
    }

    if (length == 0) {
        return REACHED_EOF;
    }

    TRACE(("datalen: %d\n", self->datalen));
    TRACE(("pos: %d, length: %d", (int) src->position, (int) src->length));
    return 0;
}
