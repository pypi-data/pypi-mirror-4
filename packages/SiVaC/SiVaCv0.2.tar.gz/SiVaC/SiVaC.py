#!/usr/bin/env python

import array
import os
import sys
from collections import OrderedDict
from bisect import bisect_right
import argparse
from time import clock, time
import struct
from sys import getsizeof
import random

random.seed(26)

# A bit array demo
def makeBitArray(bitSize, fill = 0):
    intSize = bitSize >> 3                   # number of 8 bit integers

    if (bitSize & 7):                      # if bitSize != (32 * n) add
       intSize += 1 
    
    if fill == 1:
       fill = 255                                # all bits set
    else:
       fill = 0                                      # all bits cleared
     
    bitArray = array.array('B')          # 'B' = unsigned char (int)

    bitArray.extend((fill,) * intSize)
    
    return(bitArray)

# testBit() returns a nonzero result, 2**offset, if the bit at 'bit_num' is set to 1.
def testBit(array_name, bit_num):
    record = bit_num >> 3
    offset = bit_num & 7
    mask = 1 << offset
    return(array_name[record] & mask)

# setBit() returns an integer with the bit at 'bit_num' set to 1.
def setBit(array_name, bit_num):
    record = bit_num >> 3
    offset = bit_num & 7
    mask = 1 << offset
    array_name[record] |= mask
    return(array_name[record])

# clearBit() returns an integer with the bit at 'bit_num' cleared.
def clearBit(array_name, bit_num):
    record = bit_num >> 3
    offset = bit_num & 7
    mask = ~(1 << offset)
    array_name[record] &= mask
    return(array_name[record])
   
# toggleBit() returns an integer with the bit at 'bit_num' inverted, 0 -> 1 and 1 -> 0.
def toggleBit(array_name, bit_num):
    record = bit_num >> 3
    offset = bit_num & 7
    mask = 1 << offset
    array_name[record] ^= mask
    return(array_name[record])

# arrayToByte() returns a byte that corresponds to a boolean array of size 8 bytes.
def arrayToByte(boolArray):
    myByte = makeBitArray(len(boolArray))
    for i, j in enumerate(boolArray):
        if j:
           setBit(myByte,i)

    return myByte

# byteToArray() returns a boolean array of size 8 bytes that corresponds to a byte.
def byteToArray(Byte):
    bag = []
    for i in xrange(8):
        if testBit(Byte,i):
           bag.append(1)
        else:
           bag.append(0)

    myArray = array.array('B',bag)

    return myArray

# seekAndFetchByte() returns the byte of a specified position in a specified file
def seekAndFetchByte(fileDesc, pos):
    fileDesc.seek(pos)
    data = fileDesc.read(1)
    return byteToArray(array.array('B',[int(data.encode('hex'), 16)]))

# getBitPosition() returns the position of the (i,j) pair in its corresponding box
def getBitPosition(i,j,n):
    return (i%2*2)+j%2

# getBox() returns the box number of the (i,j) pair
def getBox(i,j,n):
    return (i/2)*((n+1)/2)+(j/2)

# isDiagonal() returns True if the (i,j) pair is in the diagonal
def isDiagonal(i,j,k):
    return True if j >= i - k and j <= i + k else False

# getDiagonalBox() returns the box number of a diagonal box according to the diagonal ordering
def getDiagonalBox(i,j,k):
    return i / k + j / k

def getDiagonalBitPosition(i,j,k):
    return (i % k) * k + (j % k)

# flushEmptyDiagonals() fills the output file with boxes full with 0s in for the boxes that we already now that have no edges in the input file
def flushEmptyDiagonals (filename,currBox,key,k):
    if currBox < key-1: # check if diagonal boxes are missing
       while currBox < key-1:
           currBox += 1
           box = [False]*k*k
           for i in xrange(len(box)/8): # works only for multiples of 8
               with open(filename,"ab") as f:
                   arrayToByte(box[i*8:i*8+8]).tofile(f)
                
