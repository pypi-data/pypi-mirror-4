#encoding:utf-8

from setuptools import setup

setup(name='caoliu',  
      author='TY',  
      author_email='tianyu0915@gmail.com',  
      version='0.0.4',  
      description='你懂',  
      keywords ='你懂',
      url='http://github.com/tianyu0915/caoliu',  
      packages=['caoliu'],  
      package_data={'caoliu':['*.*','caoliu/*.*']},

      entry_points = '''
      [console_scripts]
      caoliu = caoliu:main
      '''

)  
