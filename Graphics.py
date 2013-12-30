# BastionMod - Graphics
# Manages the extraction and compilation of graphics files from Bastion.
#
# Copyright © 2013 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from copy import deepcopy
from glob import glob
import math
from multiprocessing import Process
import os
import struct
import xml.dom.minidom as X

from Common import *

try:
    from PIL import Image
except ImportError:
    print('PIL not found. Make sure the Python Imaging Libary is installed.')

# Import the CModules.
try:
    import bm_dxt
    import bm_lzx
except ImportError:
    print('Failed to find CModules. Run \'build_CModules.py build\' first.')
    import sys
    sys.exit()


class PKG:
    """Manages a package file's data."""

    VERSION = 0x5

    ATLAS = 0xDE
    TEXTURE = 0xAD
    NEXT = 0xBE

    def __init__(self, file_path, debug=False):
        """Loads the PKG's data (atlases and XNB textures."""

        self.name = os.path.splitext(os.path.basename(file_path))[0]
        if os.path.basename(os.path.dirname(file_path)) == '720p':
            self.name += '_720p'
        self.version = 0
        self.debug = debug

        print('  {}'.format(self.name))
        try:
            with open(file_path, 'rb') as f:
                self.atlases = self.load_atlases(f)
        except (OSError, IOError):
            raise GraphicsError('Failed to open PKG.')

    def load_atlases(self, f):
        """Loads all the atlases contained within the file."""

        atlases = []
        current_atlas = None

        # Load the header.
        self.version = struct.unpack('>I', f.read(0x4))[0]
        if self.version != PKG.VERSION:
            raise GraphicsError('Invalid PKG file.')

        # Load the atlases and textures, and combine them to obtain images.
        while True:
            asset_type = ord(f.read(1))

            if asset_type == PKG.ATLAS:  # Atlas definition
                # Load the atlas' header.
                current_atlas = Atlas()
                atlases.append(current_atlas)
                next_asset, num_images = struct.unpack('>II', f.read(0x8))

                # Load the images' data.
                for j in range(0, num_images):
                    name = read_string(f)
                    image = AtlasImage(name, *struct.unpack('>iiiiiiiiff',
                        f.read(0x28)))
                    current_atlas.add_image(image)

            elif asset_type == PKG.TEXTURE:  # Texture file
                # Load the texture's header.
                name = read_string(f)
                size = struct.unpack('>I', f.read(4))[0]
                texture = Texture(name, f.read(size), self.debug)
                print('    Texture: {}'.format(name))

                if current_atlas:
                    current_atlas.apply_texture(texture)
                    current_atlas = None
                else:
                    atlas = Atlas(True)
                    atlases.append(atlas)
                    image = AtlasImage(name, 0, 0, texture.width,
                        texture.height, 0, 0, texture.width, texture.height,
                        1.0, 1.0
                    )
                    atlas.add_image(image)
                    atlas.apply_texture(texture)
                    del atlas

            elif asset_type == PKG.NEXT:  # Skip to next chunk
                next_chunk = math.ceil(f.tell() / 0x800000) * 0x800000
                f.seek(next_chunk)

            elif asset_type == 0xFF:  # End of file
                break

            else:
                raise GraphicsError('Invalid asset type.')

        return atlases

    def save_xml(self, file_path):
        """Saves the PKG's data to an XML file."""

        # Build the XML data.
        impl = X.getDOMImplementation()
        doc = impl.createDocument(None, 'PKG', None)
        root = doc.documentElement
        root.setAttribute('Name', self.name)
        root.setAttribute('Version', str(self.version))
        for a in self.atlases:
            atlas = doc.createElement('Atlas')
            atlas.setAttribute('Virtual', str(int(a.virtual)))
            atlas.setAttribute('Texture', a.texture.name)
            atlas.setAttribute('Format', str(a.texture.format))
            atlas.setAttribute('Width', str(a.texture.width))
            atlas.setAttribute('Height', str(a.texture.height))
            for i in a.images:
                image = doc.createElement('Image')
                image.setAttribute('Name', i.name)
                image.setAttribute('PosX', str(i.pos[0]))
                image.setAttribute('PosY', str(i.pos[1]))
                image.setAttribute('Width', str(i.width))
                image.setAttribute('Height', str(i.height))
                image.setAttribute('TopX', str(i.top[0]))
                image.setAttribute('TopY', str(i.top[1]))
                image.setAttribute('OriginalSizeX', str(i.original_size[0]))
                image.setAttribute('OriginalSizeY', str(i.original_size[1]))
                image.setAttribute('ScaleX', str(i.scale[0]))
                image.setAttribute('ScaleY', str(i.scale[0]))
                atlas.appendChild(image)
            root.appendChild(atlas)

        # Write the XML data.
        xml_data = doc.toprettyxml(encoding='utf-8')
        try:
            with open(file_path, 'wb') as f:
                f.write(xml_data)
        except (OSError, IOError):
            raise GraphicsError('Failed to write XML PKG.')

    def output_graphics(self, output_dir):
        """Outputs the images contained within to PNG files."""

        self.save_xml('{}.xml'.format(os.path.join(output_dir, self.name)))
        for atlas in self.atlases:
            for image in atlas.images:
                path = '{}.png'.format(os.path.join(output_dir, image.name))
                path = path.replace('\\', '/')
                path_dir = os.path.dirname(path)
                if not os.path.exists(path_dir):
                    os.makedirs(path_dir)
                image.output_png(path)


class Atlas:
    """Manages an atlas' data. Atlases hold images stitched together."""

    def __init__(self, virtual=False):
        """Initializes the empty atlas."""

        self.images = []
        self.virtual = virtual

    def add_image(self, image):
        """Adds a new image to the atlas."""

        self.images.append(image)

    def apply_texture(self, texture):
        """Applies the texture to the atlas' images."""

        self.texture = texture
        for image in self.images:
            image.apply_texture(texture)


