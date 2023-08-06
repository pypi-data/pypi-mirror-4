# -*- coding: utf8 -*-
from __future__ import print_function

""" binio.py
Module that implements a simple class for reading and writing structured binary data

Version: 1.0.1b
Author:  Alejandro López Correa
Contact: alc@spika.net
URL:     http://spika.net/py/binio/
License: MIT License

Tested with python 2.7 and 3.2

(c) Alejandro López Correa, 2013
"""

import struct
from collections import namedtuple
import string

astr = lambda : str()
try:
    unicode()
    ustr = lambda : unicode()
except:
    ustr = lambda : str()        # python 3

VARIABLE_SIZE = "variable size"
class EndOfFileError( EOFError ):
    pass
    
class ParsingError( Exception ):
    pass

class WriteError( Exception ):
    pass

__TYPES = """\
byte            : s : b''
int8            : b : 0
i8              : b : 0
uint8           : B : 0
u8              : B : 0
short           : h : 0
int16           : h : 0
i16             : h : 0
ushort          : H : 0
uint16          : H : 0
u16             : H : 0
int             : i : 0
int32           : i : 0
i32             : i : 0
uint            : I : 0
uint32          : I : 0
u32             : I : 0
int64           : q : 0
i64             : q : 0
uint64          : Q : 0
u64             : Q : 0
float           : f : 0.0
float32         : f : 0.0
float64         : d : 0.0
double          : d : 0.0
char            : s : astr()
string          : s : astr()
string@utf8     : s : ustr()
string@utf16    : s : ustr()"""

def _parse_tuples( txt ):
    rows = []
    for line in txt.split( "\n" ):
        line = line.strip()
        if line:
            tokens = [t.strip() for t in line.split(':')]
            rows.append( tokens )
    return rows

def __parse_dict( txt ):
    rows = _parse_tuples( txt )
    d = dict()
    ddv = dict()
    for row in rows:
        assert len(row) == 3
        d[row[0]] = row[1]
        ddv[row[0]] = eval(row[2])
    return d, ddv
        
_C_TO_STRUCT, _C_TO_DEFVAL = __parse_dict( __TYPES )
    
def _fread( f, n ):
    buff = f.read( n )
    if len(buff) != n:
        raise EndOfFileError
    return buff
    
def _fwrite( f, x ):
    f.write( x )

