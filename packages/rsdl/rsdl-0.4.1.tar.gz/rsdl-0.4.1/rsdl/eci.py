from rpython.translator.tool.cbuild import ExternalCompilationInfo
from rpython.translator.platform import CompilationError
import py
import sys
import os

def get_rsdl_compilation_info():
    if sys.platform == 'darwin':
        eci = ExternalCompilationInfo(
            includes = ['SDL.h'],
            include_dirs = ['/Library/Frameworks/SDL.framework/Headers'],
            link_files = [
                str(py.path.local(__file__).dirpath().join('macosx-sdl-main/SDLMain.m')),
            ],
            frameworks = ['SDL', 'Cocoa']
        )
    elif sys.platform == "win32":
        try:
            sdl_prefix = os.path.abspath(os.environ["SDL_PREFIX"])
        except KeyError:
            print "You need to provide the path to SDL using the SDL_PREFIX environment variable"
            exit(1)

        # XXX: SDL_main.h does a #define main SDL_main
        # This causes a linker error with the VS C compiler
        # The solution is to #undef main before we define our own
        this_dir = os.path.dirname(__file__)
        f = open(os.path.join(this_dir, "RSDL_undef_main.h"), "w")
        print >> f, "#undef main"
        f.close()

        eci = ExternalCompilationInfo(
            includes = ['SDL.h', 'RSDL_undef_main.h'],
            include_dirs = [os.path.join(sdl_prefix, "include"), this_dir],
            link_files = [
                os.path.join(sdl_prefix, "lib", "x86", "SDLmain.lib"),
                os.path.join(sdl_prefix, "lib", "x86", "SDL.lib")
            ],
            libraries = ["SDL"],
            library_dirs = [os.path.join(sdl_prefix, "lib", "x86")],
        )
    else:
        eci = ExternalCompilationInfo(
            includes=['SDL.h'],
            )
        eci = eci.merge(ExternalCompilationInfo.from_config_tool('sdl-config'))
    return eci

def check_sdl_installation():
    from pypy.rpython.tool import rffi_platform as platform
    platform.verify_eci(get_rsdl_compilation_info())

SDLNotInstalled = (ImportError, CompilationError)