# saveReady() checks if there are diagonal boxes ready for storing and stores them to the file
def saveReady(filename, diagonal, a, k, currBox):
  
    for key in sorted(diagonal.iterkeys()): # makes sure the boxes are stored in order
        if (key < 2*(a/k)-1):
            flushEmptyDiagonals(filename,currBox,key,k) # fill the boxes missing
            currBox = key
            box = diagonal[key]
            for i in xrange(len(box)/8): # works only for multiples of 8
                with open(filename,"ab") as f:
                   arrayToByte(box[i*8:i*8+8]).tofile(f)
            del diagonal[key] # box stored, so remove from index
    return currBox

# saveDiagonas() accepts a filename as an input and stores the diagonal boxes in a new file
def saveDiagonals(filename, compressed, k = 4):
    diagonal = {} # initialize dictionary of diagonal boxes
    with open(filename, 'r') as f: # open input file
        data = f.readlines()
        n = int(data.pop(0)) # read number of nodes
        lines = data
    currBox = -1
    for line in lines: # read every edge
        nodes = line.split()
        a = int(nodes[0]) # read node a
        b = int(nodes[1]) # read node b
        if isDiagonal(a,b,k-1): # if the edge is on the diagonal add the edge to the diagonal's box
           box = getDiagonalBox(a,b,k)
           bp = getDiagonalBitPosition(a,b,k)
           diagonal.setdefault(box,[False]*k*k)[bp] = True       
        currBox = saveReady(compressed,diagonal, a, k, currBox) # each time you read an edge check if you can save any diagonal boxes to remove them from memory

    currBox = saveReady(compressed,diagonal, n*2, k, currBox)
    flushEmptyDiagonals(compressed,currBox,2*(n+1)/k,k) # store Empty diagonals till the end of the diagonal

def existsDiagonalEdge(i,j,k,f):
    box = getDiagonalBox(i,j,k)
    return seekAndFetchByte(f,4+box*2+((i%k)/2))[k*(i%2)+(j%k)]


def checkAllEdges(filename, compressed, n, index, k = 4):
    keys = index.keys()
    with open(filename, 'r') as f, open(compressed,"rb") as fc:
         n = int(f.readline()) # read number of nodes
         for line in f: # read every edge
             nodes = line.split()
             a = int(nodes[0]) # read node a
             b = int(nodes[1]) # read node b
             print a,b,existsEdge(a,b,k,n,fc,index,keys)

def testGetIncoming(compressed,n,k,index,iterab=-1):
    keys = index.keys()

    if iterab == -1: iterab = random.sample(xrange(n),1000)
 
    with open(compressed,"rb") as fc:
        start = time()
        for i in iterab:
            offset = find_le(keys,i*n)
            print getAllEdges(i,k,n,fc,offset,index[offset][0],index[offset][1],1)[1]
        end = time()
        print "Average time for retrieving incoming edges is", (end-start)/len(iterab)

def testGetOutgoing(compressed,n,k,index,iterab=-1):
    keys = index.keys()

    if iterab == -1: iterab = random.sample(xrange(n),1000)

    with open(compressed,"rb") as fc:
        start = time()
        for i in iterab:
            offset = find_le(keys,i*n)
            print getAllEdges(i,k,n,fc,offset,index[offset][0],index[offset][1],2)[0]
        end = time()
        print "Average time for retrieving outgoing edges is", (end-start)/len(iterab)

def testGetAll(compressed,n,k,index,iterab=-1):
    keys = index.keys()

    if iterab == -1: iterab = random.sample(xrange(n),1000)

    with open(compressed,"rb") as fc:
        start = time()
        for i in iterab:
            offset = find_le(keys,i*n)
            print getAllEdges(i,k,n,fc,offset,index[offset][0],index[offset][1],0)
        end = time()
        print "Average time for retrieving incoming and outgoing edges is", (end-start)/len(iterab)



def testExistsEdge(filename, compressed, n, index, k = 4):
    keys = index.keys()
    with open(filename, 'r') as f, open(compressed,"rb") as fc:
         n = int(f.readline()) # read number of nodes
         for line in f: # read every edge
             nodes = line.split()
             a = int(nodes[0]) # read node a
             b = int(nodes[1]) # read node b
             print a,b,existsEdge(a,b,k,n,fc,index,keys)

