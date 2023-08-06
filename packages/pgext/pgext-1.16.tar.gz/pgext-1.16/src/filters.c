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

static SDL_Surface*
_shadow( SDL_Surface *surface, int radius, float opacity, int w, int h, int rw, int rh, int offset, Uint8 color[4] );

static void
_blur( SDL_Surface *source, SDL_Surface *target, int radius, char vertical );

static SDL_Surface*
_gradient( int w, int h, Uint8 fcolor[4], Uint8 tcolor[4], char vertical, float ratio );



static SDL_Surface*
_shadow( SDL_Surface *surface, int radius, float opacity, int w, int h, int rw, int rh, int offset, Uint8 color[4] )
{
    int x,y;
    Uint8 r,g,b,a;
    SDL_Surface *target_surface = NULL;
    SDL_Surface *temp_surface = NULL;

    /* Helper surfaces */
    target_surface = createSurface( rw, rh );
    temp_surface = createSurface( rw, rh );

    /* Lock surfaces for direct pixel set */
    SDL_LockSurface (temp_surface);
    SDL_LockSurface (target_surface);
    /* Set color & copy surface to target */
    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            getPixel_RGBA(surface, x, y, &r, &g, &b, &a );
            if(a == 0) continue;
            if(opacity < 1){
                a = (Uint8) (((double)a) * opacity);
            }
            setPixel_RGBA(target_surface, x + offset, y + offset, color[0], color[1], color[2], a);
        }
    }
    SDL_UnlockSurface (temp_surface);
    SDL_UnlockSurface (target_surface);

    /* target => temp with horizontal blur */
    _blur( target_surface, temp_surface, radius, 0 );
    /* temp => target with vertical blur */
    _blur( temp_surface, target_surface, radius, 1 );

    /* Temp must be free */
    SDL_FreeSurface( temp_surface );
    return target_surface;
}




/* simple horizontal/vertical blur */
static void
_blur( SDL_Surface *source, SDL_Surface *target, int radius, char vertical )
{
    Uint8 r,g,b,a;
    int color_cnt = 0;
    int x,y,ra,n,s,o1,o2;
    Uint8 color[4];
    double sumcolor[4];

    /* Get sdl_surface attributes */
    int w = source->w;
    int h = source->h;

    /* Vertical/horizonal depending values */
    s = (vertical)?h:w;
    o1 = (vertical)?1:0;
    o2 = (vertical)?0:1;

    SDL_LockSurface(source);
    SDL_LockSurface(target);
    for( y = 0; y < h; y++ ){
        for( x = 0; x < w; x++ ){
            color_cnt = 0;
            sumcolor[0] = 0;
            sumcolor[1] = 0;
            sumcolor[2] = 0;
            sumcolor[3] = 0;
            ra = -radius;
            n = (vertical)?y:x;

            /* Sum of pixels within radius */
            while( ra <= radius ){
                if( (n + ra) == s ) break;
                if( (n + ra) >= 0 ){
                    getPixel_RGBA(source, x + (ra * o2), y + (ra * o1),
                        &r, &g, &b, &a);
                    sumcolor[0] += r;
                    sumcolor[1] += g;
                    sumcolor[2] += b;
                    sumcolor[3] += a;
                    color_cnt++;
                }
                ra++;
            }
            //if(sa == 0) continue;
            if(sumcolor[3] == 0) continue;
            if(color_cnt <= 1) continue;

            /* average channel value */
            color[0] = sumcolor[0] / color_cnt;
            color[1] = sumcolor[1] / color_cnt;
            color[2] = sumcolor[2] / color_cnt;
            color[3] = sumcolor[3] / color_cnt;

            /* map & set pixel */
            setPixel_RGBA(target, x, y, color[0], color[1], color[2], color[3]);
        }
    }
    SDL_UnlockSurface(source);
    SDL_UnlockSurface(target);
}


