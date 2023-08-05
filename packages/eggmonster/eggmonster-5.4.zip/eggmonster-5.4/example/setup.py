from setuptools import setup

setup(name="test_project",
        version="1.5",
        author="Authors",
        author_email="email@example.com",
        packages=["test_project", "test_project.control"],
        data_files=[
                ("test_project/view", [
                        'test_project/view/base.tmpl',
                        'test_project/view/hello.tmpl'
                        ]
                ),
                ("test_project/etc", [
                        'test_project/etc/defaults.yaml',
                        ]
                ),
                ],
        install_requires=[
                "simplejson",
        ],
        entry_points={
                'eggmonster.applications' : [
                        'main = test_project.control.root:start',
                ],
        }
        )
