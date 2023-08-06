#encoding:utf-8

from setuptools import setup

setup(name='caoliu',  
      author='TY',  
      author_email='tianyu0915@gmail.com',  
      version='0.0.5',  
      description='这个真的不是邀请码',  
      keywords ='',
      url='http://github.com/tianyu0915/caoliu',  
      packages=['caoliu'],  
      package_data={'caoliu':['*.*','caoliu/*.*']},

      entry_points = '''
      [console_scripts]
      caoliu = caoliu:main
      '''

)  
