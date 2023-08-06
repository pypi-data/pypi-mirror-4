/*
 * Copyright (c) 2009-2011 Kuan-Chung Chiu <buganini@gmail.com>
 *
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF MIND, USE, DATA OR PROFITS, WHETHER
 * IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING
 * OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

#include <Python.h>
#include <bsdconv.h>

#ifndef WIN32
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

#define IBUFLEN 1024

typedef struct {
	PyObject_HEAD
	struct bsdconv_instance *ins;
} Bsdconv;

typedef struct {

	PyObject_HEAD
	FILE *fp;
} Bsdconv_file;

static void
py_bsdconv_file_dealloc(PyObject *self)
{
	FILE *fp;
	fp=((Bsdconv_file *) self)->fp;
	if(fp!=NULL)
		fclose(fp);
	PyObject_DEL(self);
}

static PyTypeObject Bsdconv_File_Type = {
#if PY_MAJOR_VERSION < 3
	PyObject_HEAD_INIT(NULL)
#else
	PyVarObject_HEAD_INIT(NULL, 0)
#endif
	.tp_name="Bsdconv_file",
	.tp_basicsize=sizeof(Bsdconv_file),
	.tp_dealloc = (destructor)py_bsdconv_file_dealloc,
};

static PyObject *
py_bsdconv_fopen(PyObject *self, PyObject *args)
{
	char *filename, *mode;
	if (!PyArg_ParseTuple(args, "ss", &filename, &mode))
		return NULL;
	Bsdconv_file *object = NULL;
	object = PyObject_NEW(Bsdconv_file, &Bsdconv_File_Type);
	if (object == NULL)
		return NULL;
	object->fp=fopen(filename, mode);
	return (PyObject *)object;
}

static PyObject *
py_bsdconv_mktemp(PyObject *self, PyObject *args)
{
	char *template;
	if (!PyArg_ParseTuple(args, "s", &template))
		return NULL;
	char *t=strdup(template);
	int fd=mkstemp(t);
	FILE *fp=fdopen(fd, "wb+");
	Bsdconv_file *object = NULL;
	object = PyObject_NEW(Bsdconv_file, &Bsdconv_File_Type);
	object->fp=fp;
	PyObject *ret=Py_BuildValue("[O,s]", object, t);
	free(t);
	return ret;
}

static PyObject *
py_bsdconv_init(PyObject *self, PyObject *args)
{
	struct bsdconv_instance *ins;

	ins=((Bsdconv *) self)->ins;
	bsdconv_init(ins);
	Py_INCREF(Py_True);
	return Py_True;
}


static PyObject *
py_bsdconv_ctl(PyObject *self, PyObject *args)
{
	struct bsdconv_instance *ins;
	int ctl;
	PyObject *a1;
	int a2;
	void *ptr=NULL;

	if (!PyArg_ParseTuple(args, "iOi", &ctl, &a1, &a2))
		return NULL;

#if PY_MAJOR_VERSION < 3
	if (PyObject_TypeCheck (a1, &PyFile_Type)){
		ptr=PyFile_AsFile(a1);
#else
	extern PyTypeObject PyIOBase_Type;
	if(PyObject_IsInstance(a1, (PyObject *)&PyIOBase_Type)){
		int fd = PyObject_AsFileDescriptor(a1);
		ptr=fdopen(fd, "a+");
#endif
#if PY_MAJOR_VERSION < 3
	}else if (PyObject_TypeCheck (a1, &Bsdconv_File_Type)){
		ptr=((Bsdconv_file *) a1)->fp;
#else
	}else if(PyObject_IsInstance(a1, (PyObject *)&Bsdconv_File_Type)){
		ptr=((Bsdconv_file *) a1)->fp;;
#endif
	}

	ins=((Bsdconv *) self)->ins;
	bsdconv_ctl(ins, ctl, ptr, a2);

	Py_INCREF(Py_True);
	return Py_True;
}

static PyObject *
py_bsdconv_insert_phase(PyObject *self, PyObject *args)
{
	static PyObject *ret;
	char *conv;
	char *s;
	int t;
	int p;

	if (!PyArg_ParseTuple(args, "zzii", &conv, &s, &t, &p))
		return NULL;
	char *r=bsdconv_insert_phase(conv, s, t, p);
	ret=Py_BuildValue("s", r);
	bsdconv_free(r);
	return ret;
}

static PyObject *
py_bsdconv_insert_codec(PyObject *self, PyObject *args)
{
	static PyObject *ret;
	char *conv;
	char *s;
	int p;
	int c;

	if (!PyArg_ParseTuple(args, "zzii", &conv, &s, &p, &c))
		return NULL;
	char *r=bsdconv_insert_codec(conv, s, p, c);
	ret=Py_BuildValue("s", r);
	bsdconv_free(r);
	return ret;
}

static PyObject *
py_bsdconv_replace_phase(PyObject *self, PyObject *args)
{
	static PyObject *ret;
	char *conv;
	char *s;
	int t;
	int p;

	if (!PyArg_ParseTuple(args, "zzii", &conv, &s, &t, &p))
		return NULL;
	char *r=bsdconv_replace_phase(conv, s, t, p);
	ret=Py_BuildValue("s", r);
	bsdconv_free(r);
	return ret;
}

static PyObject *
py_bsdconv_replace_codec(PyObject *self, PyObject *args)
{
	static PyObject *ret;
	char *conv;
	char *s;
	int p;
	int c;

	if (!PyArg_ParseTuple(args, "zzii", &conv, &s, &p, &c))
		return NULL;
	char *r=bsdconv_replace_codec(conv, s, p, c);
	ret=Py_BuildValue("s", r);
	bsdconv_free(r);
	return ret;
}

static void
py_bsdconv_dealloc(PyObject *self)
{
	struct bsdconv_instance *ins;
	ins=((Bsdconv *) self)->ins;
	if(ins!=NULL)
		bsdconv_destroy(ins);
	PyObject_DEL(self);
}

static PyObject *
py_bsdconv_conv(PyObject *self, PyObject *args)
{
	static PyObject *r;
	struct bsdconv_instance *ins;
	char *s;
	int l;
	if (!PyArg_ParseTuple(args, "z#", &s,&l))
		return NULL;
	ins=((Bsdconv *) self)->ins;

	bsdconv_init(ins);
	ins->output_mode=BSDCONV_AUTOMALLOC;
	ins->input.data=s;
	ins->input.len=l;
	ins->input.flags=0;
	ins->flush=1;
	bsdconv(ins);

	r=Py_BuildValue("s#",ins->output.data, ins->output.len);
	bsdconv_free(ins->output.data);
	return r;
}

static PyObject *
py_bsdconv_conv_chunk(PyObject *self, PyObject *args)
{
	static PyObject *r;
	struct bsdconv_instance *ins;
	char *s;
	int l;
	if (!PyArg_ParseTuple(args, "z#", &s,&l))
		return NULL;
	ins=((Bsdconv *) self)->ins;

	ins->output_mode=BSDCONV_AUTOMALLOC;
	ins->input.data=s;
	ins->input.len=l;
	ins->input.flags=0;
	bsdconv(ins);

	r=Py_BuildValue("s#",ins->output.data, ins->output.len);
	bsdconv_free(ins->output.data);
	return r;
}

static PyObject *
py_bsdconv_conv_chunk_last(PyObject *self, PyObject *args)
{
	static PyObject *r;
	struct bsdconv_instance *ins;
	char *s;
	int l;
	if (!PyArg_ParseTuple(args, "z#", &s, &l))
		return NULL;
	ins=((Bsdconv *) self)->ins;

	ins->output_mode=BSDCONV_AUTOMALLOC;
	ins->input.data=s;
	ins->input.len=l;
	ins->input.flags=0;
	ins->flush=1;
	bsdconv(ins);

	r=Py_BuildValue("s#",ins->output.data, ins->output.len);
	bsdconv_free(ins->output.data);
	return r;
}

static PyObject *
py_bsdconv_conv_file(PyObject *self, PyObject *args)
{
	struct bsdconv_instance *ins;
	char *s1, *s2;
	FILE *inf, *otf;
	char *in;
	char *tmp;
	int fd;

	if (!PyArg_ParseTuple(args, "ss", &s1, &s2))
		return NULL;
	ins=((Bsdconv *) self)->ins;
	inf=fopen(s1,"r");
	if(!inf){
		Py_INCREF(Py_None);
		return Py_None;
	}
	tmp=malloc(strlen(s2)+8);
	strcpy(tmp, s2);
	strcat(tmp, ".XXXXXX");
	if((fd=mkstemp(tmp))==-1){
		free(tmp);
		Py_INCREF(Py_None);
		return Py_None;
	}
	otf=fdopen(fd,"w");
	if(!otf){
		free(tmp);
		Py_INCREF(Py_None);
		return Py_None;
	}

#ifndef WIN32
	struct stat stat;
	fstat(fileno(inf), &stat);
	(void) fchown(fileno(otf), stat.st_uid, stat.st_gid);
	fchmod(fileno(otf), stat.st_mode);
#endif

	bsdconv_init(ins);
	do{
		in=bsdconv_malloc(IBUFLEN);
		ins->input.data=in;
		ins->input.len=fread(in, 1, IBUFLEN, inf);
		ins->input.flags|=F_FREE;
		if(ins->input.len==0){
			ins->flush=1;
		}
		ins->output_mode=BSDCONV_FILE;
		ins->output.data=otf;
		bsdconv(ins);
	}while(ins->flush==0);

	fclose(inf);
	fclose(otf);
	unlink(s2);
	rename(tmp,s2);
	free(tmp);

	Py_INCREF(Py_True);
	return Py_True;
}

static PyObject *
py_bsdconv_testconv(PyObject *self, PyObject *args)
{
	struct bsdconv_instance *ins;
	char *s;
	int l;
	if (!PyArg_ParseTuple(args, "z#", &s,&l))
		return NULL;
	ins=((Bsdconv *) self)->ins;

	bsdconv_init(ins);
	ins->output_mode=BSDCONV_NULL;
	ins->input.data=s;
	ins->input.len=l;
	ins->input.flags=0;
	ins->flush=1;
	bsdconv(ins);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
py_bsdconv_testconv_chunk(PyObject *self, PyObject *args)
{
	struct bsdconv_instance *ins;
	char *s;
	int l;
	if (!PyArg_ParseTuple(args, "z#", &s,&l))
		return NULL;
	ins=((Bsdconv *) self)->ins;

	ins->output_mode=BSDCONV_NULL;
	ins->input.data=s;
	ins->input.len=l;
	ins->input.flags=0;
	bsdconv(ins);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
py_bsdconv_testconv_chunk_last(PyObject *self, PyObject *args)
{
	struct bsdconv_instance *ins;
	char *s;
	int l;
	if (!PyArg_ParseTuple(args, "z#", &s, &l))
		return NULL;
	ins=((Bsdconv *) self)->ins;

	ins->output_mode=BSDCONV_NULL;
	ins->input.data=s;
	ins->input.len=l;
	ins->input.flags=0;
	ins->flush=1;
	bsdconv(ins);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
py_bsdconv_testconv_file(PyObject *self, PyObject *args)
{
	struct bsdconv_instance *ins;
	char *s1;
	FILE *inf;
	char *in;

	if (!PyArg_ParseTuple(args, "s", &s1))
		return NULL;
	ins=((Bsdconv *) self)->ins;
	inf=fopen(s1,"r");
	if(!inf){
		Py_INCREF(Py_None);
		return Py_None;
	}
	bsdconv_init(ins);
	do{
		in=bsdconv_malloc(IBUFLEN);
		ins->input.data=in;
		ins->input.len=fread(in, 1, IBUFLEN, inf);
		ins->input.flags|=F_FREE;
		if(ins->input.len==0){
			ins->flush=1;
		}
		ins->output_mode=BSDCONV_NULL;
		bsdconv(ins);
	}while(ins->flush==0);

	fclose(inf);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
py_bsdconv_info(PyObject *self, PyObject *args)
{
	static PyObject *r;
	struct bsdconv_instance *ins;
	ins=((Bsdconv *) self)->ins;
	r=Py_BuildValue("{s:i,s:i,s:d,s:i,s:i,s:i}","ierr",ins->ierr,"oerr",ins->oerr,"score",ins->score,"full",ins->full,"half",ins->half,"ambi",ins->ambi);
	return r;
}

static PyObject *
py_bsdconv_error(PyObject *self, PyObject *args)
{
	static PyObject *r;
	char *s;
	s=bsdconv_error();
	r=Py_BuildValue("s",s);
	bsdconv_free(s);
	return r;
}

int
py_bsdconv_valid(PyObject *self, PyObject *args)
{
	struct bsdconv_instance *ins;
	ins=((Bsdconv *) self)->ins;
	
	if(ins!=NULL)
		return 1;
	else
		return 0;
}

static PyMethodDef Bsdconv_methods[] = {
	{"init",	py_bsdconv_init,	METH_VARARGS,
		PyDoc_STR("init() -> Initialize/Reset bsdconv instance")},
	{"ctl",	py_bsdconv_ctl,	METH_VARARGS,
		PyDoc_STR("ctl(arg_ptr_obj, arg_int) -> Initialize/Reset bsdconv instance")},
	{"conv",	py_bsdconv_conv,	METH_VARARGS,
		PyDoc_STR("conv(s) -> Perform conversion")},
	{"conv_chunk",	py_bsdconv_conv_chunk,	METH_VARARGS,
		PyDoc_STR("conv_chunk(s) -> Perform conversion without initializing and flushing")},
	{"conv_chunk_last",	py_bsdconv_conv_chunk_last,	METH_VARARGS,
		PyDoc_STR("conv_chunk_last(s) -> Perform conversion without initializing")},
	{"conv_file",	py_bsdconv_conv_file,	METH_VARARGS,
		PyDoc_STR("conv_file(from_file, to_file) -> Perform conversion with given filename")},
	{"testconv",	py_bsdconv_testconv,	METH_VARARGS,
		PyDoc_STR("testconv(s) -> Perform test conversion")},
	{"testconv_chunk",	py_bsdconv_testconv_chunk,	METH_VARARGS,
		PyDoc_STR("testconv_chunk(s) -> Perform test conversion without initializing and flushing")},
	{"testconv_chunk_last",	py_bsdconv_testconv_chunk_last,	METH_VARARGS,
		PyDoc_STR("testconv_chunk_last(s) -> Perform test conversion without initializing")},
	{"testconv_file",	py_bsdconv_testconv_file,	METH_VARARGS,
		PyDoc_STR("testconv_file(from_file) -> Perform test conversion with given filename")},
	{"info",	py_bsdconv_info,	METH_VARARGS,
		PyDoc_STR("info(cd) -> Return conversion info")},
	{NULL,		NULL}		/* sentinel */
};

