from distutils.core import setup, Extension


spa_module = Extension('_spamodule',
                           sources=['spamodule_wrap.c', 'spa.c'],
                           )

setup (name = 'spamodule',
#       ext_package='SPAmodule',
       version = '0.1',
       author      = "K.A. Shmirko",
       License = 'GNU',
       Platform = 'Any',
       description = """SPA Module algorithm""",
       ext_modules = [spa_module],
       py_modules = ["spamodule"],
       )