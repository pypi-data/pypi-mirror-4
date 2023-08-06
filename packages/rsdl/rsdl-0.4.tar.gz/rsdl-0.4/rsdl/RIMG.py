import sys
from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.rtyper.tool import rffi_platform as platform
from rpython.translator.tool.cbuild import ExternalCompilationInfo
from rsdl import RSDL


if sys.platform == 'darwin':
    eci = ExternalCompilationInfo(
        includes = ['SDL_image.h'],
        frameworks = ['SDL_image'],
        include_dirs = ['/Library/Frameworks/SDL_image.framework/Headers']
    )
else:
    eci = ExternalCompilationInfo(
        includes=['SDL_image.h'],
        libraries=['SDL_image'],
    )

eci = eci.merge(RSDL.eci)

def external(name, args, result):
    return rffi.llexternal(name, args, result, compilation_info=eci)

Load = external('IMG_Load', [rffi.CCHARP], RSDL.SurfacePtr)
