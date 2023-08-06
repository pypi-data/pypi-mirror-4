from distutils.core import setup

setup(  name='datahaven',
        version='rev7190',
        author='Vincent Cate, DataHaven.NET LTD',
        author_email='datahaven.net@gmail.com',
        maintainer='Veselin Penev',
        maintainer_email='penev.veselin@gmail.com',
        url='http://datahaven.net',
        description='Distributed encrypted backup utility',
        long_description='''DataHaven.NET is a peer-to-peer online backup utility.
        
This is a distributed network for backup data storage. 
Each participant of the network provides a portion of his hard drive for other users. 
In exchange, he is able to store his data on other users's machines.

The redundancy in backups makes it so if someone loses your data, 
you can reconstruct what was lost and give it to someone else to hold. 
And all of this happens without you having to do a thing.

All data is encrypted before it leaves your computer with a key your computer generates. 
No one else can read your data. Recover data is only one way - 
download the necessary pieces from computers of other users and 
decrypt them with your private key.
        
The system is designed in such a way that will 
keep track of each user which stores your information, and each block of your
data and maintain a state in which you can always get your data back.

You can imagine it like this: you exchange two gigabytes in a safe place
(on your hard drive) to one gigabyte, but in the distributed storage 
and so kept very reliable. If you are going to store data 
that you are not constantly in use,
but you need that they would be most protected - this is what you need!
 
This is very similar to the well-known torrents... but on the contrary! :-)))

''',
        download_url='http://datahaven.net',
        #download_url='http://pypi.python.org/packages/source/d/datahaven/datahaven-rev7190.tar.gz',
        license='Copyright DataHaven.NET LTD. of Anguilla, 2006-2012,\nAll rights reserved.\nUse of this software constitutes acceptance of the Terms of Use: http://datahaven.net/terms_of_use.html ',
        keywords='''p2p, peer to peer, backup, restore, distributed, cloud, online, storage, data, recover, python, twisted''',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Environment :: Web Environment',
            'Framework :: Twisted',
            'Intended Audience :: Customer Service',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Information Technology',
            'Intended Audience :: System Administrators',
            'License :: Other/Proprietary License',
            'Natural Language :: English',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: Microsoft :: Windows :: Windows 7',
            'Operating System :: Microsoft :: Windows :: Windows Vista',
            'Operating System :: Microsoft :: Windows :: Windows XP',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Security',
            'Topic :: Security :: Cryptography',
            'Topic :: System :: Archiving :: Backup',
            'Topic :: System :: Distributed Computing',
            'Topic :: Utilities',
            ],
            
        packages=[
            'datahaven',
    		'datahaven.p2p', 
    		'datahaven.forms',
       		'datahaven.lib',
    		'datahaven.lib.shtoom',
    		# 'datahaven.epsilon',
    		# 'datahaven.vertex',
    		# 'datahaven.cspace',
    		# 'datahaven.cspace.dht',
    		# 'datahaven.cspace.ext',
    		# 'datahaven.cspace.main',
    		# 'datahaven.cspace.network',
    		# 'datahaven.cspace.util',
    		# 'datahaven.cspaceapps',
    		# 'datahaven.nitro',
		    ],
		    
)