static SDL_Surface*
_gradient( int w, int h, Uint8 fcolor[4], Uint8 tcolor[4], char vertical, float ratio )
{
    SDL_Surface *surface = NULL;
    SDL_PixelFormat *format = NULL;
    Uint32 pixel;
    Uint8 color[4];
    int dcolor[4];
    int x,y,i,q,rows,cols;
    double nn,delta;


    dcolor[0] = (int)(tcolor[0]-fcolor[0]);
    dcolor[1] = (int)(tcolor[1]-fcolor[1]);
    dcolor[2] = (int)(tcolor[2]-fcolor[2]);
    dcolor[3] = (int)(tcolor[3]-fcolor[3]);

    surface = createSurface( w, h );
    format = surface->format;

    rows = vertical?h:w;
    cols = vertical?w:h;

    SDL_LockSurface (surface);
    for( i = 0; i < rows; i ++ ){
        delta = ((i+1)/(float)(rows+1));
        nn = pow( delta, ratio );

        color[0] = (Uint8)( fcolor[0] + ( dcolor[0] * nn ) );
        color[1] = (Uint8)( fcolor[1] + ( dcolor[1] * nn ) );
        color[2] = (Uint8)( fcolor[2] + ( dcolor[2] * nn ) );
        color[3] = (Uint8)( fcolor[3] + ( dcolor[3] * nn ) );

        pixel = SDL_MapRGBA( format, color[0], color[1], color[2], color[3] );
        for( q = 0; q < cols; q ++ ){
            x = vertical?q:i;
            y = vertical?i:q;
            setPixel(surface, x, y, pixel);
        }
    }
    SDL_UnlockSurface (surface);
    return surface;
}



/*
    Simple random noise. [RGB]+RAND
*/
static PyObject*
noise( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    int w,h,x,y = 0;
    SDL_PixelFormat *format = NULL;

    int cnt = 0;
    int value = 255;
    int density = 5;
    Uint8 r,g,b,a;
    int rnd,tr,tg,tb;

    PY_PARSEARGS_BEGIN
        "O|ii", &py_surface, &value, &density
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);
    //srand();

    cnt = (w * h) / density;
    for( ;; ){

        x = (rand() % w);
        y = (rand() % h);

        getPixel_RGBA(surface, x, y, &r, &g, &b, &a );

        rnd = (value / 2) - (rand() % value);
        tr = r + rnd;
        tg = g + rnd;
        tb = b + rnd;
        r = clampUint8(tr);
        g = clampUint8(tg);
        b = clampUint8(tb);

        setPixel_RGBA(surface, x, y, r, g, b, a);

        cnt--;
        if(cnt < 0) break;
    }

    return Py_None;
}


/*
    noise blur
*/
static PyObject*
noiseBlur( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    int w,h,x,y;
    SDL_PixelFormat *format = NULL;

    int radius = 5;
    char blend = 0;
    Uint8 r,g,b,a,tr,tg,tb,ta;
    int dx,dy;

    PY_PARSEARGS_BEGIN
        "O|ib", &py_surface, &radius, &blend
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);
    //srand();

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            dx = x + ((rand() % (radius * 2)) - radius);
            dy = y + ((rand() % (radius * 2)) - radius);
            if( dx < 0 || dx >= w || dx == x ) continue;
            if( dy < 0 || dy >= h || dy == y ) continue;
            getPixel_RGBA(surface, dx, dy, &r, &g, &b, &a );
            if(blend){
                getPixel_RGBA(surface, x, y, &tr, &tg, &tb, &ta );
                r = (tr + r) / 2;
                g = (tg + g) / 2;
                b = (tb + b) / 2;
            }
            setPixel_RGBA(surface, x, y, r, g, b, a);
        }
    }

    return Py_None;
}


