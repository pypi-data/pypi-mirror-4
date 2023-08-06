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

/* Get pixel (from pygame surface.c) */
static Uint32 getPixel(SDL_Surface* surface, int x, int y)
{
    Uint8 *pixel;
    Uint32 color = 0;
    Uint8 *pixels = (Uint8 *) surface->pixels;
    SDL_PixelFormat *format = surface->format;

    if(format->BytesPerPixel == 3){
        pixel = ((Uint8 *) (pixels + y * surface->pitch) + x * 3);
#if SDL_BYTEORDER == SDL_LIL_ENDIAN
        color = (pixel[0]) + (pixel[1] << 8) + (pixel[2] << 16);
#else
        color = (pixel[2]) + (pixel[1] << 8) + (pixel[0] << 16);
#endif
    } else if(format->BytesPerPixel == 4){
        color = *((Uint32 *) (pixels + y * surface->pitch) + x);
    }
    return color;
}

static Uint32 getPixelN(SDL_Surface* surface, int n)
{
    int x=0, y=0;
    y = (int) (n / surface->w);
    x = (int) (n - y * surface->w);
    return getPixel(surface, x, y);
}

static void getPixel_RGBA(SDL_Surface* surface, int x, int y, Uint8 *r, Uint8 *g, Uint8 *b, Uint8 *a)
{
    Uint32 pixel = getPixel(surface, x, y);
    SDL_GetRGBA(pixel, surface->format, r, g, b, a);
}

static void getPixelN_RGBA(SDL_Surface* surface, int n, Uint8 *r, Uint8 *g, Uint8 *b, Uint8 *a)
{
    int x=0, y=0;
    y = (int) (n / surface->w);
    x = (int) (n - y * surface->w);
    SDL_GetRGBA(getPixel(surface, x, y), surface->format, r, g, b, a);
}




/* Set pixel (from pygame surface.c) */
static void setPixel(SDL_Surface* surface, int x, int y, Uint32 color)
{
    SDL_PixelFormat *format = surface->format;
    Uint8 *pixels = (Uint8 *) surface->pixels;
    Uint8 *byte_buf;

    if(format->BytesPerPixel == 3){
        byte_buf = (Uint8 *) (pixels + y * surface->pitch) + x * 3;
#if SDL_BYTEORDER == SDL_LIL_ENDIAN
        *(byte_buf + 2 - (format->Rshift >> 3)) = (Uint8) (color >> 16);
        *(byte_buf + 2 - (format->Gshift >> 3)) = (Uint8) (color >> 8);
        *(byte_buf + 2 - (format->Bshift >> 3)) = (Uint8) color;
#else
        *(byte_buf + (format->Rshift >> 3)) = (Uint8) (color >> 16);
        *(byte_buf + (format->Gshift >> 3)) = (Uint8) (color >> 8);
        *(byte_buf + (format->Bshift >> 3)) = (Uint8) color;
#endif
    } else if (format->BytesPerPixel == 4){

        *((Uint32 *) (pixels + y * surface->pitch) + x) = color;
    }
}

static void setPixelN(SDL_Surface* surface, int n, Uint32 color)
{
    int x=0, y=0;
    y = (int) (n / surface->w);
    x = (int) (n - y * surface->w);
    setPixel(surface, x, y, color);
}

static void setPixel_RGBA(SDL_Surface* surface, int x, int y, Uint8 r, Uint8 g, Uint8 b, Uint8 a)
{
    Uint32 color = SDL_MapRGBA( surface->format, r, g, b, a );
    setPixel(surface, x, y, color);
}

static void setPixelN_RGBA(SDL_Surface* surface, int n, Uint8 r, Uint8 g, Uint8 b, Uint8 a)
{
    Uint32 color;
    int x=0, y=0;

    y = (int) (n / surface->w);
    x = (int) (n - y * surface->w);
    color = SDL_MapRGBA( surface->format, r, g, b, a );
    setPixel(surface, x, y, color);
}
