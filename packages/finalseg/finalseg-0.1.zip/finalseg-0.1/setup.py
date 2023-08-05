#coding:utf-8
 
from setuptools import setup, find_packages
 
setup(
    name='finalseg', #项目名
    version="0.1", #版本号
    description="A Chinese Words Segmentation Library", #介绍
    author="Sun, Junyi",
    author_email="zsp042@gmail.com",
    packages = ['finalseg'],   #要打包的文件夹名字
    zip_safe=False,          #不压缩
    include_package_data=True,
    install_requires = [
        
    ],
    entry_points = {
        
    },
)