/*
    Simple image scratching.
*/
static PyObject*
scratch( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    int w,h,x,y = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;

    int offset = 10;
    int rnd,tx;

    SDL_Surface *surface_copy = NULL;

    PY_PARSEARGS_BEGIN
        "O|i", &py_surface, &offset
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);

    surface_copy = SDL_ConvertSurface(surface, format, 0);

    //srand();

    for( y = 0; y < h; y ++ ){
        rnd = (rand() % (offset*2)) - offset;
        for( x = 0; x < w; x ++ ){
            tx = rnd + x;
            if( tx < 0 ) continue;
            if( tx >= w ) continue;
            pixel = getPixel(surface_copy, x, y);
            setPixel(surface, tx, y, pixel);
        }
    }

    SDL_FreeSurface(surface_copy);
    return Py_None;
}

/*
    Simple image scratching.
*/
static PyObject*
pixelize( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    SDL_Surface *surface;
    int w,h,x,y,rx,ry = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;

    int offset = 10;
    int halfoffset = 5;

    PY_PARSEARGS_BEGIN
        "O|ib", &py_surface, &offset
    PY_PARSEARGS_END

    halfoffset = (int) (((float) offset) / 2);

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            rx = ((x / offset) * offset) + halfoffset;
            ry = ((y / offset) * offset) + halfoffset;
            if(x == rx && y == ry) continue;
            if(rx >= w) rx = w - 1;
            if(ry >= h) ry = h - 1;
            pixel = getPixel(surface, rx, ry);
            setPixel(surface, x, y, pixel);

        }
    }

    return Py_None;
}


/*
    Horizontal/vertical gradient.
*/
static PyObject*
gradient( PyObject* self, PyObject* args )
{

    SDL_Surface *surface = NULL;
    PyObject *py_fcolor = NULL, *py_tcolor = NULL;
    Uint8 fcolor[4];
    Uint8 tcolor[4];
    int w,h;
    char vertical = 0;
    float ratio = 0.0;


    PY_PARSEARGS_BEGIN
        "(ii)OO|bf", &w, &h, &py_fcolor, &py_tcolor, &vertical, &ratio
    PY_PARSEARGS_END

    if(!RGBAFromColorObj (py_fcolor, fcolor))
        return Py_None;

    if(!RGBAFromColorObj (py_tcolor, tcolor))
        return Py_None;

    surface = _gradient(w, h, fcolor, tcolor, vertical, ratio);

    return PySurface_New( surface );
}

/*
    Create shadow from RGBA surface.
*/
static PyObject*
shadow(PyObject* self, PyObject* args)
{
    PyObject *py_surface = NULL, *py_color = NULL;
    SDL_Surface *surface;
    int w,h;
    SDL_PixelFormat *format;
    Uint8 color[4];
    SDL_Surface *target_surface = NULL;

    int radius = 5;
    float opacity = 1.0;
    char resized = 0;

    PY_PARSEARGS_BEGIN
        "OO|ibf", &py_surface, &py_color, &radius, &resized, &opacity
    PY_PARSEARGS_END

    if(!RGBAFromColorObj (py_color, color)) return Py_None;
    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);

    /* only 32bit surfaces are supported */
    if(format->BytesPerPixel == 3){
        return RAISE (PyExc_ValueError, "input surface must be 32bit surface not 24bit");
    }

    if( resized ){
        /* Set offsets for resized surface */
        target_surface = _shadow(surface, radius, opacity, w, h,
            (w + (radius * 2)), (h + (radius * 2)),
            radius, color );
    } else {
        target_surface = _shadow( surface, radius, opacity,
            w, h, w, h, 0, color );
    }

    return PySurface_New( target_surface );
}

/*
    Simple&fast blur
*/
static PyObject*
blur(PyObject* self, PyObject* args)
{

    PyObject* py_surface = NULL;
    PySurfaceObject *surface;
    int w,h;

    SDL_Surface *temp_surface = NULL;
    unsigned int radius = 5;

    /* Parsovani pyArgumentu - radius by melo byt unsigned int */
    PY_PARSEARGS_BEGIN
        "O|i", &py_surface, &radius
    PY_PARSEARGS_END

    surface = (PySurfaceObject*) py_surface;
    w = surface->surf->w;
    h = surface->surf->h;

    /* Kopie je potreba kvuli zdrojovym pixelum */
    temp_surface = createSurface( w, h );

    /* Switch original => temp with horizontal blur */
    _blur( surface->surf, temp_surface, radius, 0 );
    /* Switch temp => target with vertical blur */
    _blur( temp_surface, surface->surf, radius, 1 );

    SDL_FreeSurface( temp_surface );

    return Py_None;
}

