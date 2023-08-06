import os
from setuptools import setup, find_packages

template_dir = []
for root, dirs, files in os.walk('pkg_template'):
    if not dirs: 
        template_dir.append((os.path.join('/var/lib/bricklayer/', root), 
            map(lambda x: os.path.join(root, x), files))
        )

        
for root, dirs, files in os.walk('web'):
    if not dirs: 
        template_dir.append((os.path.join('/var/lib/bricklayer/', root), 
            map(lambda x: os.path.join(root, x), files))
        )
    else:
        template_dir.append((os.path.join('/var/lib/bricklayer/', root), 
            map(lambda x: os.path.join(root, x), files))
        )


data_files_list = template_dir
data_files_list.extend([
        ('/etc/bricklayer/', ['etc/bricklayer/bricklayer.ini',
            'etc/bricklayer/gpg.key', 'bricklayer/bricklayer.tac']),
    ]
)
setup(
    name='bricklayer',
    version='4.0.23',
    author = "Rodrigo Sampaio Vaz",
    author_email = "rodrigo.vaz@gmail.com",
    description = ("A package builder that watch git repositories"),
    license='Apache License',
    keywords = "package builder debian rpm",
    url = "http://locaweb.github.com",
    packages=find_packages(), 
    entry_points="""
    [console_scripts]
    build_consumer = bricklayer.build_consumer:main
    """,
    include_package_data = True,
    data_files=data_files_list
)