static PyNumberMethods Bsdconv_number_methods = {
#if PY_MAJOR_VERSION < 3
	.nb_nonzero = (inquiry) py_bsdconv_valid
#else
	.nb_bool = (inquiry) py_bsdconv_valid
#endif
};

#if PY_MAJOR_VERSION < 3
static PyObject *
py_bsdconv_getattr(PyObject *self, char *attrname)
{
	return Py_FindMethod(Bsdconv_methods, self, attrname);
}
#endif

static PyObject *
py_bsdconv_repr(PyObject *self, char *attrname)
{
	static PyObject *r;
	char *s;
	int len=32;
	struct bsdconv_instance *ins;
	ins=((Bsdconv *) self)->ins;
	if(ins==NULL){
		Py_INCREF(Py_None);
		return Py_None;
	}

	s=bsdconv_pack(ins);
	len+=strlen(s);
	char buf[len];
	sprintf(buf, "Bsdconv(\"%s\") at %p", s, ins);
	r=Py_BuildValue("s", buf);
	bsdconv_free(s);
	return r;
}

static PyTypeObject Bsdconv_Type = {
#if PY_MAJOR_VERSION < 3
	PyObject_HEAD_INIT(NULL)
#else
	PyVarObject_HEAD_INIT(NULL, 0)
#endif
	.tp_name="Bsdconv",
	.tp_basicsize=sizeof(Bsdconv),
	.tp_dealloc = (destructor)py_bsdconv_dealloc,
#if PY_MAJOR_VERSION < 3
	.tp_getattr = (getattrfunc)py_bsdconv_getattr,
#endif
	.tp_repr = (reprfunc)py_bsdconv_repr,
	.tp_methods = Bsdconv_methods,
	.tp_as_number = &Bsdconv_number_methods
};

