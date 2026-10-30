from pathlib import Path
import argparse
import os
import shutil
import subprocess
import tempfile
from pylatex import Document, Package, Command, Section, Figure
from pylatex.utils import NoEscape

ROOT = Path(__file__).resolve().parent
SECTIONS = ('introduction', 'theory', 'results', 'conclusion')


def read_section(name):
    return (ROOT / 'sections' / f'{name}.txt').read_text(encoding='utf-8').strip()


def build(args, sections_override=None):
    if not shutil.which('pdflatex'):
        raise SystemExit('pdflatex not found. Install a TeX distribution (MacTeX or TeX Live).')
    target = Path(args.output).expanduser()
    if not target.is_absolute():
        target = ROOT / target
    target = target.resolve().with_suffix('.pdf')
    target.parent.mkdir(parents=True, exist_ok=True)
    doc = Document(documentclass='article')
    doc.packages.append(Package('amsmath'))
    doc.packages.append(Package('hyperref', options='hidelinks'))
    doc.preamble.append(Command('title', args.title))
    doc.preamble.append(Command('author', args.author))
    doc.preamble.append(Command('date', NoEscape(r'\today')))
    doc.append(NoEscape(r'\maketitle'))
    doc.append(NoEscape(r'\tableofcontents'))
    doc.append(NoEscape(r'\listoffigures'))
    doc.append(NoEscape(r'\clearpage'))
    for name in SECTIONS:
        with doc.create(Section(name.title())):
            content = (sections_override[name] if sections_override is not None else read_section(name))
            if content:
                for paragraph in content.split('\n\n'):
                    doc.append(paragraph.strip())
                    doc.append('\n\n')
            if name == 'results' and not args.no_figure:
                figure_path = Path(args.figure).expanduser()
                if not figure_path.is_absolute():
                    figure_path = ROOT / figure_path
                if not figure_path.is_file():
                    raise SystemExit(f'Figure not found: {figure_path}')
                with doc.create(Figure(position='htbp')) as fig:
                    fig.add_image(str(figure_path.resolve()), width=NoEscape(r'\textwidth'))
                    fig.add_caption(args.caption)
    with tempfile.TemporaryDirectory(prefix='python_latex_') as temp_dir:
        tex_base = Path(temp_dir) / 'report'
        doc.generate_tex(str(tex_base))
        for i in (1, 2):
            result = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'report.tex'], cwd=temp_dir, capture_output=True, text=True)
            if result.returncode:
                log = Path(temp_dir) / 'report.log'
                details = log.read_text(errors='replace')[-3500:] if log.exists() else result.stdout[-3500:]
                raise SystemExit(f'LaTeX compilation failed on pass {i}:\n{details}')
        shutil.copy2(Path(temp_dir) / 'report.pdf', target)
    print(f'Created {target}')


def main():
    parser = argparse.ArgumentParser(description='Edit and generate a LaTeX PDF report from the terminal')
    sub = parser.add_subparsers(dest='command')
    editor = sub.add_parser('edit', help='Open a section in your terminal editor')
    editor.add_argument('section', choices=SECTIONS)
    viewer = sub.add_parser('show', help='Print a section')
    viewer.add_argument('section', choices=SECTIONS)
    builder = sub.add_parser('build', help='Build the PDF')
    builder.add_argument('--title', default='Vacuum System Report')
    builder.add_argument('--author', default='Research Team')
    builder.add_argument('--output', default='output/report.pdf')
    builder.add_argument('--figure', default='images/total_sales_by_store.png')
    builder.add_argument('--caption', default='Total sales by store.')
    builder.add_argument('--no-figure', action='store_true')
    args = parser.parse_args()
    if args.command == 'edit':
        editor_command = os.environ.get('EDITOR', 'nano')
        import shlex
        cmd = shlex.split(editor_command) + [str(ROOT / 'sections' / f'{args.section}.txt')]
        raise SystemExit(subprocess.call(cmd))
    if args.command == 'show':
        print(read_section(args.section))
        return
    if args.command in (None, 'build'):
        if args.command is None:
            args = parser.parse_args(['build'])
        build(args)


if __name__ == '__main__':
    main()
