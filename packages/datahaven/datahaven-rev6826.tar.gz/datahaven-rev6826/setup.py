from distutils.core import setup

setup(  name='datahaven',
        version='rev6826',
        author='Vincent Cate, DataHaven.NET LTD',
        author_email='datahaven.net@gmail.com',
        maintainer='Veselin Penev',
        maintainer_email='penev.veselin@gmail.com',
        url='http://datahaven.net',
        description='Distributed encrypted backup utility',
        long_description='''DataHaven.NET is a peer-to-peer online backup utility.
        
Imagine that you need the most reliable to keep the contents of a folder on
your hard drive and be sure that only you have access to this data.

We propose to divide the data into blocks, compress, encrypt and store them on
the computers of other users.

The system is designed in such a way that will 
keep track of each user which stores your information, and each block of your
data and maintain a state in which you can always get your data back.

Simple? Just tell DataHaven.Net what you want to back up, tell it  how often to
back up the data, and you are done!

Safe? Yes. The redundancy in backups makes it so if someone loses your data,
you can reconstruct what was lost and give it to someone else  to hold.
And all of this happens without you having to do a thing.

So is this secure? Absolutely!

All data is encrypted before it leaves your
computer with a key your computer generates. No one else can read your data.
Your data is broken into pieces and given to the deposit of other users in
encrypted form. We use public key encryption.

The private key is stored on your computer and NEVER leave it!!!
  
Only the private key can decrypt your data.
Recover data is only one way - download the necessary pieces from computers of
other users and decrypt them with your private key.

FREE? If you only want to receive and giving nothing in return - 
it is not for you.

You can imagine it like this: you exchange two gigabytes in a safe place
(on your hard drive) to one gigabyte, but kept very reliable.

If you are going to store data that you are not constantly in use,
but you need that they would be most protected - this is what you need!
 
This is very similar to the well-known torrents... but on the contrary! :-)

''',
        download_url='http://datahaven.net',
        #download_url='http://pypi.python.org/packages/source/d/datahaven/datahaven-rev6826.tar.gz',
        license='Copyright DataHaven.NET LTD. of Anguilla, 2006-2012,\nAll rights reserved.',
        keywords='''datahaven, data haven, data transfer, data protect, backup, 
safe backup, backup utility, backup data, backup software, backup online, 
distributed backup, peer to peer backup, storage, free storage, online storage, 
distributed storage, data storage, p2p, peer-to-peer, peer to peer, restore, 
restore data, distributed restore, restore online, safe restore, private key, 
encrypted data, data blocks, data recover, remote backup, remote storage, 
online backup software, donated space, donated, hdd space, python, twisted''',
        #platform='Windows, Linux',
        #requires='ncrypt, pycurl, wxgtk, crypto, openssl, pyasn1, twisted, python', 
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




