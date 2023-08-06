PyResizeImage  Copyright (C) 2013  Alkatron
This program comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it
under certain conditions; use -w options for details.
---------------------------------------------------------------------------
Resize images, and pad them to give an exact size image.
If not specified it creates a new folder named resized.<width>.<height> and copies
resized images into it with the same name.
- Images with a different aspect-ratio are padded with alpha channel(transparent).
- Images resized are in PNG format (to mantain transparent channel).

Module usage: 

        from pyrszimg.core import resize_img, resize_dir, VVERSION
        
        ResizedImage = resize_img(sourcefile, size)
        or
        dictResults=resize_dir(sourcedir,  size [,destdir ,formats])
        
        with dictResults={'total':<ImageFiles found (integer)>
                          'skipped':<ImageFiles skipped (integer)> 
                          'path_to':<destdir (string))>}
                       
---------------------------------------------------------------------------
Console usage: pyresizeimage [options]

Options:

-i, --input     :Folder containing images to resize

-s, --size      :Size of the producted images width/height

-o, --output    :(optional)Folder containing resized images default is 
                 <InputFolder>/resized.<width>.<height>

-f, --formats   :(optional)Image format to evaluate default is png/gif/jpg/jpeg

-w              :Show licence

Example:pyresizeimage -i ~/images -s 640/480
        pyresizeimage -i ~/images -s 640/480 -o ~/images/newpic -f gif/jpg


Install
-------
sudo pip install PIL
sudo pip install pyresizeimage
