/*
    PGExt - pygame extension - filter
    Author: Josef Vanžura
    Required: Python 2.5+, PyGame 1.8.1+, SDL 1.2
*/
    
#include "pgext.h"

#define PGEXT_VERSION 6

#define MAX_SHADOW_VALUE 20

/* simple horizontal/vertical blur */
static void _blur( SDL_Surface *source, SDL_Surface *target, int radius, char vertical ){
    Uint32 pix;
    Uint8 r,g,b,a;
    double sr,sg,sb,sa;
    int color_cnt = 0;
    int x,y,ra,n,s,o1,o2;
    double r2;
    int pxcnt = 0;

    /* Get sdl_surface attributes */
    int w = source->w;
    int h = source->h;
    SDL_PixelFormat *source_format = (SDL_PixelFormat *)source->format;
    SDL_PixelFormat *target_format = (SDL_PixelFormat *)target->format;
    Uint32 *source_pixels = (Uint32 *) source->pixels;
    Uint32 *target_pixels = (Uint32 *) target->pixels;

    /* Vertical/horizonal depending values */
    s = (vertical)?h:w;
    o1 = (vertical)?1:0;
    o2 = (vertical)?0:1;
    r2 = radius*2+1;
    
    SDL_LockSurface(source);
    SDL_LockSurface(target);
    for( y = 0; y < h; y++ ){
        for( x = 0; x < w; x++ ){
            color_cnt = 0;sr = 0;sg = 0;sb = 0;sa = 0;
            ra = -radius;
            n = (vertical)?y:x;

            /* Sum of pixel within radius */
            while( ra <= radius ){
                if( (n+ra) >= 0 && (n+ra) < s ){
                    pix = source_pixels[pxcnt + (int)( ((ra * o1) * w) + (ra * o2))];
                    SDL_GetRGBA( pix, source_format, &r, &g, &b, &a );
                    sr += r;sg += g;sb += b;sa += a;
                    color_cnt++;
                }
                ra++;
            }
            pxcnt++;
            if(sa == 0) continue;
            if(color_cnt <= 1) continue;

            /* average channel value */
            sr = sr / color_cnt;
            sg = sg / color_cnt;
            sb = sb / color_cnt;
            sa = sa / color_cnt;

            /* map & set pixel */
            pix = SDL_MapRGBA( target_format, (Uint8)sr, (Uint8)sg, 
                (Uint8)sb, (Uint8)sa);
            target_pixels[pxcnt-1] = pix;
        }
    }
    SDL_UnlockSurface(source);
    SDL_UnlockSurface(target);
}


/*
    Simple random noise. [RGB]+RAND
*/
static PyObject* noise( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    Uint32 *pixels;
    int w,h,x,y = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;

    int value = 255;
    int density = 5;
    Uint8 r,g,b,a;
    int rnd,tr,tg,tb;

    PY_PARSEARGS_BEGIN
        "O|ii", &py_surface, &value, &density
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);
    //srand();

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            if( rand()%density != 0 ) continue;
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, format, &r, &g, &b, &a );

            rnd = (value / 2) - (rand() % value);
            tr = r + rnd;
            tg = g + rnd;
            tb = b + rnd;
            r = clampUint8(tr);
            g = clampUint8(tg);
            b = clampUint8(tb);
            
            pixel = SDL_MapRGBA( format, r, g, b, a );
            pixels[ (y*w)+x ] = pixel;

        }
    }
    
    Py_INCREF(Py_None);
    return Py_None;
}


/*
    noise blur
*/
static PyObject* noiseBlur( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    Uint32 *pixels;
    int w,h,x,y = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;

    int radius = 5;
    char blend = 0;
    Uint8 r,g,b,a,tr,tg,tb,ta;
    int rnd,dx,dy;

    PY_PARSEARGS_BEGIN
        "O|ib", &py_surface, &radius, &blend
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);
    //srand();

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            dx = x + ((rand() % (radius * 2)) - radius);
            dy = y + ((rand() % (radius * 2)) - radius);
            if( dx < 0 || dx >= w || dx == x ) continue;
            if( dy < 0 || dy >= h || dy == y ) continue;
            pixel = pixels[(dy*w)+dx];
            SDL_GetRGBA( pixel, format, &r, &g, &b, &a );
            if(blend){
                pixel = pixels[(y*w)+x];
                SDL_GetRGBA( pixel, format, &tr, &tg, &tb, &ta );
                r = (tr + r)/2;
                g = (tg + g)/2;
                b = (tb + b)/2;
            }
            pixel = SDL_MapRGBA( format, r, g, b, a );
            pixels[ (y*w)+x ] = pixel;

        }
    }
    
    Py_INCREF(Py_None);
    return Py_None;
}


/*
    Simple image scratching.
*/
static PyObject* scratch( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    PySurfaceObject* c_surface;
    Uint32 *pixels;
    int w,h,x,y = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;

    int offset = 10;
    int rnd,tx;

    SDL_Surface *surface_copy = NULL;
    Uint32 *pixels_copy;

    PY_PARSEARGS_BEGIN
        "O|i", &py_surface, &offset
    PY_PARSEARGS_END

    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);

    c_surface = (PySurfaceObject *) py_surface;
    surface_copy = SDL_ConvertSurface(c_surface->surf, format, 0);
    pixels_copy = (Uint32 *)surface_copy->pixels;

    //srand();

    for( y = 0; y < h; y ++ ){
        rnd = (rand() % (offset*2)) - offset;
        for( x = 0; x < w; x ++ ){
            tx = rnd + x;
            if( tx < 0 ) continue;
            if( tx >= w ) continue;
            pixel = pixels_copy[(y*w)+x];
            pixels[ (y*w)+tx ] = pixel;
        }
    }
    
    SDL_FreeSurface(surface_copy);
    Py_INCREF(Py_None);
    return Py_None;
}

