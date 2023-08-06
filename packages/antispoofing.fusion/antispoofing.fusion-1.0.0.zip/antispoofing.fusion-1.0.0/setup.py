#!/usr/bin/env python
#Jukka Komulainen <jukmaatt@ee.oulu.fi>

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='antispoofing.fusion',
    version='1.0.0',
    description='Complementary countermeasures for detecting scenic face spoofing attacks',
    url='http://pypi.python.org/pypi/antispoofing.fusion',
    license='GPLv3',
    author='Jukka Komulainen',
    author_email='jukmaatt@ee.oulu.fi',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    #include_packages_data = True,

    install_requires=[
        "setuptools",
        "bob >= 1.0",      # base signal proc./machine learning library
        "xbob.db.replay", #Replay database
        "antispoofing.utils",  #Utils Package
    ],

    namespace_packages = [
      'antispoofing',
      ],

    entry_points={
      'console_scripts': [
        'fuse_scores.py = antispoofing.fusion.script.fuse_scores:main',
        'frame_by_frame_analysis.py = antispoofing.fusion.script.frame_by_frame_analysis:main',
        'venn.py = antispoofing.fusion.script.venn:main',
        'scatter_with_llr.py = antispoofing.fusion.script.scatter_with_llr:main',
        'find_valid_frames.py = antispoofing.fusion.script.find_valid_frames:main',        
        'time_analysis.py = antispoofing.fusion.script.time_analysis:main',
        'stub.py = antispoofing.fusion.script.stub:main',
        'fusion_scores.py = antispoofing.fusion.script.fusion_scores:main',
        ],


      'antispoofing.fusion.score_fusion': [
        'SUM = antispoofing.fusion.score_fusion.SUMFusion:SUMFusion',
        'LLR = antispoofing.fusion.score_fusion.LLRFusion:LLRFusion',
        'SVM = antispoofing.fusion.score_fusion.SVMFusion:SVMFusion',
        'LDA = antispoofing.fusion.score_fusion.LDAFusion:LDAFusion'
        ],

      'antispoofing.fusion.normalizer': [
        'ZNorm = antispoofing.fusion.normalizer.znorm:ZNorm',
        'MinMaxNorm = antispoofing.fusion.normalizer.minmax_norm:MinMaxNorm',
        'twoDNorm = antispoofing.fusion.normalizer.2dnorm:twoDNorm',
        ],

      },

)
