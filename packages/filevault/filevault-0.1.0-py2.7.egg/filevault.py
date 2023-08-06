from os import path
from os import makedirs
from uuid import uuid4
from hashlib import sha256
from itertools import permutations

HEX="0123456789abcdef"

class Vault( object ):
    def __init__( self, vaultpath='vault', depth=3, salt='changeme' ):
        self.vaultpath = vaultpath
        self.depth = depth
        self.salt = salt
        self.initVault()

    def initVault( self ):
        """Build the vault directories if they don't exist"""
        if path.exists( self.vaultpath ):
            return True

        perms = permutations( HEX * self.depth, self.depth )
        for perm in perms:
            try: makedirs( path.join( self.vaultpath, *perm ) )
            except OSError: pass

    def _generate_filename( self, h, ext='' ):
        """Accept a hash, return a valid file path"""
        dirs = h[ 0 : self.depth ]
        if ext and not ext.startswith( '.' ): ext = '.' + ext
        return path.join( *dirs ) + '/' + h + ext

    def create_filename( self, seed, ext='' ):
        """Accept a seed, return a valid file path"""
        h = sha256( seed + self.salt ).hexdigest()
        return self._generate_filename( h, ext )

    def create_random_filename( self, ext='' ):
        """Return a random but valid file path"""
        h = sha256( str( uuid4() ) ).hexdigest()
        return self._generate_filename( h, ext )


