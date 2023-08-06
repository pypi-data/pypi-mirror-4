/*
    PYGAME EXTENSION - pgext
    many parts of this project are taken from opensource projects:
        libSDL
        pygame

    Copyright (c) 2012-2013, Josef Vanzura <gindar@zamraky.cz>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

    The views and conclusions contained in the software and documentation are those
    of the authors and should not be interpreted as representing official policies,
    either expressed or implied, of the FreeBSD Project.
*/

#include "pgext.h"
#include "hsvlrgb.h"

/*
    Set all opaque (alpha>0) pixels to specified color (R,G,B).
*/
static PyObject*
setColor( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    int w,h,x,y = 0;
    SDL_PixelFormat *format = NULL;
    PyObject *py_color = NULL;
    Uint8 color[4];
    Uint8 r,g,b,a;

    PY_PARSEARGS_BEGIN
        "OO", &py_surface, &py_color
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);

    if(!RGBAFromColorObj (py_color, color))
        return Py_None;

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            getPixel_RGBA(surface, x, y, &r, &g, &b, &a);
            if(a==0) continue;
            setPixel_RGBA(surface, x, y, color[0], color[1], color[2], a );
        }
    }

    return Py_None;
}

/*
    Change alpha of surface
    method:
        0 alpha = alpha - shift
        1 alpha = alpha
        2 alpha = alpha * (shift/100)
*/
static PyObject*
setAlpha( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    int w,h,x,y = 0;
    SDL_PixelFormat *format = NULL;
    int shift;
    int method = 0;
    double percent = 0;
    Uint8 r,g,b,a;

    PY_PARSEARGS_BEGIN
        "Oi|i", &py_surface, &shift, &method
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);
    if( method == 1 ){
        shift = clampUint8( shift );
    }
    if( method == 2 ){
        percent = ((double)(shift))/100.0;
    }

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            getPixel_RGBA(surface, x, y, &r, &g, &b, &a );
            if(method == 0){
                a = a + shift;
                a = clampUint8( a );
            }
            if(method == 1){
                a = shift;
            }
            if(method == 2){
                a = a * percent;
            }
            setPixel_RGBA(surface, x, y, r, g, b, a );
        }
    }

    return Py_None;

}

/*
    Greyscale
    method:
        0 - avg RGB
        1 - HSV (saturation=0)
        2 - HSL (saturation=0)
*/
static PyObject*
greyscale( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_PixelFormat *format = NULL;
    SDL_Surface *surface;
    int w,h = 0;
    Uint8 r,g,b,a;
    int x,y;
    double hue,sat,val;
    int v;
    int method = 0;

    PY_PARSEARGS_BEGIN
        "O|i", &py_surface, &method
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);

    for(x = 0; x < w; x ++){
        for(y = 0; y < h; y ++){
            getPixel_RGBA(surface, x, y, &r, &g, &b, &a);
            if(method == 0){
                v = (r+g+b)/3.0;
                setPixel_RGBA(surface, x, y, v, v, v, a);
            } else if(method == 1){
                RGB2HSV( r, g, b, &hue, &sat, &val );
                HSV2RGB( hue, 0, val, &r, &g, &b );
                setPixel_RGBA(surface, x, y, r, g, b, a);
            } else if(method == 2){
                RGB2HSL( r, g, b, &hue, &sat, &val );
                HSL2RGB( hue, 0, val, &r, &g, &b );
                setPixel_RGBA(surface, x, y, r, g, b, a);
            }
        }
    }

    return Py_None;
}


/*
    Invert surface colors
*/
static PyObject*
invert( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    int w,h,pxcnt = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;
    Uint8 r,g,b,a;

    PY_PARSEARGS_BEGIN
        "O", &py_surface
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);
    pxcnt = w * h;

    while( pxcnt-- ){
        pixel = getPixelN(surface, pxcnt);
        SDL_GetRGBA( pixel, format, &r, &g, &b, &a );
        pixel = SDL_MapRGBA( format, 255-r, 255-g, 255-b, a );
        setPixelN(surface, pxcnt, pixel);
    }
    return Py_None;
}

