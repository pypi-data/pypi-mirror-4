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

#include <math.h>
#include <stdlib.h>
#include <Python.h>
#include <pygame/pygame.h>
#include "getset.h"

/* Parsing PyArgs */
#define PY_PARSEARGS_BEGIN if( !PyArg_ParseTuple(args,
#define PY_PARSEARGS_END ) ) return Py_None;

#define clampUint8(N)  ( (N < 0) ? 0 : ((N > 255) ? 255 : N) )
#define clampValue(N,NMIN,NMAX)  ( (N < NMIN)?NMIN:((N > NMAX)?NMAX:N) )


static void getSurfaceAttrs(PyObject* py_surface, int *w, int *h,
    SDL_PixelFormat** format, SDL_Surface** surface);

SDL_Surface* createSurface( int width, int height );

SDL_Surface* createRGBSurface( int width, int height );



/* Get surface attributes format, size and pointer to surface itself */
static void
getSurfaceAttrs(PyObject* py_surface, int *w, int *h, SDL_PixelFormat** format, SDL_Surface** surface)
{
    PySurfaceObject* c_surface = (PySurfaceObject*) py_surface;

    *w = c_surface->surf->w;
    *h = c_surface->surf->h;
    *format = c_surface->surf->format;
    *surface = (SDL_Surface *)c_surface->surf;
    //*pixels = (Uint32 *) c_surface->surf->pixels;
}

static int
round_double(double d)
{
    int n = (int) d;
    double diff = d - (double)n;
    if(diff < 0)
        diff = -diff;
    if(diff >= 0.5)
    {
        return (d < 0) ? --n : ++n;
    }
    return n;
}


/* Create 32bit surface */
SDL_Surface*
createSurface( int width, int height ){
    #if SDL_BYTEORDER == SDL_BIG_ENDIAN
        return SDL_CreateRGBSurface(SDL_SWSURFACE, width, height, 32,
            0xFF000000, 0x00FF0000, 0x0000FF00, 0x000000FF);
    #else
        return SDL_CreateRGBSurface(SDL_SWSURFACE, width, height, 32,
            0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000);
    #endif
}

/* Create 24bit surface */
SDL_Surface*
createRGBSurface( int width, int height ){
    #if SDL_BYTEORDER == SDL_BIG_ENDIAN
        return SDL_CreateRGBSurface(SDL_SWSURFACE, width, height, 24,
            0xFF0000, 0x00FF00, 0x0000FF, 0);
    #else
        return SDL_CreateRGBSurface(SDL_SWSURFACE, width, height, 24,
            0x0000FF, 0x00FF00, 0xFF0000, 0);
    #endif
}


