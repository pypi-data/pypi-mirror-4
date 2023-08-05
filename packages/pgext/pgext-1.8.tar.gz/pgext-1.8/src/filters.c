/*
    PGExt - pygame extension - filter
    Author: Josef Vanžura
    Required: Python 2.5+, PyGame 1.8.1+, SDL 1.2
*/
    
#include "pgext.h"

#define PGEXT_VERSION 5

#define MAX_SHADOW_VALUE 20

static void _blur( SDL_Surface *source, SDL_Surface *target, int radius, char vertical ){
    Uint32 pix;
    Uint8 r,g,b,a;
    double sr,sg,sb,sa;
    int color_cnt = 0;
    int x,y,ra,n,s,o1,o2;
    double r2;
    int w = source->w;
    int h = source->h;
    SDL_PixelFormat *source_format = (SDL_PixelFormat *)source->format;
    SDL_PixelFormat *target_format = (SDL_PixelFormat *)target->format;
    
    /* Surface pixels shorthand */
    Uint32 *source_pixels = (Uint32 *) source->pixels;
    Uint32 *target_pixels = (Uint32 *) target->pixels;

    s = (vertical)?h:w;
    o1 = (vertical)?1:0;
    o2 = (vertical)?0:1;
    r2 = radius*2+1;
    
    for( y = 0; y < h; y++ ){
        for( x = 0; x < w; x++ ){
            color_cnt = 0;sr = 0;sg = 0;sb = 0;sa = 0;
            n = (vertical)?y:x;
            
            for( ra = -radius; ra <= radius; ra++ ){
                if( (n+ra) >= 0 && (n+ra) < s ){
                    pix = source_pixels[(int)( ( (y + (ra * o1)) * w) + (x + (ra * o2)) )];
                    SDL_GetRGBA( pix, source_format, &r, &g, &b, &a );
                    sr += r;sg += g;sb += b;sa += a;
                    color_cnt++;
                }
            }
            sr = sr/r2;sg = sg/r2;
            sb = sb/r2;sa = sa/r2;
            pix = SDL_MapRGBA( target_format, (Uint8)sr, (Uint8)sg, (Uint8)sb, (Uint8)sa );
            target_pixels[ (y*w)+x ] = pix;
        }
    }   
}


/*
    Simple random noise. [RGB]*RAND
*/
static PyObject* noise( PyObject* self, PyObject* args )
{
    SURFACE_INIT
    int value = 255;
    int density = 5;
    Uint8 r,g,b,a;
    int rnd,tr,tg,tb;

    PY_PARSEARGS_BEGIN
        "O|ii", &py_surface,&value,&density
    PY_PARSEARGS_END

    SURFACE_PARAMS
    //srand();

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            if( rand()%density != 0 ) continue;
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, fmt, &r, &g, &b, &a );
            rnd = (value/2) - (rand()%value);
            tr = r+rnd;
            tg = g+rnd;
            tb = b+rnd;
            
            r = clampUint8(tr);
            g = clampUint8(tg);
            b = clampUint8(tb);
            
            pixel = SDL_MapRGBA( fmt, r, g, b, a );
            pixels[ (y*w)+x ] = pixel;

        }
    }
    
    Py_INCREF(Py_None);
    return Py_None;
}

/*
    Horizontal/vertical gradient.
*/
static PyObject* gradient( PyObject* self, PyObject* args )
{

    SDL_Surface *surface = NULL;
    PyObject *py_surface = NULL, *py_fcolor = NULL, *py_tcolor = NULL;
    SDL_PixelFormat *fmt = NULL;
    Uint32 *pixels = NULL;

    Uint32 pixel;
    Uint8 color[3];
    Uint8 fcolor[4];
    Uint8 tcolor[4];
    int x,y,i,q,w,h,dR,dG,dB,rows,cols;
    char vertical = 0;
    float ratio = 0.0;
    double nn,delta;
    
    
    PY_PARSEARGS_BEGIN
        "(ii)OO|bf", &w, &h, &py_fcolor, &py_tcolor, &vertical, &ratio
    PY_PARSEARGS_END
    
    if(!RGBAFromColorObj (py_fcolor, fcolor))
        return Py_None;
        
    if(!RGBAFromColorObj (py_tcolor, tcolor))
        return Py_None;


    surface = createSurface( w, h );
    pixels = (Uint32 *)surface->pixels;
    fmt = surface->format;

    dR = (int)(tcolor[0]-fcolor[0]);
    dG = (int)(tcolor[1]-fcolor[1]);
    dB = (int)(tcolor[2]-fcolor[2]);

    rows = vertical?h:w;
    cols = vertical?w:h;

    SDL_LockSurface (surface);
    for( i = 0; i < rows; i ++ ){
        delta = ((i+1)/(float)(rows+1));
        nn = pow( delta, ratio );

        color[0] = (Uint8)( fcolor[0] + ( dR * nn ) );
        color[1] = (Uint8)( fcolor[1] + ( dG * nn ) );
        color[2] = (Uint8)( fcolor[2] + ( dB * nn ) );

        pixel = SDL_MapRGB( fmt, color[0], color[1], color[2] );
        for( q = 0; q < cols; q ++ ){
            x = vertical?q:i;
            y = vertical?i:q;
            pixels[ ( y * w ) + x ] = pixel;
        }
    }
    SDL_UnlockSurface (surface);
    
    py_surface = PySurface_New( surface );
    Py_INCREF( py_surface );
    return Py_BuildValue("O", py_surface );
}

