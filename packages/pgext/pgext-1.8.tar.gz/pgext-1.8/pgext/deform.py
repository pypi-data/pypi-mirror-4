
import math
import random
import pygame

def scratch(srf,row_size=3,offset=10,phase=1.0,rect=None):
    if offset <= 0:return False
    _scratch(False,srf,row_size,offset,phase,rect)

def vscratch(srf,col_size=3,offset=10,phase=1.0,rect=None):
    if offset <= 0:return False
    _scratch(True,srf,col_size,offset,phase,rect)

def _scratch(vertical,srf,linesize,offset,phase,rect):
    if rect:
        dx = rect[0]
        dy = rect[1]
        siz = (rect[2],rect[3])
    else:
        dx = 0
        dy = 0
        siz = srf.get_size()
    if vertical:
        sizlines = siz[0]
        h = siz[1]
        w = linesize
    else:
        sizlines = siz[1]
        w = siz[0]
        h = linesize
    for line in xrange(sizlines/linesize):
        if vertical:
            x = line*linesize
            ox = x
            y = round(((offset*2) * random.random())-offset)*phase
            oy = 0
        else:
            y = line*linesize
            oy = y
            x = round(((offset*2) * random.random())-offset)*phase
            ox = 0
        srf.blit(srf,(int(x)+dx,int(y)+dy),(ox+dx,oy+dy,w,h))


def wave(surface,amp,freq,wphase,vert=True):
    siz = surface.get_size()
    if vert:
        for line in xrange(siz[1]):
            num = math.sin( (wphase+line)*freq )
            y = line
            x = amp*num
            surface.blit(surface,(int(x),int(y)),(0,y,siz[0],1))
    else:
        for line in xrange(siz[0]):
            num = math.sin( (wphase+line)*freq )
            x = line
            y = amp*num
            surface.blit(surface,(int(x),int(y)),(x,0,1,siz[1]))

def shake(surface,offset,phase,rect=None):
    v = offset*phase
    rx = random.random()
    ry = random.random()
    if rx > 0.5:rx = 1
    if ry > 0.5:ry = 1
    if rx < 0.5:rx = -1
    if ry < 0.5:ry = -1
    x = int( (rx*v)/2 )
    y = int( (ry*v) )
    if rect:
        rec = ( rect[0]+x,rect[1]+y,rect[2],rect[3] )
        surface.blit(surface,(rect[0],rect[1]),rec)
    else:
        surface.blit(surface,(x,y))
    return surface

def roundedCorners(surface):
    w,h = surface.get_size()
    clr = None
    for p in ((0,0),(0,h-1),(w-1,0),(w-1,h-1)):
        clr = surface.get_at(p)
        surface.set_at(p,(0,0,0,0))
    a = (clr[3]/3)*2
    for p in ( (1,0),(0,1),  (1,h-1),(0,h-2), (w-2,0),(w-1,1), (w-2,h-1),(w-1,h-2) ):
        surface.set_at(p,(clr[0],clr[1],clr[2],a))
    for p in ( (1,1),(1,h-2), (w-2,1), (w-2,h-2) ):
        surface.set_at(p,(clr[0],clr[1],clr[2],clr[3]/2))

def partialBlit(surface,target_surface, rects, blend=0, offset=(0,0)):
    for r in rects:
        target_surface.blit( surface, ( int(r[0]+offset[0]), int(r[1]+offset[1]) ), r, blend )