static PyObject *
py_bsdconv_NEW(const char *c)
{
	Bsdconv *object = NULL;
	object = PyObject_NEW(Bsdconv, &Bsdconv_Type);
	object->ins=NULL;
	if (object != NULL)
		object->ins = bsdconv_create(c);
	return (PyObject *)object;
}

static PyObject *
py_bsdconv_new(PyObject *self, PyObject *args)
{
	PyObject *ret = NULL;
	char *c;
	if (PyArg_ParseTuple(args, "s", &c))
		ret=py_bsdconv_NEW(c);
	else
		ret=py_bsdconv_NEW("");
	return ret;
}

static PyObject *
py_bsdconv_codecs_list(PyObject *self, PyObject *args)
{
	PyObject *ret=PyList_New(0);
	char **list;
	char **p;
	int phase_type;
	if (!PyArg_ParseTuple(args, "i", &phase_type))
		return NULL;
	list=bsdconv_codecs_list(phase_type);
	p=list;
	while(*p!=NULL){
		PyList_Append(ret, Py_BuildValue("s", *p));
		bsdconv_free(*p);
		p+=1;
	}
	bsdconv_free(list);
	return ret;
}

static PyObject *
py_bsdconv_codec_check(PyObject *self, PyObject *args)
{
	PyObject *r;
	char *s;
	int type;
	if (!PyArg_ParseTuple(args, "iz", &type, &s))
		return NULL;
	if(bsdconv_codec_check(type, s))
		r=Py_True;
	else
		r=Py_False;
	Py_INCREF(r);
	return r;
}