def testPercentageOfDiagonals(filename,k=4):
    allEdges = 0
    diagonalEdges = 0
    with open(filename, 'r') as f:
        n = int(f.readline()) # read number of nodes
        for line in f: # read every edge
            nodes = line.split()
            a = int(nodes[0]) # read node a
            b = int(nodes[1]) # read node b
            if isDiagonal(a,b,k-1):
                diagonalEdges += 1
            allEdges += 1
    print diagonalEdges,"out of",allEdges,"are in the diagonal", float(diagonalEdges)/allEdges,"%"


def existsEdge(i,j,k,n,fc,index,keys):
    if isDiagonal(i,j,k-1):
        return existsDiagonalEdge(i,j,k,fc)
    else:
        ij = (i*n)+j
        ji = (j*n)+i
        off1 = find_le(keys,ij)
        return existsNonDiagonalEdge(i,j,k,n,fc,off1,index[off1][0],index[off1][1])

def testExists(k,n,compressed,index,iterab=-1):
    keys = index.keys()

    if iterab == -1: iterab = zip([random.choice(xrange(n)) for i in xrange(1000)],[random.choice(xrange(n)) for j in xrange(1000)])

    with open(compressed,"rb") as fc:
         start = time()
         for a, b in iterab:
             print existsEdge(a,b,k,n,fc,index,keys)
         end = time()
         print "Average time for checking if a random edge exists", (end-start)/len(iterab)

def printAllDiagonalBoxes(k):
    with open("compressed","rb") as fc:
         for j in xrange(5):
             i = j + 200
             print i, seekAndFetchByte(fc,i*((k*k)/8)), seekAndFetchByte(fc,i*((k*k)/8)+1)

def createDicts(filename, dictIn, dictOut, allNodes):
    with open(filename, 'r') as f:
        f.readline()
        for line in f:
            nodes = line.split()
            a = int(nodes[0])
            b = int(nodes[1])
            allNodes.add(a)
            allNodes.add(b)
            dictOut.setdefault(a,[]).extend([b])
            dictIn.setdefault(b,[]).extend([a])


def saveNonDiagonals(filename,dictIn,dictOut,allNodes,k):
    offset = 0
    nodes = len(allNodes)
    currentByte = [False]*8
    boxType = BoxType.B
    with open(filename,"ab") as f: # opens file for append
        for n in allNodes:
            inL = []
            outL = []
            line = {}
            if n in dictIn:
                inL.extend(sorted(dictIn[n]))
            if n in dictOut:
                outL.extend(sorted(dictOut[n]))
            i = 0
            j = 0
            while i < len(inL) or j < len(outL):
                inVal = -1
                outVal = -1
                if i<len(inL):
                    inVal = inL[i]
                if j<len(outL):
                    outVal = outL[j]
                if (inVal<outVal or outVal==-1) and inVal !=-1:
                    line[inVal] = ['0','1']
                    i+=1
                elif (inVal>outVal) or inVal==-1 and outVal !=-1:
                    line[outVal] = ['1','0']
                    j+=1
                else:
                    line[outVal] = ['1','1']
                    i+=1
                    j+=1
            for n2 in sorted(line.keys()):
                if not isDiagonal(n,n2,k-1):
                    box = n*nodes+n2
                    x = box - offset
                    written = False
                    while (not written):
                        if boxType == BoxType.A1:
                            if x < 4:
                                l = list(bin(x)[2:])
                                flushToByte(l,2-len(l),currentByte)
                                flushToByte(line[n2],2,currentByte)
                                offset = box
                                boxType = BoxType.A2
                                written = True
                                continue
                            else:
                                flushToByte(['0']*4,0,currentByte)
                                boxType = BoxType.A2
                                continue
                        elif boxType == BoxType.A2:
                            if x < 4:
                                l = list(bin(x)[2:])
                                flushToByte(l,6-len(l),currentByte)
                                flushToByte(line[n2],6,currentByte)
                                offset = box
                                boxType = BoxType.A1
                                written = True
                                appendByteToFile(f,currentByte)
                                currentByte = [False]*8
                                continue
                            else:
                                if x >= nodes-2 and x <= nodes+1:
                                    flushToByte(['1','1','0','0'],4,currentByte)
                                    boxType = BoxType.A1
                                    x -= nodes-2
                                    offset += nodes-2
                                    appendByteToFile(f,currentByte)
                                    currentByte = [False]*8
                                    continue
                                elif x > nodes+1:
                                    flushToByte(['1','0','0','0'],4,currentByte)
                                    boxType = BoxType.B
                                    x -= nodes+1
                                    offset += nodes+1
                                    appendByteToFile(f,currentByte)
                                    currentByte = [False]*8
                                    continue
                                elif x >= 512 and x > (3*nodes)/4:
                                    flushToByte(['0','1','0','0'],4,currentByte)
                                    boxType = BoxType.B
                                    x -= (3*nodes)/4
                                    offset += (3*nodes)/4
                                    appendByteToFile(f,currentByte)
                                    currentByte = [False]*8
                                    continue
                                else:
                                    flushToByte(['0']*4,0,currentByte)
                                    boxType = BoxType.B
                                    appendByteToFile(f,currentByte)
                                    currentByte = [False]*8
                                    continue
                        elif boxType == BoxType.B:
                            if x < 512:
                                flushToByte(['0'],0,currentByte)
                                y = ( x - (x % 4) )
                                l = list(bin(y/4)[2:])
                                flushToByte(l,8-len(l),currentByte)
                                x -= y
                                offset += y
                                boxType = BoxType.A1
                                appendByteToFile(f,currentByte)
                                currentByte = [False]*8
                                continue
                            else:
                                flushToByte(['1'],0,currentByte)
                                xb = x / 512
                                if xb < 128:
                                    l = list(bin(xb)[2:])
                                    flushToByte(l,8-len(l),currentByte)
                                    m = xb * 512
                                    x -= m
                                    offset += m
                                    appendByteToFile(f,currentByte)
                                    currentByte = [False]*8
                                    continue
                                else:
                                    flushToByte(['1']*7,1,currentByte)
                                    x -= 65024 # 127 * 512
                                    offset += 65024 # 127 * 512
                                    appendByteToFile(f,currentByte)
                                    currentByte = [False]*8
        if (boxType == BoxType.A2):
            appendByteToFile(f,currentByte)

