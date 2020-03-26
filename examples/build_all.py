import subprocess
from pathlib import Path
from shutil import copytree, rmtree

import yaml
from jinja2 import Environment, FileSystemLoader


env = Environment(
    loader=FileSystemLoader('.'),
    extensions=['jinja2_markdown.MarkdownExtension'],
)


def make_index():
    data = yaml.safe_load(Path('index.yml').open())
    template = env.get_template('index.html.j2')
    return template.render(**data)


def get_examples():
    root = Path(__file__).absolute().parent
    for path in root.iterdir():
        if not path.is_dir():
            continue
        if not (path / 'main.go').exists():
            continue
        if path.name in ('server', 'build', 'frontend'):
            continue
        yield path


if __name__ == '__main__':
    build_path = Path(__file__).absolute().parent.parent / 'build'
    build_path.mkdir(exist_ok=True)

    (build_path / 'index.html').write_text(make_index())

    for path in get_examples():
        cmd = [str(path.parent / 'build.sh'), path.name]
        result = subprocess.run(cmd)
        if result.returncode != 0:
            exit(1)
        src = path.parent / 'build'
        assert src.exists()
        dst = build_path / path.name
        if dst.exists():
            rmtree(str(dst))
        copytree(src=str(src), dst=str(dst))

    print(build_path)
