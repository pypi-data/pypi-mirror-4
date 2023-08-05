## AUTHOR  : Zhenfei Yuan, Taizhong Hu
## EMAIL   : zfyuan@mail.ustc.edu.cn; thu@ustc.edu.cn
## URL     : taizhonglab.ustc.edu.cn/software/pyvine.html
## DATE    : Jan, 3, 2012
## LICENCE : GPL-v3


def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('bvcopula',parent_package,top_path)
    config.add_extension(name='bvnorm',sources=['bvnorm.f90',
                                                'bvnorm.pyf',
                                                'src/prob.f90',
                                                'src/lmin.f90',
                                                'src/rseed.f90'])
    config.add_extension(name='bvt',sources=['bvt.f90',
                                             'bvt.pyf',
                                             'src/quadpack.f90',
                                             'src/blas.f',
                                             'src/lbfgsb.f',
                                             'src/linpack.f',
                                             'src/timer.f',
                                             'src/prob.f90',
                                             'src/lmin.f90',
                                             'src/rseed.f90'])

    config.add_extension(name='bvclayton',sources=['bvclayton.f90',
                                                   'bvclayton.pyf',
                                                   'src/lmin.f90',
                                                   'src/rseed.f90'])

    config.add_extension(name='bvgumbel',sources=['bvgumbel.f90',
                                                  'bvgumbel.pyf',
                                                  'src/lmin.f90',
                                                  'src/rseed.f90'])

    config.add_extension(name='bvfrank',sources=['bvfrank.f90',
                                                 'bvfrank.pyf',
                                                 'src/lmin.f90',
                                                 'src/rseed.f90'])

    config.add_extension(name='bvjoe',sources=['bvjoe.f90',
                                               'bvjoe.pyf',
                                               'src/lmin.f90',
                                               'src/rseed.f90'])

    return config

if __name__=='__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