def existsNonDiagonalEdge(i,j,k,n,f,offset,fp,boxType,rev=False):
    x = (i*n)+j

    if offset == x and boxType == BoxType.A1:
        byte = seekAndFetchByte(f,fp)
        outEdge = byte[2]
        inEdge = byte[3]
    elif offset == x and boxType == BoxType.A2:
        byte = seekAndFetchByte(f,fp)
        outEdge = byte[6]
        inEdge = byte[7]
    elif offset == x and boxType == BoxType.B:
        byte = seekAndFetchByte(f,fp+1)
        outEdge = byte[2]
        inEdge = byte[3]
    val = False
    while(offset<x or val):
        val = False
        try:
            byte = seekAndFetchByte(f,fp)
        except:
            return 0
        if boxType == BoxType.B:
            if byte[0]==1:
                y = byteToInt(byte[1:])*512
                offset += y
                fp += 1
                val = True
                continue
            else:
                y = byteToInt(byte[1:])*4
                offset += y
                boxType = BoxType.A1
                fp += 1
                val = True
                continue
        elif boxType == BoxType.A1:
            y = byteToInt(byte[0:2])
            offset += y
            outEdge = byte[2]
            inEdge = byte[3]
            boxType = BoxType.A2
            continue
        elif boxType == BoxType.A2:
            y = byteToInt(byte[4:6])
            outEdge = byte[6]
            inEdge = byte[7]
            fp += 1
            check = not inEdge and not outEdge
            if check and y == 3:
                offset += n-2
                boxType = BoxType.A1
                val = True
                continue
            elif check and y == 2:
                offset += n+1
                boxType = BoxType.B
                val = True
                continue
            elif check and y == 1:
                offset += (3*n)/4
                boxType = BoxType.B
                val = True
                continue
            elif check and y == 0:
                boxType = BoxType.B
                continue
            else:
                offset += y
                boxType = BoxType.A1
                continue
    if offset == x and not rev:
        return outEdge
    elif offset == x and rev:
        return inEdge
    else:
        return 0


def getAllEdges(i,k,n,fc,offset,fp,boxType,t):
    nd = getAllNonDiagonalEdges(i,k,n,fc,offset,fp,boxType)
    
    outEdges = nd[0]
    inEdges = nd[1]
    if t != 1:
        for j in range(i-k,i+k):
            if j >= 0 and j < n:
                if existsDiagonalEdge(i,j,k,fc):
                    outEdges.append(j)
    if t != 2:
        for j in range(i-k,i+k):
            if j >= 0 and j < n:
                if existsDiagonalEdge(j,i,k,fc):
                    inEdges.append(j)
    return [outEdges,inEdges]