static PyMethodDef module_methods[] = {
	{"insert_phase",	py_bsdconv_insert_phase,	METH_VARARGS,
		PyDoc_STR("insert_phase(conversion, codecs, phase_type, phasen) -> Insert conversion phase into bsdconv conversion string")},
	{"insert_codec",	py_bsdconv_insert_codec,	METH_VARARGS,
		PyDoc_STR("insert_codec(conversion, codec, phasen, codecn) -> Insert conversion codec into bsdconv conversion string")},
	{"replace_phase",	py_bsdconv_replace_phase,	METH_VARARGS,
		PyDoc_STR("replace_phase(conversion, codecs, phase_type, phasen) -> Replace conversion phase in the bsdconv conversion string")},
	{"replace_codec",	py_bsdconv_replace_codec,	METH_VARARGS,
		PyDoc_STR("replace_codec(conversion, codec, phasen, codecn) -> Replace conversion codec in the bsdconv conversion string")},
	{"error",	py_bsdconv_error,	METH_VARARGS,
		PyDoc_STR("error() -> Return error message")},
	{"mktemp",	py_bsdconv_mktemp,	METH_VARARGS,
		PyDoc_STR("mktemp() -> Make temporary file")},
	{"fopen",	py_bsdconv_fopen,	METH_VARARGS,
		PyDoc_STR("fopen() -> Open file")},
	{"codecs_list",	py_bsdconv_codecs_list,	METH_VARARGS,
		PyDoc_STR("codecs_list() -> list codecs")},
	{"codec_check",	py_bsdconv_codec_check,	METH_VARARGS,
		PyDoc_STR("codec_check(type, codec) -> check if a codec is available")},
	{NULL,		NULL}		/* sentinel */
};
#if PY_MAJOR_VERSION >= 3
static PyModuleDef Bsdconv_Module = {
	PyModuleDef_HEAD_INIT,
	"bsdconv",
	"BSD licensed charset/encoding converter library",
	-1,
	module_methods,
	NULL, NULL, NULL, NULL
};
#endif