/*
    Simple&fast blur
*/
static PyObject*
hvBlur(PyObject* self, PyObject* args)
{
    PyObject* py_surface = NULL;
    PySurfaceObject *surface;
    SDL_Surface *copy_surface = NULL;
    unsigned int radius = 5;
    char vertical = 0;

    /* Parsovani pyArgumentu - radius by melo byt unsigned int */
    PY_PARSEARGS_BEGIN
        "O|ib", &py_surface, &radius, &vertical
    PY_PARSEARGS_END

    surface = (PySurfaceObject*) py_surface;

    /* Kopie je potreba kvuli zdrojovym pixelum */
    copy_surface = SDL_ConvertSurface(surface->surf, surface->surf->format, 0);

    /* Switch original => temp with vertical blur */
    _blur( copy_surface, surface->surf, radius, vertical );

    SDL_FreeSurface(copy_surface);

    return Py_None;
}

/*
    Simple&fast ripple effect
*/
static PyObject*
ripple(PyObject* self, PyObject* args)
{
    PyObject* py_surface = NULL;
    int w,h,o,i,j,imax,jmax;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;

    SDL_Surface *surface = NULL;
    SDL_Surface *copy_surface = NULL;

    int frequency = 10;
    int amplitude = 5;
    double phase = 0.0;
    char vertical = 0;

    double offset = 0;
    double q;

    /* python arguments parsing*/
    PY_PARSEARGS_BEGIN
        "Oii|db", &py_surface, &frequency, &amplitude, &phase, &vertical
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &surface);

    /* surface copy is needed for source pixels  */
    copy_surface = SDL_ConvertSurface(surface, format, 0);

    imax = vertical ? w : h;
    jmax = vertical ? h : w;

    for( i = 0; i < imax; i++ ){
        q = ((double)(i % frequency)) / ((double) frequency);
        offset = sin((q + phase) * 3.1415 * 2) * ((double)amplitude);
        for( j = 0; j < jmax; j++ ){
            o = (int) round_double(j + offset);
            if(o < 0) o = jmax - o;
            if(o >= jmax) o = o - jmax;
            if(vertical){
                pixel = getPixel(copy_surface, i, o);
                setPixel(surface, i, j, pixel);
            } else {
                pixel = getPixel(copy_surface, o, i);
                setPixel(surface, j, i, pixel);
            }
        }
    }

    SDL_FreeSurface( copy_surface );

    return Py_None;
}


static PyMethodDef FiltersMethods[] = {
    {"gradient", gradient, METH_VARARGS, "Create vertical/horizontal gradient"},
    {"blur", blur, METH_VARARGS, "Blur surface"},
    {"hvBlur", hvBlur, METH_VARARGS, "Horizonal/vertical blur"},
    {"noise", noise, METH_VARARGS, "Simple surface noise"},
    {"noiseBlur", noiseBlur, METH_VARARGS, "Simple surface noise"},
    {"shadow", shadow, METH_VARARGS, "Create RGBA surface shadow"},
    {"scratch", scratch, METH_VARARGS, "Create RGBA surface shadow"},
    {"pixelize", pixelize, METH_VARARGS, "Fast pixelize effect"},
    {"ripple", ripple, METH_VARARGS, "Simple ripple effect"},
    {NULL, NULL, NULL, NULL}
};

PyMODINIT_FUNC initfilters(void)
{
    Py_InitModule("filters", FiltersMethods);
    import_pygame_surface();
    import_pygame_color();
}
