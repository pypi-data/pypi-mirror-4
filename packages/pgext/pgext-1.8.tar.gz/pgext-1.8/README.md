PyGame EXTension
=========
Small python extension (written in C) for pygame.Surface manipulation.

## Dependecies
 * Python 2.5.4+
 * pygame 1.8+
 * SDL 1.2+

Installing (Example for Fedora)
```
$ yum install pygame-devel python-devel SDL-devel
```

## Installation (Linux)
```
$ git clone https://github.com/gindar/pgext.git
$ cd pgext
$ su -c python setup.py install
```

## Functions

 * filters
   * blur
   * shadow
   * noise
   * gradient (vertical, horizontal)
  
 * color
   * colorize
   * saturation
   * greyscale
   * setColor
  