PyDoc_STRVAR(module_doc,
"BSD licensed charset/encoding converter library");

/* Initialization function for the module (*must* be called initxx) */

PyMODINIT_FUNC
#if PY_MAJOR_VERSION < 3
initbsdconv(void)
#else
PyInit_bsdconv(void)
#endif
{
	PyObject *m;
	Bsdconv_Type.tp_new = (newfunc)py_bsdconv_new;
#if PY_MAJOR_VERSION < 3
	if (PyType_Ready(&Bsdconv_Type) < 0)
		return;
	m = Py_InitModule3("bsdconv", module_methods, module_doc);
	if (m == NULL)
		return;
#else
	if (PyType_Ready(&Bsdconv_Type) < 0){
		return NULL;
	}
	m = PyModule_Create(&Bsdconv_Module);
	if (m == NULL){
		return NULL;
	}
#endif
	Py_INCREF(&Bsdconv_Type);
	PyModule_AddObject(m, "Bsdconv", (PyObject *)&Bsdconv_Type);

	PyModule_AddIntConstant(m, "FROM", FROM);
	PyModule_AddIntConstant(m, "INTER", INTER);
	PyModule_AddIntConstant(m, "TO", TO);

	PyModule_AddIntConstant(m, "CTL_ATTACH_SCORE", BSDCONV_ATTACH_SCORE);
	PyModule_AddIntConstant(m, "CTL_SET_WIDE_AMBI", BSDCONV_SET_WIDE_AMBI);
	PyModule_AddIntConstant(m, "CTL_SET_TRIM_WIDTH", BSDCONV_SET_TRIM_WIDTH);
	PyModule_AddIntConstant(m, "CTL_ATTACH_OUTPUT_FILE", BSDCONV_ATTACH_OUTPUT_FILE);
#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
