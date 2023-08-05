/*
    PGExt - pygame extension - color
    Author: Josef Vanžura
    Required: Python 2.5+, PyGame 1.8.1+, SDL 1.2
*/

#include "pgext.h"

#define PGEXT_VERSION 6

/*
    Set all opaque (alpha>0) pixels to specified color (R,G,B).
*/
static PyObject* setColor( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    Uint32 *pixels;
    int w,h,x,y = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;
    PyObject *py_color = NULL;
    Uint8 color[4];
    Uint8 r,g,b,a;

    PY_PARSEARGS_BEGIN
        "OO", &py_surface, &py_color
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);

    if(!RGBAFromColorObj (py_color, color))
        return Py_None;
    
    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, format, &r, &g, &b, &a );
            if(a==0) continue;
            pixel = SDL_MapRGBA( format, color[0], color[1], color[2], a );
            pixels[ (y*w)+x ] = pixel;
        }
    }
    
    Py_INCREF(Py_None);
    return Py_None;

}

/*
    Greyscale
    method:
        0 - avg RGB
        1 - HSV (saturation)
*/
static PyObject* greyscale( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_PixelFormat *format = NULL;
    Uint32 *pixels;
    int w,h,x,y = 0;
    Uint32 pixel;
    Uint8 r,g,b,a;
    double hue,sat,val;
    int v;
    int method = 0;

    PY_PARSEARGS_BEGIN
        "O|i", &py_surface, &method
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, format, &r, &g, &b, &a );
            if( method == 0 ){
                /* average RGB */
                v = (r+g+b)/3.0;
                pixel = SDL_MapRGBA( format, v, v, v, a );
            }
            if( method == 1 ){
                /* HSV stauration = 0 */
                RGB2HSV( r, g, b, &hue, &sat, &val );
                sat = 0;
                HSV2RGB( hue, sat, val, &r, &g, &b );
                pixel = SDL_MapRGBA( format, r, g, b, a );
            }
            if( method == 2 ){
                /* HSL stauration = 0 */
                RGB2HSL( r, g, b, &hue, &sat, &val );
                sat = 0;
                HSL2RGB( hue, sat, val, &r, &g, &b );
                pixel = SDL_MapRGBA( format, r, g, b, a );
            }
            pixels[ (y*w)+x ] = pixel;

        }
    }
    Py_INCREF(Py_None);
    return Py_None;
}


/*
    Invert surface colors
*/
static PyObject* invert( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    Uint32 *pixels;
    int w,h,x,y = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;
    Uint8 r,g,b,a;

    PY_PARSEARGS_BEGIN
        "O", &py_surface
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, format, &r, &g, &b, &a );
            pixel = SDL_MapRGBA( format, 255-r, 255-g, 255-b, a );
            pixels[ (y*w)+x ] = pixel;

        }
    }
    Py_INCREF(Py_None);
    return Py_None;
}

/*
    Change hue of surface
    method: (only 0)
        0 - hue += shift
*/
static PyObject* hue( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    Uint32 *pixels;
    int w,h,x,y = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;
    int shift = 0;
    int method = 0;
    Uint8 r,g,b,a;
    double hue,sat,val;

    PY_PARSEARGS_BEGIN
        "Oi|i", &py_surface, &shift, &method
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, format, &r, &g, &b, &a );

            RGB2HSV( r,g,b, &hue, &sat, &val );

            if(method == 0){
                hue += (double)(shift);
            }

            if(method == 1){
                hue = (double)(shift);
            }

            /* clamp hue 0-100 */
            if( hue < 0 ){
                hue = 360.0+hue;
            }
            if( hue > 360 ){
                hue = hue-360.0;
            }
            hue = clampValue( hue, 0.0, 360.0 );
            HSV2RGB( hue,sat,val, &r, &g, &b );
            pixel = SDL_MapRGBA( format, r, g, b, a );
            pixels[ (y*w)+x ] = pixel;
        }
    }
    Py_INCREF(Py_None);
    return Py_None;

}

/*
    Change saturation of surface
    method:
        0 - sat += s_shift
        1 - sat = s_shift
        2 - sat =  sat * (s_shift/100.0)
*/
static PyObject* saturation( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    Uint32 *pixels;
    int w,h,x,y = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;
    int shift = 0;
    int method = 0;
    Uint8 r,g,b,a;
    double hue,sat,val;
    double percent = 0;

    PY_PARSEARGS_BEGIN
        "Oi|i", &py_surface, &shift, &method
    PY_PARSEARGS_END
    
    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);

    if( method == 2 ){
        percent = ((double)(shift))/100.0;
    }
    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, format, &r, &g, &b, &a );

            RGB2HSV( r,g,b, &hue, &sat, &val );
            if( method == 0 )
                sat += (double)(shift);
            
            if( method == 1 )
                sat = (double)(shift);
            
            if( method == 2 )
                sat = sat * percent;
            
            /* clamp sat 0-100 */
            sat = clampValue( sat, 0.0, 100.0 );
            HSV2RGB( hue,sat,val, &r, &g, &b );
            pixel = SDL_MapRGBA( format, r, g, b, a );
            pixels[ (y*w)+x ] = pixel;
        }
    }
    Py_INCREF(Py_None);
    return Py_None;

}