/*
    Simple image scratching.
*/
static PyObject* pixelize( PyObject* self, PyObject* args )
{
    PyObject* py_surface = NULL;
    PySurfaceObject* c_surface;
    Uint32 *pixels;
    int w,h,x,y,rx,ry = 0;
    Uint32 pixel;
    SDL_PixelFormat *format = NULL;

    int offset = 10;
    int halfoffset = 5;

    PY_PARSEARGS_BEGIN
        "O|ib", &py_surface, &offset
    PY_PARSEARGS_END

    halfoffset = (int) (((float) offset) / 2);

    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);

    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            rx = ((x / offset) * offset) + halfoffset;
            ry = ((y / offset) * offset) + halfoffset;
            if(rx >= w) rx = w - 1;
            if(ry >= h) ry = h - 1;
            pixel = pixels[(ry*w)+rx];
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
    SDL_PixelFormat *format = NULL;
    Uint32 *pixels = NULL;

    Uint32 pixel;
    Uint8 color[4];
    Uint8 fcolor[4];
    Uint8 tcolor[4];
    int x,y,i,q,w,h,dR,dG,dB,dA,rows,cols;
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
    format = surface->format;

    dR = (int)(tcolor[0]-fcolor[0]);
    dG = (int)(tcolor[1]-fcolor[1]);
    dB = (int)(tcolor[2]-fcolor[2]);
    dA = (int)(tcolor[3]-fcolor[3]);

    rows = vertical?h:w;
    cols = vertical?w:h;

    SDL_LockSurface (surface);
    for( i = 0; i < rows; i ++ ){
        delta = ((i+1)/(float)(rows+1));
        nn = pow( delta, ratio );

        color[0] = (Uint8)( fcolor[0] + ( dR * nn ) );
        color[1] = (Uint8)( fcolor[1] + ( dG * nn ) );
        color[2] = (Uint8)( fcolor[2] + ( dB * nn ) );
        color[3] = (Uint8)( fcolor[3] + ( dA * nn ) );

        pixel = SDL_MapRGBA( format, color[0], color[1], color[2], color[3] );
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
    Uint32 *pixels;
    Uint32 pixel;
    unsigned int w,h,x,y;
    int rw,rh;
    int offset = 0;
    SDL_PixelFormat *format;
    Uint8 r,g,b,a;

    SDL_Surface *target_surface = NULL;
    Uint32 *target_pixels;
    SDL_PixelFormat *target_format;
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
    
    getSurfaceAttrs(py_surface, &w, &h, &format, &pixels);
    
    if( resized ){
        /* Set offsets for resized surface */
        rw = w + (radius * 2);
        rh = h + (radius * 2);
        offset = radius;
    } else {
        rw = w;
        rh = h;
        offset = 0;
    }

    /* Helper surfaces */
    target_surface = createSurface( rw, rh );
    target_pixels  = (Uint32 *)target_surface->pixels;
    target_format = target_surface->format;
    temp_surface = createSurface( rw, rh );
    
    /* Lock surfaces for direct pixel set */
    SDL_LockSurface (temp_surface);
    SDL_LockSurface (target_surface);
    /* Set color & copy surface to target */
    for( y = 0; y < h; y ++ ){
        for( x = 0; x < w; x ++ ){
            pixel = pixels[(y*w)+x];
            SDL_GetRGBA( pixel, format, &r, &g, &b, &a );
            a = (Uint8) (((double)a)*opacity);
            pixel = SDL_MapRGBA( target_format, color[0], color[1], color[2], a );
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
    unsigned int w,h;

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
static PyObject* hvBlur(PyObject* self, PyObject* args)
{

    PyObject* py_surface = NULL;
    PySurfaceObject *surface;
    SDL_Surface *copy_surface = NULL;
    SDL_PixelFormat *format;
    unsigned int radius = 5;
    char vertical = 0;
    
    /* Parsovani pyArgumentu - radius by melo byt unsigned int */
    PY_PARSEARGS_BEGIN
        "O|ib", &py_surface, &radius, &vertical
    PY_PARSEARGS_END
    
    surface = (PySurfaceObject*) py_surface;
    format = (SDL_PixelFormat *)surface->surf->format;
    
    /* Kopie je potreba kvuli zdrojovym pixelum */
    copy_surface = SDL_ConvertSurface(surface->surf, format, 0);
    
    /* Switch original => temp with vertical blur */
    _blur( copy_surface, surface->surf, radius, vertical );
    
    SDL_FreeSurface(copy_surface);

    Py_INCREF( Py_None );
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
    {NULL, NULL, NULL, NULL}
};

PyMODINIT_FUNC initfilters(void)
{
    PyObject *module = Py_InitModule("filters", FiltersMethods);
    import_pygame_surface();
    import_pygame_color();
    PyObject_SetAttrString(module, "version", PyLong_FromLong(PGEXT_VERSION));
}
