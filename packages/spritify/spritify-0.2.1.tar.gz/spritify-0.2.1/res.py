# -*- coding: utf-8 -*-
'''
Copyright 2012 Rodrigo Pinheiro Matias <rodrigopmatias@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from argparse import ArgumentParser

try:
    from jinja2 import Template
except ImportError:
    print 'Install the jinja2'

import os
import re
import unicodedata as u

project_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(project_dir, 'templates')

try:
    from PIL import Image
except ImportError:
    import Image

DEBUG = False
# DEBUG = True

MAX_HEIGHT = 8192
DISTANCE_WIDTH = 300

get_namefile = lambda n: '.'.join(n.split('.')[:-1])


def get_long_description():
    try:
        text = open('README.rst', 'r').read()
    except:
        text = None
    finally:
        return text


def get_infos():
    return {
        'name': 'spritify',
        'description': 'The spritify is a tool for transform directory of images in the stylesheet and image file.',
        'long_description': get_long_description(),
        'version': version(),
        'home': 'https://bitbucket.org/rodrigopmatias/spritify',
        'author': 'Rodrigo Pinheiro Matias',
        'author_email': 'rodrigopmatias@gmail.com',
        'maintainer': 'Rodrigo Pinheiro Matias',
        'maintainer_email': 'rodrigopmatias@gmail.com',
        'py_modules': ['res'],
        'scripts': ['spritify.py'],
        'install_requires': ['PIL', 'jinja2'],
        'data_files': [
            ('templates', ['templates/default.html']),
        ],
        'classifiers': [
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'License :: OSI Approved :: Apache Software License',
            'Natural Language :: Portuguese (Brazilian)',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.4',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Internet',
            'Topic :: Multimedia :: Graphics :: Editors',
            'Topic :: Software Development :: Code Generators',
            'Topic :: Text Processing :: Markup :: HTML'
        ]
    }


def version():
    return '0.2.1'


def factory_args_parse():
    parser = ArgumentParser(
        description=u'HTML Generator of thumb directory.'
    )

    parser.add_argument(
        '-v',
        '--version',
        help=u'Print the version of generator.',
        action='store_true'
    )

    parser.add_argument(
        '-p',
        '--path',
        help=u'Path of base images to show in thum',
        dest='path'
    )

    parser.add_argument(
        '-o',
        '--output',
        help=u'Path of file to out processed html with thumbs.',
        dest='outfile'
    )

    parser.add_argument(
        '-t',
        '--template',
        help=u'HTML Template.',
        dest='template',
        default='default.html'
    )

    parser.add_argument(
        '-s',
        '--sprite',
        help=u'Spirite name for css and HTML.',
        dest='sprite_name',
        default=None
    )

    parser.add_argument(
        '-d',
        '--doubt',
        help=u'Spirite name for css and HTML.',
        dest='doubt',
        default=None
    )

    return parser


def get_do_params(nm):
    dct = nm.__dict__
    del dct['version']

    return dct


def slugify(text):
    text = u.normalize('NFKD', unicode(text)).lower()
    return re.sub('(-|\.|_|\s|\(|\)|\[|\]|\{|\}|\'|\")+', '-', text)


def get_images_from_path(path, append=None):
    images = {}

    for filename in os.listdir(path):
        if re.match('^.+\.(png|jpg|gif|tiff|bmp)$', filename) is not None:
            try:
                im = Image.open(os.path.join(path, filename))
            except:
                print 'ERR: %s' % os.path.join(path, filename)
            else:
                slot = im.size
                layers = images.get(slot, [])
                to_slug = get_namefile(filename) if append is None else ' '.join([get_namefile(filename), append])
                layers.append((os.path.join(path, filename), slugify(to_slug)))
                images.update({slot: layers})
                # im.close()
        elif filename not in ('.', '..') and os.path.isdir(os.path.join(path, filename)):
            images.update(get_images_from_path(
                os.path.join(path, filename),
                filename if append is None else '-'.join([append, filename])
            ))

    return images


def get_image_out_size(images):
    out_width = 0
    out_height = 0

    for key in images.keys():
        width, height = key
        need_height = height * len(images.get(key))
        number_cols = (need_height / MAX_HEIGHT) + (1 if need_height % MAX_HEIGHT > 0 else 0)
        out_height = MAX_HEIGHT if need_height > MAX_HEIGHT else (need_height if need_height > out_height else out_height)
        out_width += width * number_cols

    return out_width, out_height


def do(path, template, outfile, minify=False, sprite_name=None, doubt=None):
    outdir = os.path.dirname(outfile.name)

    if sprite_name is None:
        sprite_name = '-'.join(['spirite', slugify(os.path.basename(get_namefile(outfile.name)))])

    spirite_css_file = os.path.join(outdir, '.'.join([sprite_name, 'css']))
    spirite_image_file = os.path.join(outdir, '.'.join([sprite_name, 'png']))
    css_file = open(spirite_css_file, 'wt')

    images = get_images_from_path(path)
    out_width, out_height = get_image_out_size(images)

    css_lines = []
    css_lines.append('''.icon-%(slug)s { background: url('%(image)s') no-repeat 0 0 } ''' % {
        'slug': sprite_name,
        'image': os.path.basename(spirite_image_file)
    })

    transparent = (255, 255, 255, 0)
    out_im = Image.new('RGBA', (out_width, out_height), color=transparent)
    left = 0
    top = 0
    count = 0
    for slot, items in images.items():
        width, height = slot
        for item in items:
            count += 1
            filepath, slug = item
            im = Image.open(filepath)
            out_im.paste(im, (left, top))

            if doubt is None:
                css_lines.append('''.icon-%(slug)s { background-position: %(left)dpx %(top)spx !important } ''' % {
                    'slug': slug,
                    'sprite': sprite_name,
                    'top': top * (-1),
                    'left': left * (-1)
                })
            else:
                css_lines.append('''.icon-%(doubt)s-%(slug)s { background-position: %(left)dpx %(top)spx !important } ''' % {
                    'slug': slug,
                    'doubt': doubt,
                    'top': top * (-1),
                    'left': left * (-1)
                })

            top += height
            if (top + height) > MAX_HEIGHT:
                top = 0
                left += width
        left += width
        top = 0

    tpl = Template(template.read())
    icon = lambda x: 'icon-%s' % x
    outfile.write(
        tpl.render(
            cssfile=os.path.basename(css_file.name),
            slots=[
                {
                    'width': slot[0],
                    'height': slot[1],
                    'images': [
                        ' '.join([
                            icon(sprite_name),
                            icon(slug if doubt is None else '-'.join([doubt, slug]))
                        ])
                        for im, slug in sorted(items, (lambda x1, x2: 1 if x1[1] > x2[1] else -1))
                    ]
                }
                for slot, items in sorted(images.items(), lambda a, b: 1 if a[0] > b[0] else -1)
            ]
        )
    )

    css_file.write('\n'.join(css_lines) if minify is False else ' '.join(css_lines))
    css_file.close()

    print 'Finish of process %d images.' % count
    out_im.save(spirite_image_file, 'PNG')