/*
    Change hue of surface
    method: (only 0)
        0 - hue += shift
*/
static PyObject*
hue( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    int w,h,pxcnt = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;
    int shift = 0;
    int method = 0;
    Uint8 r,g,b,a;
    double hue,sat,val;

    PY_PARSEARGS_BEGIN
        "Oi|i", &py_surface, &shift, &method
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);
    pxcnt = w * h;

    while( pxcnt-- ){
        pixel = getPixelN(surface, pxcnt);
        SDL_GetRGBA( pixel, format, &r, &g, &b, &a );

        RGB2HSV( r,g,b, &hue, &sat, &val );

        if(method == 0){
            hue += (double)(shift);
        } else if(method == 1){
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
        HSV2RGB( hue, sat, val, &r, &g, &b );
        pixel = SDL_MapRGBA( format, r, g, b, a );
        setPixelN(surface, pxcnt, pixel);
    }
    return Py_None;
}

/*
    Change saturation of surface
    method:
        0 - sat += s_shift
        1 - sat = s_shift
        2 - sat =  sat * (s_shift/100.0)
*/
static PyObject*
saturation( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    int w,h,pxcnt = 0;
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

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);
    pxcnt = w * h;

    if( method == 2 ){
        percent = ((double)(shift))/100.0;
    }

    while( pxcnt-- ){
        pixel = getPixelN(surface, pxcnt);
        SDL_GetRGBA( pixel, format, &r, &g, &b, &a );

        RGB2HSV( r,g,b, &hue, &sat, &val );
        switch(method){
            case 0: sat += (double)(shift);break;
            case 1: sat = (double)(shift);break;
            case 2: sat = sat * percent;break;
        }

        /* clamp sat 0-100 */
        sat = clampValue( sat, 0.0, 100.0 );
        HSV2RGB( hue,sat,val, &r, &g, &b );
        pixel = SDL_MapRGBA( format, r, g, b, a );
        setPixelN(surface, pxcnt, pixel);
    }
    return Py_None;
}

/*
    Change value of surface
    method:
        0 - val += v_shift
        1 - val = v_shift
        2 - val =  val * (v_shift/100.0)
*/
static PyObject*
value( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    int w,h,pxcnt = 0;
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

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);
    pxcnt = w * h;

    if( method == 2 ){
        percent = ((double)(shift))/100.0;
    }
    while( pxcnt-- ){
        pixel = getPixelN(surface, pxcnt);
        SDL_GetRGBA( pixel, format, &r, &g, &b, &a );

        RGB2HSV( r,g,b, &hue, &sat, &val );
        switch(method){
            case 0: val += (double)(shift);break;
            case 1: val = (double)(shift);break;
            case 2: val = val * percent;break;
        }

        /* clamp sat 0-100 */
        val = clampValue( val, 0, 100 );
        HSV2RGB( hue,sat,val, &r, &g, &b );
        pixel = SDL_MapRGBA( format, r, g, b, a );
        setPixelN(surface, pxcnt, pixel);
    }
    return Py_None;
}

static PyObject*
lightness( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    int w,h,pxcnt = 0;
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

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);
    pxcnt = w * h;

    if( method == 2 ){
        percent = ((double)(shift))/100.0;
    }
    while( pxcnt-- ){
        pixel = getPixelN(surface, pxcnt);
        SDL_GetRGBA( pixel, format, &r, &g, &b, &a );

        RGB2HSL( r,g,b, &hue, &sat, &val );
        switch(method){
            case 0: val += (double)(shift);break;
            case 1: val = (double)(shift);break;
            case 2: val = val * percent;break;
        }

        /* clamp sat 0-100 */
        val = clampValue( val, 0.0, 100.0 );
        HSL2RGB( hue,sat,val, &r, &g, &b );
        pixel = SDL_MapRGBA( format, r, g, b, a );
        setPixelN(surface, pxcnt, pixel);
    }

    return Py_None;
}