/*
    Change value of surface
    method:
        0 - val += v_shift
        1 - val = v_shift
        2 - val =  val * (v_shift/100.0)
*/
static PyObject* value( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    Uint32 *pixels;
    int w,h,x,y = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;

    int shift = 0;
    int method = 0;
    Uint8 r,g,b,a;
    double hue,sat,val;
    double percent = 0;

    PY_PARSEARGS_BEGIN
        "Oi|i", &py_surface, &shift, &method
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);

    if( method == 2 ){
        percent = ((double)(shift))/100.0;
    }
    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, format, &r, &g, &b, &a );

            RGB2HSV( r,g,b, &hue, &sat, &val );
            if( method == 0 )
                val += (double)(shift);
            
            if( method == 1 )
                val = (double)(shift);
            
            if( method == 2 )
                val = val * percent;
            
            /* clamp sat 0-100 */
            val = clampValue( val, 0.0, 100.0 );
            HSV2RGB( hue,sat,val, &r, &g, &b );
            pixel = SDL_MapRGBA( format, r, g, b, a );
            pixels[ (y*w)+x ] = pixel;
        }
    }
    Py_INCREF(Py_None);
    return Py_None;

}

static PyObject* lightness( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    Uint32 *pixels;
    int w,h,x,y = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;
    int shift = 0;
    int method = 0;
    Uint8 r,g,b,a;
    double hue,sat,val;
    double percent = 0;

    PY_PARSEARGS_BEGIN
        "Oi|i", &py_surface, &shift, &method
    PY_PARSEARGS_END
    
    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);

    if( method == 2 ){
        percent = ((double)(shift))/100.0;
    }
    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, format, &r, &g, &b, &a );

            RGB2HSL( r,g,b, &hue, &sat, &val );
            if( method == 0 )
                val += (double)(shift);
            
            if( method == 1 )
                val = (double)(shift);
            
            if( method == 2 )
                val = val * percent;
            
            /* clamp sat 0-100 */
            val = clampValue( val, 0.0, 100.0 );
            HSL2RGB( hue,sat,val, &r, &g, &b );
            pixel = SDL_MapRGBA( format, r, g, b, a );
            pixels[ (y*w)+x ] = pixel;
        }
    }
    Py_INCREF(Py_None);
    return Py_None;

}

/*
    Replace pixels (hue == check_hue) with new_hue.
*/
static PyObject* colorize( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    Uint32 *pixels;
    int w,h,x,y = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;
    int check_hue,new_hue;
    int s_shift = 0;
    int v_shift = 0;
    Uint8 r,g,b,a;
    double hue,sat,val;
    float sq;
    long count = 0;

    PY_PARSEARGS_BEGIN
        "Oii|ii", 
        &py_surface, &check_hue, &new_hue, &v_shift, &s_shift
    PY_PARSEARGS_END
    
    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, format, &r, &g, &b, &a );
            RGB2HSV( r,g,b, &hue, &sat, &val );
            if( (int)hue == check_hue ){
                hue = new_hue;
                if( s_shift != 0 || v_shift != 0 ){
                    sq = sat/100.f;
                    if( s_shift != 0 ){
                        sat += ( ((double)(s_shift)) *sq);
                        sat = clampValue( sat, 0.0, 100.0 );
                    }
                    if( v_shift != 0 ){
                        val += ( ((double)(v_shift)) *sq);
                        val = clampValue( val, 0.0, 100.0 );
                    }
                }
                count++;
            }
            HSV2RGB( hue,sat,val, &r, &g, &b );
            pixel = SDL_MapRGBA( format, r, g, b, a );
            pixels[ (y*w)+x ] = pixel;

        }
    }
    return Py_BuildValue("i", count );
}


/*
    Replace pixels (hue == check_hue) with new_hue.
*/
static PyObject* alphaMask( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    Uint32 *pixels;
    int w,h,x,y,mw,mh = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;
    PyObject* py_surface_mask = NULL;
    Uint32 *pixels_mask;
    SDL_PixelFormat *format_mask = NULL;


    Uint8 r,g,b,a;
    double hue,sat,val;
    float alpha;

    PY_PARSEARGS_BEGIN
        "OO",
        &py_surface, &py_surface_mask
    PY_PARSEARGS_END
    
    getSurfaceAttrs(py_surface_mask, &mw, &mh, &format_mask, &pixels_mask);
    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);
    
    if( mw != w || mh != h ){
        return RAISE (PyExc_ValueError, "mask must be same size as surface");
    }

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            /* get mask pixel*/
            pixel = pixels_mask[(y*w)+x];
            SDL_GetRGBA( pixel, format_mask, &r, &g, &b, &a );
            RGB2HSV( r,g,b, &hue, &sat, &val );
            if(val >= 99.9) continue;
            alpha = (float)(val/100.0);
            
            /* set pixel */
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, format, &r, &g, &b, &a );
            
            a = (Uint8)(((float)a) * alpha );
            
            pixel = SDL_MapRGBA( format, r, g, b, a );
            pixels[ (y*w)+x ] = pixel;

        }
    }
    
    return Py_None;

}


static PyMethodDef ColorMethods[] = {
    {"setColor", setColor, METH_VARARGS, "Set opaque pixels to color"},
    
    {"hue", hue, METH_VARARGS, "Hue"},
    {"saturation", saturation, METH_VARARGS, "Change saturation of surface"},
    {"value", value, METH_VARARGS, "Change value of surface"},
    {"lightness", lightness, METH_VARARGS, "Lightness"},
    
    {"invert", invert, METH_VARARGS, "Invert colors of surface"},
    {"greyscale", greyscale, METH_VARARGS, "Create greyscale surface"},
    {"colorize", colorize, METH_VARARGS, "Change hue of surface"},

    {"alphaMask", alphaMask, METH_VARARGS, ""},
    {NULL, NULL, NULL, NULL}
};

PyMODINIT_FUNC initcolor(void)
{
    PyObject *module = Py_InitModule("color", ColorMethods);
    import_pygame_surface();
    import_pygame_color();
    PyObject_SetAttrString(module, "version", PyLong_FromLong(PGEXT_VERSION));
}
