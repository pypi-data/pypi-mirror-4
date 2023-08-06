#ifndef __PYX_HAVE__couchbase__libcouchbase
#define __PYX_HAVE__couchbase__libcouchbase


/* "couchbase/libcouchbase.pyx":11
 * 
 * 
 * cdef public enum _cb_formats:             # <<<<<<<<<<<<<<
 *     FMT_JSON = 0x0
 *     FMT_PICKLE = 0x1
 */
enum _cb_formats {
  FMT_JSON = 0x0,
  FMT_PICKLE = 0x1,
  FMT_PLAIN = 0x2,
  FMT_MASK = 0x3
};

#ifndef __PYX_HAVE_API__couchbase__libcouchbase

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

#endif /* !__PYX_HAVE_API__couchbase__libcouchbase */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initlibcouchbase(void);
#else
PyMODINIT_FUNC PyInit_libcouchbase(void);
#endif

#endif /* !__PYX_HAVE__couchbase__libcouchbase */