/* Color multiply */
static PyObject*
multiply( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    int w,h,pxcnt = 0;
    SDL_PixelFormat *format = NULL;
    float shift = 1.0;
    float rp = 1.0, gp = 1.0, bp = 1.0;
    char rb = 1, gb = 1, bb = 1;
    Uint8 r,g,b,a;

    PY_PARSEARGS_BEGIN
        "Of|bbb", &py_surface, &shift, &rb, &gb, &bb
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);
    pxcnt = w * h;

    if(rb){rp = shift;}
    if(gb){gp = shift;}
    if(bb){bp = shift;}

    while( pxcnt-- ){
        getPixelN_RGBA(surface, pxcnt, &r, &g, &b, &a);

        r = clampUint8(r * rp);
        g = clampUint8(g * gp);
        b = clampUint8(b * bp);

        setPixelN_RGBA(surface, pxcnt, r, g, b, a);
    }

    return Py_None;
}


/*
    Replace pixels (hue == check_hue) with new_hue.
*/
static PyObject*
colorize( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
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

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            pixel = getPixel(surface, x, y);
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
            setPixel(surface, x, y, pixel);

        }
    }
    return Py_BuildValue("i", count );
}


/*
    Apply per-pixel alpha mask on surface
*/
static PyObject*
alphaMask( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    SDL_Surface *target_surface;
    int w,h,x,y,mw,mh = 0;
    SDL_PixelFormat *format = NULL;
    PyObject* py_surface_mask = NULL;
    SDL_Surface *surface_mask;
    SDL_PixelFormat *format_mask = NULL;

    Uint8 r,g,b,a,tmp_a;
    double hue,sat,val;
    int method = 0;
    float alpha,alpha2;

    PY_PARSEARGS_BEGIN
        "OO|i",
        &py_surface, &py_surface_mask, &method
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface_mask, &mw, &mh, &format_mask, &surface_mask);
    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);
    target_surface = createSurface( mw, mh );


    /*if(format->BytesPerPixel == 3){
        return RAISE (PyExc_ValueError, "input surface must be 32bit surface not 24bit");
    }*/

    if( mw != w || mh != h ){
        return RAISE (PyExc_ValueError, "mask must be same size as surface");
    }

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            /* get mask pixel*/
            getPixel_RGBA(surface_mask, x, y, &r, &g, &b, &a );

            if( method == 0 ){
                RGB2HSV( r,g,b, &hue, &sat, &val );
                alpha = (((float)val) / 100.0);
                /* set pixel */
                getPixel_RGBA(surface, x, y, &r, &g, &b, &a );
                tmp_a = (Uint8)( ((float)a) * alpha );
            } else if( method == 1 ){
                tmp_a = a;
                getPixel_RGBA(surface, x, y, &r, &g, &b, &a );
            } else if( method == 2 ){
                tmp_a = a;
                getPixel_RGBA(surface, x, y, &r, &g, &b, &a );
                /* alpha blend */
                alpha = ((float) a) / 255.0;
                alpha2 = ((float) tmp_a) / 255.0;
                tmp_a = (alpha * alpha2) * 255;
            } else if( method == 3 ){
                tmp_a = a;/*mask alpha*/
                getPixel_RGBA(surface, x, y, &r, &g, &b, &a );
                if(tmp_a > 0){/* if mask alpha > 0 then set original alpha */
                    tmp_a = a;
                }
            } else {
                tmp_a = 255;
            }

            setPixel_RGBA(target_surface, x, y, r, g, b, tmp_a);

        }
    }

    return PySurface_New( target_surface );
}


static PyMethodDef ColorMethods[] = {
    {"setColor", setColor, METH_VARARGS, "Set opaque pixels to color"},
    {"setAlpha", setAlpha, METH_VARARGS, "Set alpha channel of surface"},

    {"hue", hue, METH_VARARGS, "Hue"},
    {"saturation", saturation, METH_VARARGS, "Change saturation of surface"},
    {"value", value, METH_VARARGS, "Change value of surface"},
    {"lightness", lightness, METH_VARARGS, "Lightness"},
    {"multiply", multiply, METH_VARARGS, "Color multiply"},

    {"invert", invert, METH_VARARGS, "Invert colors of surface"},
    {"greyscale", greyscale, METH_VARARGS, "Create greyscale surface"},
    {"colorize", colorize, METH_VARARGS, "Change hue of surface"},

    {"alphaMask", alphaMask, METH_VARARGS, ""},
    {NULL, NULL, NULL, NULL}
};

PyMODINIT_FUNC initcolor(void)
{
    Py_InitModule("color", ColorMethods);
    import_pygame_surface();
    import_pygame_color();
}
