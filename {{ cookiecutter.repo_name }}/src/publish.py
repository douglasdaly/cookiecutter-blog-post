#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to take post and convert local images to image assets for blog
and to copy relevant media files to the publish/media folder.

:Author: Douglas Daly
:Date: 11/16/2018
"""
#
#   Imports
#
import os
import re
import shutil
import pickle
import zipfile

import imageio
import click


#
#   Variables
#

_VIDEO_EXTENSIONS = ('mp4', 'ogg')
_FILE_EXTENSIONS = ('pdf',)


#
#   Functions
#

def _load_file_contents(filename):
    """Loads text file contents"""
    if not os.path.isfile(filename):
        return None

    with open(filename, 'r') as fin:
        contents = fin.readlines()

    return contents


def _get_local_links_in_line(line):
    """Gets the relevant tags from the given line"""
    p = re.compile('(?:!\[([^\]]+)\]\(\.([^\s\)]+)\s\"([^\"\)]+)\"\))|(?:!\[([^\]]+)\]\(([^\)]+)\))')
    lnks = p.findall(line)

    ret = list()
    for lnk in lnks:
        ret.append([x.strip() for x in lnk if len(x.strip()) > 0])

    if ret is None or len(lnks) == 0:
        return None
    else:
        return ret


def _convert_name_to_asset(link_name, to_prepend=None):
    """Converts a given name to an asset for use with the blog"""
    asset_slug = link_name.lower().replace(' ', '-').replace('.', '')

    if to_prepend is not None:
        asset_slug = to_prepend.lower() + "_" + asset_slug

    output = "asset:" + asset_slug

    return output


def _do_clean(dir_to_clean):
    """Helper to clean files from given directory"""
    print('[INFO] Cleaning output directory... ', end='', flush=True)
    for (root, dirs, files) in os.walk(dir_to_clean):
        for fn in files:
            if not fn.endswith('.gitkeep'):
                fp = os.path.join(root, fn)
                os.remove(fp)
        for dn in dirs:
            shutil.rmtree(os.path.join(root, dn))
    print('DONE')


#
#   Script Functions
#

@click.group()
def cli():
    """Publish tool to generate upload content for blog posts"""
    pass


@cli.command()
@click.option('--output-dir', type=str, default='publish/', help="Output directory to use")
@click.option('--filename', type=str, default='', help='Output post file to clear publish directory for')
def clean(output_dir, filename):
    """
    Cleans the output directory of all files
    """
    if filename:
        _do_clean(os.path.join(output_dir, '_'.join(filename.split('.')[:-1])))
    else:
        _do_clean(output_dir)


@cli.command()
@click.argument('filename', type=str)
@click.option('--asset-tag', type=str, default=None, help="Tag to tag assets with")
@click.option('--output-dir', type=str, default="publish/", help="Output directory to use")
@click.option('--post-image', type=str, default=None, help='Image for post thumbnail')
@click.option('--output-list', is_flag=True, default=False,
              help="Output txt file with asset information", show_default=True)
def create(filename, asset_tag, output_dir, post_image, output_list):
    """
    Takes the given post file and converts the media links
    so that they'll reference assets for the blog.  Copies
    the relevant media files.
    """
    output = os.path.join(output_dir, '_'.join(filename.split('.')[:-1]))
    if not os.path.exists(output) or not os.path.isdir(output):
        print('[INFO] Creating new output directory {}... '.format(output), end='', flush=True)
        os.mkdir(output)
        print('DONE')

    # - Load file contents
    print("[INFO] Loading post file contents... ", end='', flush=True)
    file_path = os.path.join('post', filename)
    contents = _load_file_contents(file_path)

    if contents is None:
        print("ERROR")
        print("  Invalid input filename given!")
        return
    else:
        print("DONE")

    # - Get all relevant entries from contents and process text
    print('[INFO] Processing post file... ', end='', flush=True)
    all_links = dict()
    new_lines = list()
    for line in contents:
        t_lnks = _get_local_links_in_line(line)
        if t_lnks is None:
            new_lines.append(line)
            continue

        mod_line = line
        for lnk_arr in t_lnks:
            lnk_name = lnk_arr[0]
            lnk_ref = lnk_arr[1]
            if len(lnk_arr) > 2:
                lnk_desc = lnk_arr[2]
            else:
                lnk_desc = None

            asset_name = _convert_name_to_asset(lnk_name, asset_tag)
            mod_line = mod_line.replace(lnk_ref, asset_name, 1)

            if lnk_ref not in all_links.keys():
                all_links[lnk_ref] = (lnk_name, asset_name.split(":")[1:], lnk_desc)

        new_lines.append(mod_line)
    print('DONE')

    # - Clear out publish directory
    _do_clean(output)

    # - Copy post image (if exists)
    if post_image is not None:
        print('[INFO] Copying post image to output... ', end='', flush=True)
        dst = os.path.join(output, post_image.split('/')[-1])
        shutil.copy2(post_image, dst)
        print('DONE')

    # - Copy media files over
    print('[INFO] Copying posts media files to output... ', end='', flush=True)
    os.mkdir(os.path.join(output, 'media'))
    asset_listing = dict()
    for lnk_ref, lnk_data in all_links.items():
        in_path = os.path.abspath(lnk_ref.replace('..', '.'))

        lnk_file = lnk_ref.split('/')[-1]
        if asset_tag:
            lnk_file = '%s-%s' % (asset_tag, lnk_file)
        lnk_file = lnk_file.lower()
        out_path = os.path.join(output, 'media', lnk_file)

        shutil.copy2(in_path, out_path)

        asset_type = 'image'
        addl_meta_data = dict()
        file_ext = lnk_file.split('.')[-1].lower()
        if file_ext in _VIDEO_EXTENSIONS:
            asset_type = 'video'
            # - Get dimensions
            vid_reader = imageio.get_reader(out_path)
            vid_meta = vid_reader.get_meta_data()
            addl_meta_data['video_width'], addl_meta_data['video_height'] = \
                vid_meta['size']

        elif file_ext in _FILE_EXTENSIONS:
            asset_type = 'file'

        asset_listing[lnk_file] = {'type': asset_type, 'title': lnk_data[0],
                                   'slug': lnk_data[1][0], 'description': lnk_data[2],
                                   'tag': asset_tag, **addl_meta_data}

    with open(os.path.join(output, 'media', '__assets.pkl'), 'wb') as fout:
        pickle.dump(asset_listing, fout)

    print('DONE')

    # - Save Zipped Assets
    print('[INFO] Creating bulk assets zip archive... ', end='', flush=True)
    with zipfile.ZipFile(os.path.join(output, 'bulk_assets.zip'), 'w') as zout:
        for root, dirs, files in os.walk(os.path.join(output, 'media')):
            for file in files:
                zout.write(os.path.join(output, 'media', file), file)
    print('DONE')

    if output_list:
        # - Save text version of assets
        print("[INFO] Writing txt listing of assets... ", end='', flush=True)
        with open(os.path.join(output, 'asset_listing.txt'), 'w') as fout:
            for asset_file, meta_data in asset_listing.items():
                fout.write('{}\n'.format(asset_file))
                for k, v in meta_data.items():
                    fout.write("{}: {}\n".format(k, v))
                fout.write('\n')
        print('DONE')

    # - Save output post
    print('[INFO] Writing converted post markdown... ', end='', flush=True)
    with open(os.path.join(output, 'post.md'), 'w') as fout:
        fout.writelines(new_lines)
    print('DONE')


#
#   Entry-Point
#

if __name__ == "__main__":
    cli()