class BinIO( object ):
    """ objectDef format:
    
        Lines of text, where each line is a triplet c t n
        c: item count (or var name)
        t: item type
        n: item name
        
        Example:
        
        1    : uint32   : object id
        16   : char     : object name
        1    : uint32   : txtn
        txtn : string   : text
        3    : float32  : position
        3    : float32  : rgb colour"""
        
    _Item = namedtuple( "Item", "n,tc,ts,tssz,name".split(',') )
    
    def __init__( self, objectDef ):
        triplets = _parse_tuples( objectDef )
        items = []
        byteCount = 0
        names = set([])
        inames = set([])
        for row in triplets:
            if len(row) != 3:
                raise ParsingError( 'too many tokens in definition "%s"' % str(row) )

            n = self.__validate_count_expression( row[0], inames )
            tc = row[1]
            try:
                ts = _C_TO_STRUCT[tc]
            except:
                raise ParsingError( 'unknown type "%s"' % tc )
            name = row[2]
            if len(name) == 0:
                raise ParsingError( 'missing identifier in "%s"' % str(row) )
            if name in names:
                raise ParsingError( 'duplicated identifier "%s"' % name )
            self.__validate_identifier( name )

            names.add( name )
            if ts in 'bBhHiIqQ' and n == 1:
                inames.add( name )
            tssz = struct.calcsize( '='+ts )

            items.append( BinIO._Item( n, tc, ts, tssz, name ) )
            if type(byteCount) == int and type(n) == int:
                byteCount += tssz*n
            else:
                byteCount = VARIABLE_SIZE
        self.__items = items
        self.__byteSize = byteCount
        self.clear()
        
    def get_size_in_bytes( self ):
        """ returns byte count of this struct or VARIABLE_SIZE """
        if self.__byteSize == VARIABLE_SIZE:
            bcount = 0
            for item in self.__items:
                if type(item.n) == int:
                    n = item.n
                else:
                    n = eval( item.n, self.__dict__ )
                    
                fmt = '%i%s' % (n,item.ts)
                bcount += n*item.tssz
        else:
            bcount = self.__byteSize
        return bcount
        
    def clear( self ):
        """ initializes all items to default value """
        for item in self.__items:
            setattr( self, item.name, _C_TO_DEFVAL[item.tc] )

    def read( self, f, byteOrder='=' ):
        """ read data from f with given byteOrder
            returns number of bytes read
        """
        assert byteOrder in ('=','<','>')
        self.clear()
        bytesRead = 0
        for item in self.__items:
            if type(item.n) == int:
                n = item.n
            else:
                n = eval( item.n, self.__dict__ )
                
            fmt = '%i%s' % (n,item.ts)
            bcount = n*item.tssz
            values = struct.unpack( byteOrder+fmt, _fread( f, bcount ) )
            bytesRead += bcount
            
            setattr( self, item.name, self._process_read( values, item.tc, n ) )
        return bytesRead
                
    def write( self, f, byteOrder='=' ):
        """ write data to f with given byteOrder
            no data is written until all values have been correctly packaged
            returns number of bytes written
        """
        assert byteOrder in ('=','<','>')
        toWrite = b''
        for item in self.__items:
            if type(item.n) == int:
                n = item.n
            else:
                n = eval( item.n, self.__dict__ )

            values = self._process_write( getattr( self, item.name ), item.tc, n )
            if values:
                try:
                    fmt = '%i%s' % (n,item.ts)
                    p = struct.pack( byteOrder+fmt, *values )
                except struct.error:
                    raise WriteError( "error packing %s into bytes (wrong type, value out of range, etc)" % item.name )
                toWrite += p

        _fwrite( f, toWrite )
        return len(toWrite)
            
    @staticmethod
    def __validate_identifier( ident ):
        if ident[0] not in string.ascii_letters:
            raise ParsingError( 'invalid identifier "%s"' % ident )
        for c in ident:
            if c not in string.ascii_letters and c not in string.digits:
                raise ParsingError( 'invalid identifier "%s"' % ident )

    @staticmethod
    def __validate_count_expression( expr, validNames ):
        def is_int( x ):
            try:
                n = int(x)
                return True
            except:
                return False
        def is_identifier( x ):
            try:
                BinIO.__validate_identifier( x )
                return True
            except:
                return False
        
        if is_int( expr ):
            return int(expr)                

        validChars = '()+-*/% \t'
        varnames = expr
        for c in validChars:
            varnames = varnames.replace( c, ':' )
        varnames = [v for v in varnames.split(':') if is_identifier(v) and v not in validNames]
        if varnames:
            raise ParsingError( 'invalid identifier in count expression "%s" (non scalar integer type)' % expr )
        
        for c in expr:
            if c not in validChars and c not in string.ascii_letters and c not in string.digits:
                raise ParsingError( 'invalid chars in count expression "%s"' % expr )
        
        return expr

    def _process_read( self, values, tc, n ):
        if tc == 'byte':
            values = values[0]
        elif tc.startswith( 'string' ) or tc == 'char':
            values = values[0]
            if tc == 'string' or tc == 'char':
                values = values.decode( 'ascii' ).rstrip('\x00')
            else:
                codec = tc.split( '@' )[1]
                values = values.decode( codec ).rstrip('\x00')
        elif n == 1:
            values = values[0]
        else:
            values = [x for x in values]
        return values

    def _process_write( self, values, tc, n ):
        if tc == 'byte':
            values = values[:n]
            if len(values) < n:
                values += b'\x00'*(n-len(values))
            values = [values]
        elif tc.startswith( 'string' ) or tc == 'char':
            if tc == 'string' or tc == 'char':
                values = values.encode( 'ascii' )
            else:
                codec = tc.split( '@' )[1]
                tmp = values.encode( codec )
                if codec == 'utf16':
                    if tmp[:2] == b'\xff\xfe' and tmp[2:].decode(codec) == values:
                        tmp = tmp[2:]                    
                values = tmp
            if len(values) < n:
                values += b'\x00'*(n-len(values))
            values = [values]
        elif n == 1:
            values = [values]
        else:
            values = values[:n]
            if len(values) < n:
                values.extend( [_C_TO_DEFVAL[tc]]*(n-len(values)) )
        
        return [x for x in values]

def new( objectDef ):
    return BinIO( objectDef )
    
def test():
    testFile = new( """
            1 : uint8           : item1
            1 : uint32          : item2
            8 : uint32          : item3
            1 : int32           : n4
         n4*2 : string@utf16    : item4
            1 : int32           : n5
           n5 : string@utf8     : item5
            1 : int32           : n6
           n6 : string          : item6
            1 : int32           : n7
         n7*3 : double          : item7
           16 : byte            : item8
            1 : char            : item9
    """ )
    
    def show_values():
        for i in range(1,10):
            x = 'item%i'%i
            v = getattr( testFile, x )
            print( '%s %16s %s' % (x, type(v), v) )
    
    print( 'default values' )
    show_values()
    print( 'size in bytes:', testFile.get_size_in_bytes() )

    print( '\nwrite' )

    testFile.item1 = 1
    testFile.item2 = 2
    testFile.item3 = list(range(8))
    testFile.item4 = "abcdefg"
    testFile.n4 = len(testFile.item4.encode('utf16'))
    testFile.item5 = "hijk"
    testFile.n5 = len(testFile.item5.encode('utf8'))+5 # add 5 to check padding
    testFile.item6 = "lmnopq"
    testFile.n6 = len(testFile.item6.encode('ascii'))
    testFile.item7 = [float(x) for x in range(9)]
    testFile.n7 = int(len(testFile.item7)/3)
    testFile.item8 = b'0123456789abcdef'
    testFile.item9 = 'z'
    
    show_values()
    print( 'size in bytes:', testFile.get_size_in_bytes() )
    
    n = testFile.write( open( 'test.binio', 'wb' ) )
    print( 'bytes written:', n )

    print( '\nread' )
    n = testFile.read( open( 'test.binio', 'rb' ) )
    print( 'bytes read:', n )
    show_values()
    
if __name__ == '__main__':
    test()