def getAllNonDiagonalEdges(i,k,n,f,offset,fp,boxType):
    x = i*n
    end = x+n+1
    val = False
    inEdges = []
    outEdges = []
    while(offset<end or val):
        val = False
        try:
            byte = seekAndFetchByte(f,fp)
        except:
            return [outEdges,inEdges]
        if boxType == BoxType.B:
            if byte[0]==1:
                y = byteToInt(byte[1:])*512
                offset += y
                fp += 1
                val = True
                continue
            else:
                y = byteToInt(byte[1:])*4
                offset += y
                boxType = BoxType.A1
                fp += 1
                val = True
                continue
        elif boxType == BoxType.A1:
            y = byteToInt(byte[0:2])
            offset += y
            a = offset / n
            b = offset % n
            outEdge = byte[2]
            inEdge = byte[3]
            if (a==i and outEdge==1):
                outEdges.append(b)
            if (a==i and inEdge==1):
                inEdges.append(b)
            boxType = BoxType.A2
            continue
        elif boxType == BoxType.A2:
            y = byteToInt(byte[4:6])
            outEdge = byte[6]
            inEdge = byte[7]
            fp += 1
            check = not inEdge and not outEdge
            if check and y == 3:
                offset += n-2
                boxType = BoxType.A1
                val = True
                continue
            elif check and y == 2:
                offset += n+1
                boxType = BoxType.B
                val = True
                continue
            elif check and y == 1:
                offset += (3*n)/4
                boxType = BoxType.B
                val = True
                continue
            elif check and y == 0:
                boxType = BoxType.B
                continue
            else:
                offset += y
                a = offset / n
                b = offset % n
                if (a==i and outEdge==1):
                    outEdges.append(b)
                if (a==i and inEdge==1):
                    inEdges.append(b)
                boxType = BoxType.A1
                continue
    return [outEdges,inEdges]


def createIndex(k,n,fc,index, pl = 50):
    linesIn = []
    fc.seek(0,2)
    size = fc.tell()-1
    offset = 0
    fp = n+(n%2)+4
    boxType = BoxType.B
    index[0] = [fp,boxType]
    linesIn.append(0)
    while(fp<size):
        byte = seekAndFetchByte(fc,fp)
        if (offset / n) / pl not in linesIn and boxType == BoxType.A1:
            index[offset] = [fp,boxType]
            linesIn.append((offset / n) / pl)
        if boxType == BoxType.B:
            if byte[0]==1:
                y = byteToInt(byte[1:])*512
                offset += y
                fp += 1
                continue
            else:
                y = byteToInt(byte[1:])*4
                offset += y
                boxType = BoxType.A1
                fp += 1
                continue
        elif boxType == BoxType.A1:
            y = byteToInt(byte[0:2])
            offset += y
            outEdge = byte[2]
            inEdge = byte[3]
            boxType = BoxType.A2
            continue
        elif boxType == BoxType.A2:
            y = byteToInt(byte[4:6])
            outEdge = byte[6]
            inEdge = byte[7]
            fp += 1
            check = not inEdge and not outEdge
            if check and y == 3:
                offset += n-2
                boxType = BoxType.A1
                val = True
                continue
            elif check and y == 2:
                offset += n+1
                boxType = BoxType.B
                val = True
                continue
            elif check and y == 1:
                offset += (3*n)/4
                boxType = BoxType.B
                val = True
                continue
            elif check and y == 0:
                boxType = BoxType.B
                continue
            else:
                offset += y
                boxType = BoxType.A1
                continue
            

		

def byteToInt(byte):
    dec = 0
    for i in byte:
        dec = dec*2+i
    return dec
                    
def flushToByte(l,pos,byte):
    for i in l:
        if i == '1':
            byte[pos] = True
        pos += 1
    return byte

def appendByteToFile(f,byte):
    arrayToByte(byte).tofile(f)

class BoxType:
    A1 = 1
    A2 = 2
    B = 3
    

