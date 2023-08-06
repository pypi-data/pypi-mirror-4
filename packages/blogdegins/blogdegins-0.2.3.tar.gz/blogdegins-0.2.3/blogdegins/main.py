# -*- encoding: utf-8 -*-
"""
Utility for creating static html code.
"""

import argparse
import sys
import os.path
import shutil
from pkg_resources import iter_entry_points, load_entry_point

import envoy

try:  # pragma: no cover
    from ConfigParser import ConfigParser
except:  # pragma: no cover
    from configparser import ConfigParser

import logging
logging.basicConfig(level=logging.DEBUG)

from blogdegins.getyesno import getyesno

BLOGDEGINS_INI = 'blogdegins.ini'

comandos = ['init', 'skeleton', 'render', 'page', 'widget', 'rsync']


def get_python_page_code(Content, content, is_widget=False, widget_dir=None):
    if is_widget:
        widget_path = os.path.join(
            'widgets' if not widget_dir else widget_dir,
            content,
            ''
        )
    else:
        widget_path = ''

    python_page_code = """# -*- encoding: utf-8 -*-
from ghtml.c_ghtml import GHtml
from ginsfsm.gconfig import add_gconfig

{content}_data = {{
    'myname': 'Blogdegins.',
}}

{Content}_CONFIG = {{
    'gaplic_namespace': [
        str, '', 0, None,
        'namespace of gaplic, to store callbacks.',
    ],
    '{content}_options': [
        dict,
        {{
            # See default values in the partner javascript file.
        }},
        0,
        None,
        'A dictionary containing the javascript options.'
    ],
}}


class {Content}(GHtml):
    def __init__(self, fsm=None, gconfig=None):
        gconfig = add_gconfig(gconfig, {Content}_CONFIG)
        super({Content}, self).__init__(fsm=fsm, gconfig=gconfig)

    def start_up(self):
        pass

    def render(self, **kw):
        kw.update(**{content}_data)
        return super({Content}, self).render(**kw)


def create_{content}(name, parent, **kw):
    {content} = parent.create_gobj(
        name,
        {Content},
        parent,
        template='{widget_path}{content}.mako',
        **kw
    )
    return {content}

""".format(Content=Content, content=content, widget_path=widget_path)
    return python_page_code


def get_init_py_widget_code(content):
    init_py_widget_code = """\
from {content} import create_{content}
""".format(content=content)
    return init_py_widget_code

mako_page_code = ""

javascript_page_code = """jQuery(function($) {
    // Your code using failsafe $ alias here...

    $(function() {
        // Document is ready
    });

});
"""

scss_page_code = ""


def main(argv=sys.argv):
    command = Blogdegins(argv)
    return command.run()


class Blogdegins(object):
    description = 'Generate static html code.'
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "command",
        choices=comandos,
        help="Available commands:\n"
"init {project} ==> create a .ini file and the directory structure.\n"
"skeleton ==> create a new tag directory, copying a assets directory.\n"
"render ==> generate a new index.html, in tags/{version} directory.\n"
"page {name} ==> creat a new set of py/js/mako/scss files in main directory.\n"
"widget {name} [widget_path] ==> creat a new wigdet directory"
    " with their set of py/js/mako/scss files in the widgets directory\n"
