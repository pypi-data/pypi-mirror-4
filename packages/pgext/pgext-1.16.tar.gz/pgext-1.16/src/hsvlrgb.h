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

int HSV2RGB( double ih, double is, double iv, Uint8 *r, Uint8 *g, Uint8 *b );

void RGB2HSV(Uint8 r, Uint8 g, Uint8 b, double *eh, double *es, double *ev);

int RGB2HSL(Uint8 r, Uint8 g, Uint8 b, double *eh, double *es, double *el);

int HSL2RGB(double eh, double es, double el, Uint8 *r, Uint8 *g, Uint8 *b);


/* copy&paste from internet :) */
int
HSV2RGB( double ih, double is, double iv, Uint8 *r, Uint8 *g, Uint8 *b )
{
    double hsv[4] = { 0, 0, 0 };
    double f, p, q, t, v, s;
    int hi;

    hsv[0] = ih;
    hsv[1] = is;
    hsv[2] = iv;

    s = hsv[1] / 100.f;
    v = hsv[2] / 100.f;

    hi = (int) floor (hsv[0] / 60.f);
    f = (hsv[0] / 60.f) - hi;
    p = v * (1 - s);
    q = v * (1 - s * f);
    t = v * (1 - s * (1 - f));

    switch (hi)
    {
    case 0:
        *r = (Uint8) (v * 255);
        *g = (Uint8) (t * 255);
        *b = (Uint8) (p * 255);
        break;
    case 1:
        *r = (Uint8) (q * 255);
        *g = (Uint8) (v * 255);
        *b = (Uint8) (p * 255);
        break;
    case 2:
        *r = (Uint8) (p * 255);
        *g = (Uint8) (v * 255);
        *b = (Uint8) (t * 255);
        break;
    case 3:
        *r = (Uint8) (p * 255);
        *g = (Uint8) (q * 255);
        *b = (Uint8) (v * 255);
        break;
    case 4:
        *r = (Uint8) (t * 255);
        *g = (Uint8) (p * 255);
        *b = (Uint8) (v * 255);
        break;
    case 5:
        *r = (Uint8) (v * 255);
        *g = (Uint8) (p * 255);
        *b = (Uint8) (q * 255);
        break;
    default:
        return -1;
    }

    return 0;
}


/* copy&paste from internet :) */
void
RGB2HSV(Uint8 r, Uint8 g, Uint8 b, double *eh, double *es, double *ev)
{
   float min, max, delta, rc, gc, bc, h,s,v;
   h = 0.0;

   rc = (float)r / 255.0;
   gc = (float)g / 255.0;
   bc = (float)b / 255.0;
   max = MAX(rc, MAX(gc, bc));
   min = MIN(rc, MIN(gc, bc));
   delta = max - min;
   v = max;

   if (max != 0.0)
      s = delta / max;
   else
      s = 0.0;

   if (s == 0.0) {
      h = 0.0;
   }
   else {
      if (rc == max)
     h = (gc - bc) / delta;
      else if (gc == max)
     h = 2 + (bc - rc) / delta;
      else if (bc == max)
     h = 4 + (rc - gc) / delta;

      h *= 60.0;
      if (h < 0)
     h += 360.0;
    }

    *eh = (double)h;
    *es = (double)(s*100);
    *ev = (double)(v*100);
}


int
RGB2HSL(Uint8 r, Uint8 g, Uint8 b, double *eh, double *es, double *el)
{
    double hsl[3] = { 0, 0, 0 };
    double frgb[3];
    double minv, maxv, diff;

    /* Normalize */
    frgb[0] = ((double)r) / 255.0;
    frgb[1] = ((double)g) / 255.0;
    frgb[2] = ((double)b) / 255.0;

    maxv = MAX (MAX (frgb[0], frgb[1]), frgb[2]);
    minv = MIN (MIN (frgb[0], frgb[1]), frgb[2]);

    diff = maxv - minv;

    /* Calculate L */
    hsl[2] = 50.f * (maxv + minv); /* 1/2 (max + min) */

    if (maxv == minv)
    {
        *eh = 0;
        *es = 0;
        *el = (double)hsl[2];
        return 0;
    }

    /* Calculate S */
    if (hsl[2] <= 50)
        hsl[1] = diff / (maxv + minv);
    else
        hsl[1] = diff / (2 - maxv - minv);
    hsl[1] *= 100.f;

    /* Calculate H */
    if (maxv == frgb[0])
        hsl[0] = fmod ((60 * ((frgb[1] - frgb[2]) / diff)), 360.f);
    else if (maxv == frgb[1])
        hsl[0] = (60 * ((frgb[2] - frgb[0]) / diff)) + 120.f;
    else
        hsl[0] = (60 * ((frgb[0] - frgb[1]) / diff)) + 240.f;
    if (hsl[0] < 0)
        hsl[0] += 360.f;

    /* H,S,L */
    *eh = (double)hsl[0];
    *es = (double)hsl[1];
    *el = (double)hsl[2];

    return 1;
}


int
HSL2RGB(double eh, double es, double el, Uint8 *r, Uint8 *g, Uint8 *b)
{
    double ht, h, q, p = 0, s, l = 0;
    static double onethird = 1.0 / 3.0f;

    s = es / 100.f;
    l = el / 100.f;

    if (s == 0)
    {
        *r = (Uint8) (l * 255);
        *g = (Uint8) (l * 255);
        *b = (Uint8) (l * 255);
        return 0;
    }

    if (l < 0.5f)
        q = l * (1 + s);
    else
        q = l + s - (l * s);
    p = 2 * l - q;

    ht = eh / 360.f;

    /* Calulate R */
    h = ht + onethird;
    if (h < 0)
        h += 1;
    else if (h > 1)
        h -= 1;

    if (h < 1./6.f)
        *r = (Uint8) ((p + ((q - p) * 6 * h)) * 255);
    else if (h < 0.5f)
        *r = (Uint8) (q * 255);
    else if (h < 2./3.f)
        *r = (Uint8) ((p + ((q - p) * 6 * (2./3.f - h))) * 255);
    else
        *r = (Uint8) (p * 255);

    /* Calculate G */
    h = ht;
    if (h < 0)
        h += 1;
    else if (h > 1)
        h -= 1;

    if (h < 1./6.f)
        *g = (Uint8) ((p + ((q - p) * 6 * h)) * 255);
    else if (h < 0.5f)
        *g = (Uint8) (q * 255);
    else if (h < 2./3.f)
        *g = (Uint8) ((p + ((q - p) * 6 * (2./3.f - h))) * 255);
    else
        *g = (Uint8) (p * 255);

    /* Calculate B */
    h = ht - onethird;
    if (h < 0)
        h += 1;
    else if (h > 1)
        h -= 1;

    if (h < 1./6.f)
        *b = (Uint8) ((p + ((q - p) * 6 * h)) * 255);
    else if (h < 0.5f)
        *b = (Uint8) (q * 255);
    else if (h < 2./3.f)
        *b = (Uint8) ((p + ((q - p) * 6 * (2./3.f - h))) * 255);
    else
        *b = (Uint8) (p * 255);

    return 0;
}
