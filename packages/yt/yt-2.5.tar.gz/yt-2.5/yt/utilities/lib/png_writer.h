#ifndef __PYX_HAVE__yt__utilities__lib__png_writer
#define __PYX_HAVE__yt__utilities__lib__png_writer

struct mem_encode;

/* "yt/utilities/lib/png_writer.pyx":225
 * # http://stackoverflow.com/questions/1821806/how-to-encode-png-to-buffer-using-libpng
 * 
 * cdef public struct mem_encode:             # <<<<<<<<<<<<<<
 *     char *buffer
 *     size_t size
 */
struct mem_encode {
  char *buffer;
  size_t size;
};

#ifndef __PYX_HAVE_API__yt__utilities__lib__png_writer

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(void) my_png_write_data(png_structp, png_bytep, size_t);
__PYX_EXTERN_C DL_IMPORT(void) my_png_flush(png_structp);

#endif /* !__PYX_HAVE_API__yt__utilities__lib__png_writer */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initpng_writer(void);
#else
PyMODINIT_FUNC PyInit_png_writer(void);
#endif

#endif /* !__PYX_HAVE__yt__utilities__lib__png_writer */