def writeIntToFile(x,f):
    bitArray = array.array('I') # 'I' = unsigned 32-bit integer
    bitArray.extend((0,)*1)
    l = list(reversed([int(i) for i in list(bin(x)[2:])]))
    al =  l + [0] * (32 - len(l))
    for i, j in enumerate(al):
        if j:
            record = i >> 5
            offset = i & 31
            mask = 1 << offset
            bitArray[record] |= mask
    bitArray.tofile(f)
    f.close()



def find_le(a, key):
    '''Find smallest item less-than or equal to key.
    Raise ValueError if no such item exists.
    If multiple keys are equal, return the leftmost.

    '''
    i = bisect_right(a, key)
    if i:
        return a[i-1]
    raise ValueError('No item found with key at or below: %r' % (key,))


def createCompressedFile(filename,compressed,k,n):
    saveDiagonals(filename,compressed,k)
    dictIn = {}
    dictOut = {}
    allNodes = set([])
    createDicts(filename,dictIn,dictOut,allNodes)
    saveNonDiagonals(compressed,dictIn,dictOut,allNodes,k)

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

# main function
def main(argv=None):

   if argv is None:
        argv = sys.argv

   # initialize parser for command line arguments
   parser =  argparse.ArgumentParser()

   # set parsing options
   parser.add_argument("-f", "--file", type=str, dest="file", default="dataset/citation-PaperJSON_199star.graph.txt", help="interaction mode: filename [default: %(default)s]")
   parser.add_argument("-m", "--mode", type=str, dest="mode", default="checkAllEdges", help="interaction mode: checkAllEdges, testGetIncoming, testGetOutgoing, testGetAll, testPercentageOfDiagonals, or testExists [default: %(default)s]")
   parser.add_argument("-c", "--compressedfile", type=str, dest="compressedfile", default=None, help="interaction mode: compressed filename [default: %(default)s]")
   # parse command line arguments
   args = parser.parse_args()

   filename = args.file
   if args.compressedfile:
       compressed = args.compressedfile
   else:
       compressed = args.file + ".xA8"

   k = 4

   if not args.compressedfile:
       n = int(open(filename,"r").readline())
       try:
           os.remove(compressed)
       except:
           pass
       writeIntToFile(n,open(compressed,"wb"))
       createCompressedFile(filename,compressed,k,n)
   else:
       n = struct.unpack('I', str(open(compressed).read(4)))[0] 
       filename = compressed[:len(compressed)-4]
   index = {}
   createIndex(k,n,open(compressed,"rb"),index,50)
   mySortedIndex = OrderedDict(sorted(index.items(), key=lambda t: t[0]))
   index = None

   print "index length is",len(mySortedIndex.keys())
   print "index size in memory is",sys.getsizeof(mySortedIndex) # comment this line for pypy to work!

   try:

      if args.mode == "checkAllEdges":
          checkAllEdges(filename, compressed, n,mySortedIndex,k)      
      elif args.mode == "testGetIncoming":
          testGetIncoming(compressed,n,k,mySortedIndex)
          # you can also call testGetIncoming with a customised last argument as shown below
          # testGetIncoming(compressed,n,k,mySortedIndex,[2,6,123,0,9])
      elif args.mode == "testGetOutgoing":
          testGetOutgoing(compressed,n,k,mySortedIndex)
          # you can also call testGetOutgoing with a customised last argument as shown below
          # testGetOutgoing(compressed,n,k,mySortedIndex,[21,3,13,40,4])
      elif args.mode == "testGetAll":
          testGetAll(compressed,n,k,mySortedIndex)
          # you can also call testGetAll with a customised last argument as shown below
          # testGetAll(compressed,n,k,mySortedIndex,[1,13,3,51,14])
      elif args.mode == "testPercentageOfDiagonals":
          testPercentageOfDiagonals(filename,k=4)
      elif args.mode == "testExists":
          testExists(k,n,compressed,mySortedIndex)
          # you can also call testExists with a customised last argument as shown below
          # testExists(k,n,compressed,mySortedIndex,[(302,1),(5,49),(89,88)])
      else:
         raise Usage("Invalid option: " + args.mode)

   except Usage, err:
        print err.msg
        parser.print_help()
        return 1 

if __name__ == '__main__':
   sys.exit(main())
