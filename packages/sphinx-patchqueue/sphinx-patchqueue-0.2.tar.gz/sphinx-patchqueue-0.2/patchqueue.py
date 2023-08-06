import shutil
import tempfile
import itertools
import os.path

from docutils import nodes
from docutils.parsers.rst import Directive, directives
import sphinx.directives

import mercurial.patch
import pygments.lexers
import pygments.util

SERIES_KEY = 'series'

def setup(app):
    app.add_directive('queue', Queue)
    app.add_directive('patch', Patch)

    app.connect('html-page-context', add_styling_scripting)


def add_styling_scripting(app, page, template, context, doctree):
    """ Adds styling for the 4 hook classes pq-patch, pq-section, pq-diff and
    pq-file, as well as the scripting for toggling between the various content
    panes of ``pq-patch``.

    The output of each :rst:dir:`patch` is a tree with the shape::

        .pq-patch
            <file name>
            .pq-section
                code-block+
            .pq-diff
                code-block[diff]
            .pq-file
                code-block
            <file name>
            .pq-section
                code-block+
            .pq-diff
                code-block[diff]
            .pq-file
                code-block
            etc...
    """
    meta = [context.get('metatags', '')]

    add_styling(meta)
    add_scripting(meta)

    context['metatags'] = ''.join(meta)


def add_styling(meta):
    """ Adds default styling (to all pages?):
    * .pq-diff and .pq-file sections are hidden by default
    * .pq-section is shown
    * .pq-show-{section} on .pq-patch toggles the visibility of each section
    """
    meta.append("""<style type="text/css">
.pq-diff, .pq-file,
.pq-show-section .pq-diff, .pq-show-diff .pq-section, .pq-show-file .pq-section,
.pq-show-section .pq-file, .pq-show-diff .pq-file,    .pq-show-file .pq-diff {
    display: none;
}
.pq-show-section .pq-section,
.pq-show-diff .pq-diff,
.pq-show-file .pq-file {
    display: block;
}
</style>""")


def add_scripting(meta):
    """ On page start, adds 3-state toggles (radios?) inside all .pq-patch,
    each radio shows the corresponding section of the .pq-patch: section, diff
    or file.

    Fucking Bullshit: can't find a way to add JS code at the end of the page or
    at least after script_files are loaded (aside from JS files, which are
    apparently for themes or something, don't seem to have any point for
    extensions unless using horrible hacks e.g. dumping files into a tempdir
    and mounting that)
    (which might actually work now that I think about it)

    Anyway point is, going with straight W3C DOM, so no oldIE support.
    """
    meta.append("""<script type="text/javascript">
function makeRadios(code) {
    var fragment = document.createDocumentFragment();
    ['section', 'diff', 'file'].forEach(function (section, _, a) {
        var radio = document.createElement('input')
        radio.setAttribute('type', 'radio');
        radio.setAttribute('name', 'pq-radio-' + code);
        radio.setAttribute('data-section', section);
        if (section === 'section') {
            radio.checked = true;
        }

        var label = document.createElement('label');
        label.appendChild(radio);
        label.appendChild(document.createTextNode(' ' + section));

        fragment.appendChild(label);
        fragment.appendChild(document.createTextNode(' '));
    });
    return fragment;
}
document.addEventListener('DOMContentLoaded', function () {
    var patches = document.querySelectorAll('.pq-patch');
    for(var i=0; i<patches.length; ++i) {
        var block = document.createElement('div');
        block.appendChild(makeRadios(i));
        var patch = patches[i];
        patch.insertBefore(block, patch.childNodes[0]);
        patch.addEventListener('click', function (event) {
            var el = event.target;
            if (el.nodeName.toUpperCase() !== 'INPUT'
                || !el.hasAttribute('data-section')) {
                return;
            }
            // input < label < div[block] < div.pq-patch
            var patch = el.parentNode.parentNode.parentNode;
            var classes = patch.className.split(/\s+/)
                .filter(function (cls, index, names) {
                    return !/^pq-show-\w+/.test(cls);
                });
            classes.push('pq-show-' + el.getAttribute('data-section'));
            patch.className = classes.join(' ');
        });
    }
}, false);
</script>""")


class SphinxUI(object):
    verbose = False

    def __init__(self, app):
        self.app = app

    def note(self, s):
        self.app.info(s.strip('\n'))
    def warn(self, s):
        self.app.warn(s.strip('\n'))


