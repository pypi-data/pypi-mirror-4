#!/usr/bin/env python
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
from res import version, factory_args_parse, DEBUG, do, get_do_params, get_infos, template_dir

import codecs
import os

def main():
    parser = factory_args_parse()

    # preparando para iniciar
    nm = parser.parse_args()
    if nm.path is not None:
        process_generator(nm)
    elif nm.version is True:
        process_version()
    else:
        parser.print_help()

def process_version():
    print '''%(description)s
Version: %(version)s
Homepage: %(home)s
   ''' % get_infos()

def process_generator(nm):
    if nm.outfile is None:
        filename = '.'.join([
            os.path.dirname(nm.path),
            'html'
        ])
        filepath = os.path.abspath(os.path.join(nm.path, '..'))
        nm.outfile = codecs.open(os.path.join(filepath, filename), 'w', 'utf-8')
    else:
        nm.outfile = codecs.open(nm.outfile, 'w', 'utf-8')

    try:
        template_path = os.path.join(template_dir, nm.template)
        if os.path.exists(template_path) is True:
            nm.template = codecs.open(template_path, 'r', 'utf-8')
        else:
            nm.template = codecs.open(nm.template, 'r', 'utf-8')
    except Exception, e:
        print e
    else:
        if DEBUG is True:
            print 'Path: %s' % nm.path
            print 'Template: %s' % nm.template
            print 'HTML output: %s' % nm.outfile

        do(**get_do_params(nm))

        # preparando para parar
        nm.template.close()
        nm.outfile.close()


if __name__ == '__main__': main()