"rsync ==> syncronize the tag version with the remote host.\n"
    )
    parser.add_argument(
        "arguments",
        nargs=argparse.REMAINDER,
        help="Arguments to command."
    )
    parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        action='store_true',
        help="True if render in development mode, False in production mode.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        action='store_true',
    )

    def __init__(self, argv=sys.argv):
        self.args = self.parser.parse_args(argv[1:])
        if self.args.debug:
            self.args.verbose = True

    def run(self):
        cmd = self.args.command
        fn = getattr(self, cmd)
        if cmd != 'init':
            self.load_ini()

        return fn()

    def init(self):
        """ create a .ini file and the directory structure
        """
        print('====> init')
        if not self.args.arguments:
            print('<---- * You must supply a project name!')
            return 2
        project = self.args.arguments[0].lower()
        output_dir = os.path.abspath(os.path.normpath(project))
        if os.path.exists(output_dir):
            print('<---- * Directory "%s" already exists!' % (output_dir))
            return 2
        else:
            print('<---- * Creating blogdegins project in "%s".' % output_dir)
        os.mkdir(output_dir)

        src_path = self.assets_dir()
        dst_path = os.path.join(output_dir, 'assets')
        shutil.copytree(src_path, dst_path, symlinks=True)

        src_path = self.code_dir()
        dst_path = os.path.join(output_dir, project, 'htmlrendercode')
        shutil.copytree(
            src_path,
            dst_path,
            ignore=shutil.ignore_patterns('*.pyc', '*~'),
            symlinks=True,
        )
        dst_path = os.path.join(output_dir, project, 'htmlrendercode', 'wid')

        os.mkdir(os.path.join(output_dir, 'tags'))
        current_tag = '0.00.aa'
        config = ConfigParser()
        config.set('DEFAULT', 'current_tag', current_tag)
        config.add_section('tags')
        config.set('tags', current_tag, '')
        config.add_section(current_tag)
        config.set(
            current_tag,
            'assets',
            os.path.join('assets', 'h5bp+jquery'),
        )
        config.set(
            current_tag,
            'remote-server',
            '',
        )

        ini_file = os.path.join(output_dir, BLOGDEGINS_INI)
        with open(ini_file, 'w') as configfile:
            config.write(configfile)

        util_names = os.listdir(self.utils_dir())
        for name in util_names:
            srcname = os.path.join(self.utils_dir(), name)
            shutil.copy2(srcname, output_dir)

        return 0

    def load_ini(self):
        if not os.path.exists(BLOGDEGINS_INI):
            print('File "%s" NOT found.' % (BLOGDEGINS_INI))
            exit(2)
        # 'here' is the directory of the .ini file
        here = os.path.dirname(os.path.abspath(BLOGDEGINS_INI))
        self.config = ConfigParser({'here': here})
        self.config.read(BLOGDEGINS_INI)
        self.config.here = here
        self.config.current_tag = self.config.get('DEFAULT', 'current_tag')

    def module_dir(self):
        mod = sys.modules[self.__class__.__module__]
        return os.path.dirname(mod.__file__)

    def assets_dir(self):
        return os.path.join(self.module_dir(), "assets")

    def code_dir(self):
        return os.path.join(self.module_dir(), "_htmlrendercode")

    def utils_dir(self):
        return os.path.join(self.module_dir(), "utils")

    def current_tag_dir(self):
        return os.path.join(
            self.config.here,
            'tags',
            self.config.current_tag,
        )

    def skeleton(self):
        """ create a new tag directory, copying a assets directory
        """
        print('====> skeleton')
        dst_path = self.current_tag_dir()

        if not os.path.exists(dst_path):
            print('<---- * Creating "%s" directory.' % (dst_path))
        else:
            resp = getyesno(
                'You are re-creating the skeleton "%s".\n'
                'You will loose your data! Are you sure?' % dst_path,
                default='n',
            )
            if not resp:
                print('<---- * Operation aborted.')
                return 2
            print('<---- * Re-creating "%s" directory.' % (dst_path))
            shutil.rmtree(dst_path)

        assets = self.config.get(self.config.current_tag, 'assets')
        src_path = os.path.join(
            self.config.here,
            assets,
        )
        shutil.copytree(
            src_path,
            dst_path,
            symlinks=True,
        )

        # TODO creat links of current pages/widgets ???

        return 0

    def widget(self):
        """ creat a new widget directory
        with their set of py/js/mako/scss files in the widgets directory
        """
        print('====> widget')
        if not self.args.arguments:
            print('<---- * You must supply a name!')
            return 2
        name = self.args.arguments[0].lower()
        Name = name.capitalize()
        if len(self.args.arguments) >= 2:
            widget_dir = self.args.arguments[1]
        else:
            widget_dir = None  # TODO hay un fallo con los widgets sin dir, hay que darles el dir
        self._make_set(
            name,
            get_python_page_code(Name, name, True, widget_dir),
            mako_page_code,
            javascript_page_code,
            scss_page_code,
            True,
            widget_dir
        )

    def page(self):
        """ creat a new set of py/js/mako/scss files in the main directory
        """
        print('====> page')
        if not self.args.arguments:
            print('<---- * You must supply a name!')
            return 2
        name = self.args.arguments[0].lower()
        Name = name.capitalize()
        self._make_set(
            name,
            get_python_page_code(Name, name),
            mako_page_code,
            javascript_page_code,
            scss_page_code,
        )

    def _make_set(self,
            name,
            python_page_code,
            mako_page_code,
            javascript_page_code,
            scss_page_code,
            is_widget=False,
            widget_dir=None,
        ):
        project = os.path.basename(self.config.here).lower()

        if not is_widget:
            rendercode_path = os.path.join(
                self.config.here,
                project,
                'htmlrendercode',
            )
        else:
            rendercode_path = os.path.join(
                self.config.here,
                project,
                'htmlrendercode',
                'widgets' if not widget_dir else widget_dir,
                name,
            )

        if not os.path.exists(self.current_tag_dir()):
            print('<---- * First you must create a tag skeleton.')
            exit(2)

        if not os.path.exists(rendercode_path):
            os.mkdir(rendercode_path)

        py_file = '%s.py' % name
        js_file = '%s.js' % name
        scss_file = '%s.scss' % name
        mako_file = '%s.mako' % name

        widget_path = os.path.join(rendercode_path)
        if not os.path.exists(widget_path):
            os.mkdir(widget_path)
        filename = os.path.join(rendercode_path, '__init__.py')
        if not os.path.exists(filename):
            fd = open(filename, 'w')
            if is_widget:
                fd.write(get_init_py_widget_code(name))
            else:
                fd.write('')
            fd.close()

        ## Python
        filename = os.path.join(rendercode_path, py_file)
        if not os.path.exists(filename):
            print('<---- * Creating "%s" file.' % (filename))
            fd = open(filename, 'w')
            fd.write(python_page_code)
            fd.close()

        ## Mako
        filename = os.path.join(rendercode_path, mako_file)
        if not os.path.exists(filename):
            print('<---- * Creating "%s" file.' % (filename))
            fd = open(filename, 'w')
            fd.write(mako_page_code)
            fd.close()

        ## Javascript
        filename = os.path.join(rendercode_path, js_file)
        if not os.path.exists(filename):
            print('<---- * Creating "%s" file.' % (filename))
            fd = open(filename, 'w')
            fd.write(javascript_page_code)
            fd.close()

        ## Scss
        filename = os.path.join(rendercode_path, scss_file)
        if not os.path.exists(filename):
            print('<---- * Creating "%s" file.' % (filename))
            fd = open(filename, 'w')
            fd.write(scss_page_code)
            fd.close()

        ## js symbolic link
        if not is_widget:
            ln_path = os.path.join(
                self.current_tag_dir(),
                'static',
                'js',
                'bottom',
                'app',
            )
        elif not widget_dir:
            ln_path = os.path.join(
                self.current_tag_dir(),
                'static',
                'js',
                'bottom',
                'widgets',
            )
        else:
            ln_path = os.path.join(
                self.current_tag_dir(),
                'static',
                'js',
                'bottom',
                widget_dir,
            )
            if not os.path.exists(ln_path):
                os.mkdir(ln_path)

        os.chdir(ln_path)
        if not is_widget:
            source_file = '../../../../../../%s/htmlrendercode/%s' % (
                project, js_file)
        else:
            source_file = '../../../../../../%s/htmlrendercode/%s/%s/%s' % (
                project,
                'widgets' if not widget_dir else widget_dir,
                name,
                js_file
            )
        link_name = js_file
        try:
            os.symlink(source_file, link_name)
            print('<---- * Creating "%s" symbolic link.' % (
                ln_path + '/' + link_name))
            msg = """Remember to add to bottom_js_content[] list (assets.py) \
the line:
    'js/bottom/%s/%s.js'""" % (
                'app' if not is_widget else 'widgets'
                    if not widget_dir else widget_dir,
                name,
            )
            print(msg)
        except OSError:
            pass

        ## scss symbolic link
        if not is_widget:
            ln_path = os.path.join(
                self.current_tag_dir(),
                'static',
                'css',
                'app',
            )
        elif not widget_dir:
            ln_path = os.path.join(
                self.current_tag_dir(),
                'static',
                'css',
                'widgets',
            )
        else:
            ln_path = os.path.join(
                self.current_tag_dir(),
                'static',
                'css',
                widget_dir,
            )
            if not os.path.exists(ln_path):
                os.mkdir(ln_path)

        os.chdir(ln_path)
        if not is_widget:
            source_file = '../../../../../%s/htmlrendercode/%s' % (
                project, scss_file)
        else:
            source_file = '../../../../../%s/htmlrendercode/%s/%s/%s' % (
                project,
                'widgets' if not widget_dir else widget_dir,
                name,
                scss_file,
            )
        link_name = scss_file
        try:
            os.symlink(source_file, link_name)
            print('<---- * Creating "%s" symbolic link.' % (
                ln_path + '/' + link_name))
            msg = """Remember to add to scss_content[] list (assets.py) \
the line:
    'css/%s/%s.scss'""" % (
                'app' if not is_widget else 'widgets'
                    if not widget_dir else widget_dir,
                name
            )
            print(msg)
        except OSError:
            pass

        return 0

    def render(self):
        """ generate a new index.html, in tags/{version} directory
        Blogdegins will render using next call code:

        get_page(code_path, output_path, debug)
            is the only function being called from blogdegins.
            The rest is up to you.
            This function must return a class with a `render` method.
            The `render` method must return a string with the html code.
            :param code_path: path where python and templates code reside.
            :param output_path: current output tag directory.
            :param debug: True if you want debug.
        """
        project = os.path.basename(self.config.here).lower()
        if self.args.verbose:
            print('====> render ' + project)
        output_path = self.current_tag_dir()
        if not os.path.exists(output_path):
            print('<---- * First you must create a tag skeleton.')
            exit(2)

        code_path = os.path.join(
            self.config.here,
            #'htmlrendercode',
        )
        sys.path.append(code_path)
        os.chdir(self.config.here)

        # from wibterm.htmlrendercode.page import get_page
        package = __import__(project, globals(), locals(), [], -1)
        page = package.htmlrendercode.page.get_page(
            code_path, output_path, self.args.debug)

        html = page.render()
        if self.args.verbose:
            print(html)

        index_html = os.path.join(output_path, 'index.html')
        fd = open(index_html, 'w')
        fd.write(html)
        fd.close()
        return 0

    def rsync(self):
        """ syncronize the tag version with the remote host
        """
        print('====> rsync')
        src_path = os.path.join(self.current_tag_dir(), '')
        remote = self.config.get(self.config.current_tag, 'remote-server')
        if not remote:
            print('<---- * Please specify a remote server path.')
            exit(2)

        command = 'rsync -avz --delete ' \
            '--exclude \.webassets-cache --exclude \.cache %s %s' % (
            src_path,
            remote,
        )
        if self.args.verbose:
            print(command)
        response = envoy.run(command)
        print(response.std_out)

        return 0


if __name__ == '__main__':
    main()