class AtlasImage:
    """An image stored in an atlas."""

    def __init__(self, name, pos_x, pos_y, width, height, top_x, top_y,
        o_size_x, o_size_y, scale_x, scale_y):
        """Initializes the image's properties."""

        self.name = name
        self.pos = (pos_x, pos_y)
        self.width = width
        self.height = height
        self.top = (top_x, top_y)
        self.original_size = (o_size_x, o_size_y)
        self.scale = (scale_x, scale_y)

        self.image = None

    def apply_texture(self, texture):
        """Applies the texture to this image, slicing it appropriately."""

        if texture.image:
            self.image = texture.image.crop((
                self.pos[0], self.pos[1],
                self.pos[0] + self.width, self.pos[1] + self.height
            ))

    def output_png(self, file_path):
        """Outputs the image as a PNG file."""

        if not self.image:
            return
        self.image.save(file_path, format='PNG')


class Texture:
    """XNB texture file."""

    HEADER_START = b'XNBw'
    VERSION = 0x4
    COMPRESSED_FLAG = 0x80

    READER_NAME = b'Microsoft.Xna.Framework.Content.Texture2DReader'
    FORMAT_COLOR = 0x1
    FORMAT_DXT1 = 0x1C
    FORMAT_DXT5 = 0x20

    def __init__(self, name, data, debug):
        """Loads and eventually decompresses the texture data."""

        self.name = name
        self.debug = debug

        # Make sure the XNB file is valid.
        if data[:4] != Texture.HEADER_START:
            raise GraphicsError('Invalid XNB file.')
        self.version, self.flags, size = struct.unpack('<BBI', data[0x4:0xA])
        if not self.version:
            raise GraphicsError('Invalid XNB version.')

        # Check its compression status.
        if self.flags == Texture.COMPRESSED_FLAG:
            d_size = struct.unpack('<I', data[0xA:0xE])[0]
            texture_data = bm_lzx.decompress(d_size, data[0xE:])
        else:
            texture_data = data[0xA:]

        self.format, self.width, self.height, self.image = (
            self.get_texture_data(texture_data))

    def get_texture_data(self, texture_data):
        """Extracts the texture's data from the raw data."""

        # Get the reader information. There should be only a Texture2D reader.
        reader_count, offset = read_7BitEncodedInt(texture_data[0:5])
        reader_name_len = texture_data[offset]
        reader_name = texture_data[offset + 1:offset + 1 + reader_name_len]
        offset += 1 + reader_name_len
        reader_version = texture_data[offset:offset + 0x4]
        if reader_count != 1 or reader_name != Texture.READER_NAME:
            raise GraphicsError('Invalid texture, not a Texture2D.')
        offset += 0x4

        # Get the shared resource count. There shouldn't be any.
        shared_count, shared_len = read_7BitEncodedInt(
            texture_data[offset:offset + 0x5]
        )
        offset += shared_len
        if shared_count != 0:
            raise GraphicsError('Texture\'s shared resource count is not 0.')

        # Organize the texture's data before returning it.
        i = offset
        typeId, typeId_len = read_7BitEncodedInt(texture_data[i:i + 0x5])
        i += typeId_len
        format, width, height, mip_count = struct.unpack('<iIII',
            texture_data[i:i + 0x10]
        )
        if mip_count != 1:
            raise GraphicsError('Mip count is not 0.')
            return None
        i += 16
        mip_size = struct.unpack('<I', texture_data[i:i + 4])[0]
        i += 4
        image = Image.frombuffer('RGBA', (width, height),
            self.to_rgba(format, width, height, texture_data[i:i + mip_size]),
            'raw', 'RGBA', 0, 1
        )

        return format, width, height, image

    def to_rgba(self, format, width, height, data):
        """Converts data from the specified format to the RGBA format."""

        if format == Texture.FORMAT_COLOR:
            image = []
            l = len(data)
            i = 0
            while i < l:
                image += (data[i+2], data[i+1], data[i], data[i+3])
                i += 4
            image = bytearray(image)
        elif format == Texture.FORMAT_DXT1:
            image = bm_dxt.to_rgba(1, width, height, data)
        elif format == Texture.FORMAT_DXT5:
            image = bm_dxt.to_rgba(4, width, height, data)
        return image


class Graphics(BastionModule):
    """Extracts and compiles graphical files."""

    DATA_TYPE = 'graphics'

    CONTENT_DIR = ''
    EXTRACT_DIR = 'Graphics'

    def extract(self, graphics_dir, extract_dir):
        """Extracts the graphics data."""

        # Get a list of PKG files.
        pkgs = []
        pkgs_big = sorted(glob(os.path.join(graphics_dir, '*.pkg')))
        pkgs_720p = sorted(glob(os.path.join(graphics_dir, '720p', '*.pkg')))
        pkgs.extend(pkgs_big)
        pkgs.extend(pkgs_720p)
        if not pkgs:
            raise GraphicsError('Failed to find any PKGs.')

        # Load and process the PKG files.
        # Use processes to reduce memory usage.
        for pkg_path in pkgs:
            if pkg_path in pkgs_big:
                e_dir = extract_dir
            else:
                e_dir = os.path.join(extract_dir, '720p')
            p = Process(
                target=run_process,
                args=(pkg_path, self.debug, e_dir)
            )
            p.start()
            p.join()

def run_process(pkg_path, debug, extract_dir):
    """Runs a package extraction process."""

    try:
        pkg = PKG(pkg_path, debug)
        pkg.output_graphics(extract_dir)
    except KeyboardInterrupt:
        pass

MODULES.append(Graphics)