class Series(object):
    """ Iterator on a sequence of patches, handles applying the patches to a
    temporary directory before returning a list of (file name,
    applied file location, patch hunks for file) for each file in a patch
    """
    def __init__(self, app, path, patches):
        self.ui = SphinxUI(app)
        self.index = -1
        self.path = path
        self.patches = patches
        self.directory = tempfile.mkdtemp()

        self.hgbackend = mercurial.patch.fsbackend(None, self.directory)

    def close(self, *args):
        shutil.rmtree(self.directory, ignore_errors=True)

    def __iter__(self):
        return self

    def next(self):
        self.index += 1
        if self.index >= len(self.patches):
            raise StopIteration

        patch = self.patches[self.index]
        with open(os.path.join(self.path, patch), 'rb') as fp:
            patchbackend = mercurial.patch.fsbackend(self.ui, self.directory)
            res = mercurial.patch.applydiff(
                self.ui, fp,
                patchbackend,
                mercurial.patch.filestore())

            assert res != -1, "Patch application failed"

            fp.seek(0)
            hunks = None
            content = []
            for event, values in mercurial.patch.iterhunks(fp):
                if event == 'file':
                    fromfile, tofile, first_hunk, gp = values
                    if not gp:
                        gp = mercurial.patch.makepatchmeta(
                            patchbackend, fromfile, tofile, first_hunk,
                            # default strip value for applydiff
                            strip=1)
                    hunks = []
                    content.append(
                        (gp.path, os.path.join(self.directory, gp.path), hunks))
                elif event == 'hunk':
                    hunks.append(values)
            return content

    __next__ = next


class Queue(Directive):
    """ Sets up a :class:`~patchqueue.Series` in the document context, and
    closing the series iterator after the document has been converted to a
    doctree
    """
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        document = self.state.document
        env = document.settings.env
        relpath, series_file = env.relfn2path(self.arguments[0])
        patches_dir = os.path.dirname(series_file)

        with open(series_file, 'rb') as f:
            series = env.temp_data[SERIES_KEY] = Series(
                env.app, patches_dir, [line.strip() for line in f])

        # Once the doctree is done generating, cleanup series
        env.app.connect('doctree-read', series.close)
        return []


def find_changed_lines(hunk):
    lines = (line for line in hunk.hunk if not line.startswith('-'))
    next(lines)  # skip hunk header
    # literalinclude does not allow passing stripnl=False to
    # pygments.highlight, so need to discard leading lines composed only of a
    # newline.
    for index, line in enumerate(
            itertools.dropwhile(lambda l: l == ' \n', lines)):
        if line[0] == '+':
            yield index


class Patch(Directive):
    """ Takes the next patch out of a series set up by a previous
    :class:`~patchqueue.Queue` call, displays it as sections of file
    corresponding to the patch hunks (with "+"'d files emphasized), the raw
    patch file and the full, final file, for each file in the patch.
    """
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'hidden': directives.flag,
    }

    def run_hunk(self, hunk, filepath, lang='guess'):
        """ Formats and displays a given hunk as a slice of the corresponding
        file (with added/edited lines emphasized)
        """
        return sphinx.directives.LiteralInclude(
            self.name,
            [filepath],
            {
                'language': lang,
                'lines': "%d-%d" % (hunk.startb, hunk.startb + hunk.lenb - 1),
                'emphasize-lines': ','.join(
                    str(n + 1) for n in find_changed_lines(hunk)),
            },
            [],
            self.lineno,
            self.content_offset,
            self.block_text,
            self.state,
            self.state_machine
        ).run()

    def run_diff(self, patchlines):
        """ Formats and displays a patch file
        """
        return sphinx.directives.CodeBlock(
            self.name,
            ['diff'],
            {'linenos': False},
            patchlines,
            self.lineno,
            self.content_offset,
            self.block_text,
            self.state,
            self.state_machine
        ).run()

    def run_content(self, filepath, lang='guess'):
        """ Formats and displays a complete result file, after having applied
        the current patch directive
        """
        return sphinx.directives.LiteralInclude(
            self.name,
            [filepath],
            {'linenos': True, 'language': lang},
            [],
            self.lineno,
            self.content_offset,
            self.block_text,
            self.state,
            self.state_machine
        ).run()

    def run(self):
        document = self.state.document
        if not document.settings.file_insertion_enabled:
            return [document.reporterwarning("File insertion disabled",
                                             line=self.lineno)]

        patch = next(document.settings.env.temp_data[SERIES_KEY], None)
        if patch is None:
            return [document.reporterwarning(
                "No patch left in queue %s" % document.series.path,
                line=self.lineno)]

        if 'hidden' in self.options:
            return []

        patch_root = nodes.container(classes=['pq-patch'])
        for fname, path, hunks in patch:
            patch_root.append(nodes.emphasis(text=fname))

            relative_path = os.path.relpath(path)

            try:
                lang = pygments.lexers.guess_lexer_for_filename(
                    fname, open(path, 'rb').read()).aliases[0]
            except pygments.util.ClassNotFound:
                lang = 'guess'

            patchlines = []
            section = nodes.container(classes=['pq-section'])
            for hunk in hunks:
                patchlines.extend(line.rstrip('\n') for line in hunk.hunk)

                section.extend(self.run_hunk(hunk, relative_path, lang=lang))
            patch_root.append(section)

            patch_root.append(
                nodes.container(
                    '', *self.run_diff(patchlines),
                    classes=['pq-diff']))
            patch_root.append(
                nodes.container(
                    '', *self.run_content(relative_path, lang=lang),
                    classes=['pq-file']))

        return [patch_root]
