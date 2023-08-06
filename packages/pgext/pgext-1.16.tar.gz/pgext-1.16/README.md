PyGame EXTension
=========
Small python extension (written in C) for pygame.Surface manipulation.
Created by Josef Vanžura <gindar@zamraky.cz>
http://zamraky.cz/projects/pgext/


## Dependecies

 * Python 2.5.4+
 * pygame 1.8+
 * SDL 1.2+, SDL_image

## Installation (Fedora)

1. Install dependencies (as root):

    ```yum install pygame-devel python-devel SDL-devel```

2. Download and extract pgext source package from pypi:

    ```http://pypi.python.org/pypi/pgext```

3. Install pgext (as root):

    ```python setup.py install```


## Installation (Ubuntu)

1. Add pygame development PPA

    ```sudo add-apt-repository ppa:pygame/pygame-dev```

2. Install header files and dependencies:

    ```sudo apt-get install python-dev pygame-dev libsdl-dev libsdl-image1.2-dev```

3. Download and extract pgext source package from pypi:

    ```http://pypi.python.org/pypi/pgext```

4. Install pgext:

    ```sudo python setup.py install```


## Installation (Windows)

1. Download and install python 2.7 32bit:

    ```http://python.org/ftp/python/2.7.3/python-2.7.3.msi```

2. Download and install pygame 1.9:

    ```http://pygame.org/ftp/pygame-1.9.1.win32-py2.7.msi```

3. Download and install pgext:

    ```http://zamraky.cz/projects/pgext/```


## Build from git repository (Fedora linux example)

    yum install pygame-devel python-devel SDL-devel
    git clone https://bitbucket.org/gindar/pgext.git
    cd pgext
    su -c python setup.py install

## Links

 * Project homepage: http://zamraky.cz/projects/pgext/
 * Python homepage: http://python.org
 * Pygame homepage: http://pygame.org
