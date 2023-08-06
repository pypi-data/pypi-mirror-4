# -*- coding: utf-8 -*-
'''
    PyRszImg: Resize images, and pad them to give an exact size image
    Copyright (C) 2013  Alkatron, (alkatron@gmail.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import os, logging, sys
from PIL import Image, ImageChops, ImageOps

lggr = logging.getLogger('%s.%s' % (sys.argv[0],__name__))

# create null handler, altrimenti o scrive 2 volte,
# o va in errore se chiamato da modulo e lggr.error
#No handlers could be found for logger "gino.py.pyrszimg.core"  
ch = logging.NullHandler()
# add the handlers to the logger
lggr.addHandler(ch)

def resize_img(f_in, size):
    imge = Image.open(f_in)

    if imge.size[0]<size[0] and imge.size[1]<size[1]:
        src_width, src_height = imge.size
        if src_width>src_height:
            dst_width=size[0]
            dst_height= size[0]* src_height/src_width
        else:
            dst_height=size[1]
            dst_width= size[1]* src_width/src_height
        imge = imge.resize((dst_width, dst_height), Image.ANTIALIAS)
    else:
        imge.thumbnail(size, Image.ANTIALIAS)

    img_w,img_h=imge.size
    background = Image.new('RGBA', size, (0, 0, 0, 0))
    bg_w,bg_h=background.size
    offset=((bg_w-img_w)/2,(bg_h-img_h)/2)
    background.paste(imge,offset)
#    background.save(f_out,'PNG')
    return background

def resize_dir(_source, _size, _pthdst='' , _formats='jpg/jpeg/gif/png'):
    _ret = {'total':0,'skipped':0,'path_to':''}
    if not _pthdst:
        _pthdst=os.path.join(_source,'resized.%s' % ('.'.join([str(x) for x in _size])))
    if not os.path.isdir(_pthdst):
        os.mkdir(_pthdst)
    # Filtro i file sui formati
    # _formats.find('') torna 0 cosi gestisco anche i file senza estensione usando find>0  
    _ret['path_to']=_pthdst
    try:
        _size=[int(x) for x in _size.split('/') if int(x)]
        if len(_size)<>2: raise 
    except Exception: # as errore:
        lggr.error('Invalid size %s use the form width/height' % (_size))
        return _ret

    _formats='/' + _formats 
    flist=[_fls for _fls in os.listdir(_source) if _formats.find(os.path.splitext(_fls)[1][1:].lower()) > 0]
    nfiles=len(flist)    
    _ret['total']=nfiles
#    print 'gino'
    for fl in flist:
        lggr.info( "%i - Resizing image %s" % (nfiles, fl))
        _src=os.path.join(_source,fl)
        fl='%s.png'% (os.path.splitext(fl)[0])
        _dst=os.path.join(_pthdst,fl)
        # Open the image
        try:
            _img=resize_img(_src, size=_size)
        except Exception as _err:
            lggr.error( '     %s' % (_err))
            lggr.error( '     %s skipped!' % _src)
            _ret['skipped']+=1
        else:
            _img.save(_dst,'PNG')
        nfiles-=1
    return _ret
    