/*
    Create shadow from RGBA surface.
*/
static PyObject* shadow(PyObject* self, PyObject* args)
{
    PyObject *py_surface = NULL, *py_color = NULL;
    PySurfaceObject *surface;
    Uint32 *pixels;
    Uint32 pixel;
    int w,h,x,y;
    int rw,rh;
    int offset = 0;
    SDL_PixelFormat *fmt;
    Uint8 r,g,b,a;

    SDL_Surface *target_surface = NULL;
    Uint32 *target_pixels;
    SDL_Surface *temp_surface = NULL;
    PyObject *out_py_surface = NULL;

    Uint8 color[4];
    
    int radius = 5;
    float opacity = 1.0;
    char resized = 0;

    PY_PARSEARGS_BEGIN
        "OO|ibf", &py_surface, &py_color, &radius, &resized, &opacity
    PY_PARSEARGS_END
    
    if(!RGBAFromColorObj (py_color, color))
        return Py_None;

    if( radius > MAX_SHADOW_VALUE )
        radius = MAX_SHADOW_VALUE;
    
    surface = (PySurfaceObject*) py_surface;
    w = surface->surf->w;
    h = surface->surf->h;
    fmt = surface->surf->format;
    pixels = (Uint32 *)surface->surf->pixels;
    
    if( resized ){
        /* Set offsets for resized surface */
        rw = w + (radius*2);
        rh = h + (radius*2);
        offset = radius;
    } else {
        rw = w;rh = h;
        offset = 0;
    }

    /* Helper surfaces */
    target_surface = createSurface( rw, rh );
    target_pixels  = (Uint32 *)target_surface->pixels;
    temp_surface = createSurface( rw, rh );
    
    /* Lock surfaces for direct pixel set */
    SDL_LockSurface (temp_surface);
    SDL_LockSurface (target_surface);
    /* Set color & copy surface to target */
    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, fmt, &r, &g, &b, &a );
            a = (Uint8) (((double)a)*opacity);
            pixel = SDL_MapRGBA( fmt, color[0], color[1], color[2], a );
            target_pixels[ ( (y+offset) * rw)+( x+offset ) ] = pixel;
        }
    }
    SDL_UnlockSurface (temp_surface);
    SDL_UnlockSurface (target_surface);

    /* Switch target => temp with horizontal blur */
    _blur( target_surface, temp_surface, radius, 0 );
    /* Switch temp => target with vertical blur */
    _blur( temp_surface, target_surface, radius, 1 );
    
    /* Temp must be free */
    SDL_FreeSurface( temp_surface );
    
    out_py_surface = PySurface_New( target_surface );
    Py_INCREF( out_py_surface );
    return Py_BuildValue("O", out_py_surface );
}

/*
    Simple&fast blur
*/
static PyObject* blur(PyObject* self, PyObject* args)
{

    PyObject* py_surface = NULL;
    PySurfaceObject *surface;
    int w,h;

    SDL_Surface *temp_surface = NULL;
    int radius = 5;

    /* Parsovani pyArgumentu - radius by melo byt unsigned tiny int */
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
static PyObject* hvBlur(PyObject* self, PyObject* args)
{

    PyObject* py_surface = NULL;
    PySurfaceObject *surface;
    SDL_Surface *copy_surface = NULL;
    SDL_PixelFormat *fmt;
    int radius = 5;
    char vertical = 0;
    
    /* Parsovani pyArgumentu - radius by melo byt unsigned tiny int */
    PY_PARSEARGS_BEGIN
        "O|ib", &py_surface, &radius, &vertical
    PY_PARSEARGS_END
    
    surface = (PySurfaceObject*) py_surface;
    fmt = (SDL_PixelFormat *)surface->surf->format;
    
    /* Kopie je potreba kvuli zdrojovym pixelum */
    copy_surface = SDL_ConvertSurface(surface->surf, fmt, 0);
    
    /* Switch original => temp with vertical blur */
    _blur( copy_surface, surface->surf, radius, vertical );
    
    Py_INCREF( Py_None );
    return Py_None;
}

static PyMethodDef FiltersMethods[] = {
    {"gradient", gradient, METH_VARARGS, "Create vertical/horizontal gradient"},
    {"blur", blur, METH_VARARGS, "Blur surface"},
    {"hvBlur", hvBlur, METH_VARARGS, "Horizonal/vertical blur"},
    {"noise", noise, METH_VARARGS, "Simple surface noise"},
    {"shadow", shadow, METH_VARARGS, "Create RGBA surface shadow"},
    {NULL, NULL, NULL, NULL}
};

PyMODINIT_FUNC initfilters(void)
{
    PyObject *module = Py_InitModule("filters", FiltersMethods);
    import_pygame_surface();
    import_pygame_color();
    PyObject_SetAttrString(module, "version", PyLong_FromLong(PGEXT_VERSION));
}
