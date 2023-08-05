
'''
setup.py for bamboo

'''

from distutils.core import setup
import os, glob

def get_version():

    '''return version from fixed always must exist file

       Making very broad assumptions about the 
       existence of files '''
    
    v = open('bamboo/scaffold/version.txt').read().strip()
    return v




def main():

    setup(name='bamboo.scaffold',
          version=get_version(),
          packages=['bamboo.scaffold'
                   ],
          namespace_packages = ['bamboo'],
          author='See AUTHORS.txt',
          author_email='info@cnx.org',
          url='https://github.com/Connexions/rhaptos2.repo',
          license='LICENSE.txt',
          description='Misc tools supporting build and deployment, usually via jenkins',
          long_description='see description',
          install_requires=[
              "fabric >= 1.4.0"
              ,"requests"
              ,"nose"
              ,"rhaptos2.common>=0.0.13"
              ,"virtualenv"
              ,"jenkinsapi"

                           ],
          scripts=glob.glob('scripts/*'),

          package_data={'bamboo.scaffold': ['tmpls/*.*',
                                            'version.txt',
                                            'docs/*.*'
                                           ],
                        },

          
          )



if __name__ == '__main__':
    main()

