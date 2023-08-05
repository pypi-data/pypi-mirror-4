"""

Read and write various types of file / directory

"""

from nesoni import grace, legion

import os, sys, re, weakref, collections, csv, subprocess, gzip, bz2, itertools

from nesoni.workspace import Workspace



STREAM_PROCESS = weakref.WeakKeyDictionary()
def close(f):
    """ Violently close pipes """
    if f in STREAM_PROCESS:
        STREAM_PROCESS[f].kill()
    f.close()

def run(args, stdin=None, stdout=subprocess.PIPE, stderr=None):
    return subprocess.Popen(
        args,
        bufsize=1<<24,
        stdin=stdin,        
        stdout=stdout,
        stderr=stderr,
        close_fds=True,
    )

def execute(args, stdin=None, stdout=None):
    p = run(args, stdin=stdin, stdout=stdout)
    assert p.wait() == 0, 'Failed to execute "%s"' % ' '.join(args)


#def peek_and_pipe(f, n_peek):
#    try:
#        f.seek(0)
#        peek = f.read(n_peek)
#        f.seek(0)
#        f.flush() #Necessary in CPython but noy PyPy to actually seek file
#        return peek, f
#    except IOError: #Non-seekable
#        pass
#
#    script = """
#
#import os, sys, select
#n = %d
#f_in = os.fdopen(os.dup(sys.stdin.fileno()),'rb',0)
#f_out = os.fdopen(os.dup(sys.stdout.fileno()),'wb',0)
#try:
#    peek = f_in.read(n)
#    f_out.write(peek + chr(0) * (n-len(peek)))
#    f_out.write(peek)
#    chunks = [ ]
#    done = False
#    while not done or chunks:
#        rlist, wlist, elist = select.select([ f_in ] if len(chunks) < 16 else [ ], [ f_out ] if chunks else [ ], [ ])
#        if wlist:
#            f_out.write(chunks.pop(0))
#        elif rlist:
#            chunk = f_in.read(1<<16)
#            if not chunk:
#                done = True                
#            else:
#                chunks.append( chunk )
#except IOError, error:
#    if error.errno != 32: #Broken pipe
#        raise error
#except KeyboardInterrupt:
#    sys.exit(1)
#
#""" % n_peek
#
#    p = legion.subprocess_Popen(
#         [sys.executable,'-u','-c',script],
#         bufsize=0, #Random crashes if set to, eg, 1<<20
#         stdin=f,       
#         stdout=subprocess.PIPE,
#         close_fds=True,
#         )
#    f.close()
#    
#    peek = p.stdout.read(n_peek).rstrip(chr(0))
#    d = os.dup(p.stdout.fileno())
#    p.stdout.close()
#    f_out = os.fdopen(d,'rb', 1<<20)
#    STREAM_PROCESS[f_out] = p
#    
#    return peek, f_out
#
#def process_buffer(f):
#    return peek_and_pipe(f, 0)[1]  


def is_remote_filename(filename):
    return bool( re.match('\w+:', filename) )

def abspath(*components):
    """ Absolute path of a filename.
        Note: this also ensures the filename does not look like a flag.
    """    
    filename = os.path.join(*components)

    if is_remote_filename(filename):
        return filename
    else:
        return os.path.abspath(filename)

#def open_possibly_remote_file(filename):
#    """ Use lftp to read remote files.
#    """
#
#    if not is_remote_filename(filename):
#        # Doesn't look like a URL
#        return open(filename, 'rb')
#    
#    p = legion.subprocess_Popen(
#         ['lftp', '-c', 'cat', filename],
#         stdout=subprocess.PIPE,
#         close_fds=True,
#         )
#    return p.stdout
    
def open_possibly_compressed_file(filename):
    """ Notionally, cast "filename" to a file-like object.
    
        If filename is already file-like, return it.
        If it's compressed, return a decompressing file-like object.
        If it's a BAM file, return a file-like object that produces SAM format.
        Otherwise, just return an open file!
    """
    if hasattr(filename, 'read'):
        return filename #It's already file-like
        
    from nesoni import sam    
    
    f = open(filename,'rb')
    peek = f.read(4)
    f.close()

    if peek.startswith('\x1f\x8b'): #gzip format
        if sam.is_bam(filename): #it might be a BAM
            return sam.open_bam(filename)
            
        return gzip.open(filename, 'rb')
    elif peek.startswith('BZh'): #bzip2 format
        return bz2.BZFile(filename, 'rb')
    else:
        return open(filename, 'rb')


def copy_file(source, dest):
    f_in = open_possibly_remote_file(source)
    f_out = open(dest, 'wb')
    while True:
        text = f_in.read(1<<20)
        if not text: break
        f_out.write(text)
    f_out.close()
    f_in.close()


class Pipe_writer(object):
    """ Write to a file via another process. 
    
        Buffering to avoid slowness in pypy.
        
        Drop-in replacement for a file, assuming
        you only use write and close.
    """

    def __init__(self, filename, command):
        self.command = command
        f_out = open(filename,'wb')
        self.process = subprocess.Popen(
            command,
            stdin = subprocess.PIPE,
            stdout = f_out,
    #        bufsize = 1<<24,
            close_fds = True
        )
        f_out.close()
        
        #self.buffer = [ ]
        #self.buf_size = 0

    #def write(self, text):
    #    self.buffer.append( text )
    #    self.buf_size += len(text)
    #    if self.buf_size >= 1<<20: self.flush_buffer()
    
    #def flush_buffer(self):
    #    self.process.stdin.write( ''.join(self.buffer) )
    #    self.buffer = [ ]
    #    self.buf_size = 0
    
    def fileno(self):
        return self.process.stdin.fileno()
    
    def write(self, text):
        self.process.stdin.write( text )
    
    def flush_buffer(self):
        pass
    
    def close(self):
        self.flush_buffer()
        self.process.stdin.close()
        assert self.process.wait() == 0, ' '.join(self.command) + ' failed'


def open_gzip_writer(filename):
    return Pipe_writer(filename, ['gzip'])

def open_bzip2_writer(filename):    
    return Pipe_writer(filename, ['bzip2'])

def open_possibly_compressed_writer(filename):
    if filename[-3:].lower() == '.gz':
        return open_gzip_writer(filename)
    elif filename[-4:].lower() == '.bz2':
        return open_bzip2_writer(filename)
    else:
        return open(filename, 'wb')


def read_solid(filename):
    reads_file = open_possibly_compressed_file(filename)
    
    while True:
        line1 = reads_file.readline()
        while line1.startswith('#'):
            line1 = reads_file.readline()
        if not line1: break
        assert line1.startswith('>'), 'Not a SOLiD CSFASTA file?'
        line2 = reads_file.readline()

        read_name = line1.rstrip('\n')[1:]
        read_seq = line2.rstrip('\n')
        yield read_name, read_seq



def read_illumina(filename):
    reads_file = open_possibly_compressed_file(filename)
    
    while True:
        line1 = reads_file.readline()
        if not line1: break
        line2 = reads_file.readline()
        line3 = reads_file.readline()
        line4 = reads_file.readline()
            
        assert line1.startswith('@'), 'Not an Illumina FASTQ file?'
        assert line3.startswith('+'), 'Not an Illumina FASTQ file?'
            
        read_name = line1.rstrip('\n')[1:]
        assert read_name, 'FASTQ file contains record with no name'
        
        read_seq = line2.rstrip('\n')
        yield read_name, read_seq

def read_illumina_with_quality(filename):
    reads_file = open_possibly_compressed_file(filename)
    
    while True:
        line1 = reads_file.readline()
        if not line1: break
        line2 = reads_file.readline()
        line3 = reads_file.readline()
        line4 = reads_file.readline()
            
        assert line1.startswith('@'), 'Not an Illumina FASTQ file?'
        assert line3.startswith('+'), 'Not an Illumina FASTQ file?'
            
        read_name = line1.rstrip('\n')[1:]
        read_seq = line2.rstrip('\n')
        read_qual = line4.rstrip('\n')
        yield read_name, read_seq, read_qual

def read_fasta(filename):
    reads_file = open_possibly_compressed_file(filename)
    
    line = reads_file.readline()
    while line:
        line = line.rstrip()
        assert line.startswith('>'), 'Not a FASTA file?'
        read_name = line[1:] #.split()[0]
        assert read_name, 'FASTA file contains record with no name'
        
        line = reads_file.readline()
        parts = [ ]
        while line and not line.startswith('>'):
            parts.append(line.rstrip())
            line = reads_file.readline()
        
        yield read_name, ''.join(parts)


def read_gff3_sequence(filename):
    f = open_possibly_compressed_file(filename)
    
    for line in f:
        if line.rstrip() == '##FASTA':
            break
    else:
        raise grace.Error('Tried reading file as a GFF3 but it contains no ##FASTA section')
    
    return read_fasta(f)


def read_genbank_sequence(filename, genbank_callback=None):
    from Bio import SeqIO

    f = open_possibly_compressed_file(filename)
    
    for record in SeqIO.parse(f,'genbank'):
        name = record.id
        if name == '' or name == 'unknown':
            name = record.name
        assert name, 'GENBANK file contains record with no accession or name' 
        
        #Hideous hack: samshrimp makes a copy of each record in a genbank file
        if genbank_callback: genbank_callback(name, record)
        
        yield name, record.seq.tostring()    
    f.close()

def read_empty(filename):
    f = open_possibly_compressed_file(filename)
    f.close()
    return
    yield


def _filter_name(iterator, argument):
    for read in iterator:
        yield (read[0].split()[0],) + read[1:]

def _filter_bar(iterator, argument):
    nth = int(argument)

    for read in iterator:
        parts = read[0].split('|')
        assert len(parts) > nth, 'Not enough parts in: '+name
        yield (parts[nth].strip(),) + read[1:]

def _filter_rename(iterator, argument):
    for read in iterator:
        yield (argument,) + read[1:]

def _filter_select(iterator, argument):
    good = set(argument.split(','))
    for read in iterator:
        if read[0] in good:
            yield read

def _filter_lengthatleast(iterator, argument):
    cutoff = int(argument)
    for read in iterator:
        if len(read[1]) >= cutoff:
            yield read

def _filter_pfilter(iterator, argument):
    for read in iterator:
        variables = {'name':name,'seq':seq}
        if len(read)>2: variables['quality'] = read[2]
        result = eval(argument, variables)
        if not result: continue
        if isinstance(result, str): read = (result,)+read[1:]
        yield read

def _filter_qclip(iterator, argument):
    cutoff = chr(64 + int(argument))
    for name, seq, qual in iterator:
        best_start = 0
        best_end = 0
        start = 0
        for i in xrange(len(qual)):
            if qual[i] < cutoff:
                start = i+1 
            else:
                if i+1-start > best_end-best_start:
                    best_start = start
                    best_end = i+1
        yield name, seq[best_start:best_end], qual[best_start:best_end] 

def _filter_first(iterator, argument):
    n = int(argument)
    for item in iterator:
        if n <= 0: break
        n -= 1
        yield item

FILTERS = {
    'name': _filter_name,
    'bar:': _filter_bar,
    'rename:': _filter_rename,
    'select:': _filter_select,
    'lengthatleast:': _filter_lengthatleast,
    'pfilter:': _filter_pfilter,
    'qclip:': _filter_qclip,
    'first:': _filter_first,
}

def filter_no_qualities(iterator):
    for read in iterator:
        yield read[:2]    

def read_sequences(filename, qualities=False, genbank_callback=None):
    """ Read fasta or illumina sequences, possibly compressed 
    
        Post reading filters can be applied.
    """
    
    parts = filename.split('~~')

    f = open_possibly_compressed_file(parts[0])
    peek = f.read(8)
    f.close()
    
    have_qualities = False
    
    if not peek:
        result = read_empty(parts[0])
    elif peek.startswith('>'):
        result = read_fasta(parts[0])
    elif peek.startswith('LOCUS'):
        result = read_genbank_sequence(parts[0], genbank_callback)
    elif peek.startswith('@'):
        have_qualities = True
        result = read_illumina_with_quality(parts[0])    
    elif peek.startswith('##gff'):
        result = read_gff3_sequence(parts[0])
    elif peek.startswith('.sff'):
        f.close()
        grace.require_sff2fastq()
        have_qualities = True
        process = run(['sff2fastq', parts[0]])
        result = read_illumina_with_quality(process.stdout)
    else:
        raise grace.Error('Unrecognized file format for '+filename)
    
    for part in parts[1:]:
        for prefix in FILTERS:
            if part.lower().startswith(prefix):
                result = FILTERS[prefix](result, part[len(prefix):])
                break
        else:
            raise grace.Error('Unrecognized filter: '+part)

    if have_qualities and not qualities:
        result = filter_no_qualities(result)
    
    return result   


def is_sequence_file(filename):
    if not os.path.isfile(filename): 
        return False
    try:
        read_sequences(filename)
    except grace.Error:
        return False
    return True


def guess_quality_offset(filename):
    grace.status('Guessing quality offset')
    try:
        min_value = chr(255)
        #max_value = chr(0)
        for i, item in enumerate(read_sequences(filename, qualities=True)):
            if len(item) == 2: return 33 #Not fastq
            
            min_value = min(min_value, min(item[2]))
            #max_value = max(max_value, max(item[2]))
            
            if i >= 100000: break
        
        low = ord(min_value)
        #high = ord(max_value)
        #print 'Quality chars in range %d-%d in %s' % (low,high,filename)
        if low < 59: return 33 #Sanger and Illumina 1.8+
        return 64 #Illumina pre 1.8
    finally:
        grace.status('')


def check_name_uniqueness(read_filenames, pair_filenames=[], interleaved_filenames=[]):
    """ Check first few read names are unique """
    names = set()
    for filename in read_filenames:
        for i, (name, seq) in enumerate(read_sequences(filename)):
            name = name.split()[0]
            assert name not in names, 'Duplicate sequence name: '+name
            names.add(name)
            if i >= 1000: break

    for filename1, filename2 in pair_filenames:
        for i, ((name1, seq1), (name2, seq2)) in enumerate(itertools.izip(
            read_sequences(filename1),
            read_sequences(filename2),
        )):
            name1 = name1.split()[0]
            name2 = name2.split()[0]
            assert name1 not in names, 'Duplicate sequence name: '+name1
            assert name2 not in names, 'Duplicate sequence name: '+name2
            assert name1[:-4] == name2[:-4], 'Read pair with dissimilar names: '+name1+', '+name2
            names.add(name1)
            names.add(name2)
            if i >= 1000: break
    
    for filename in interleaved_filenames:
        iterator = read_sequences(filename)
        for i in xrange(1000):
            try:
                name1, seq1 = iterator.next()
            except StopIteration: break
            try:
                name2, seq2 = iterator.next()
            except StopIteration:
                assert False, 'Interleaved read file with odd number of reads.'
            name1 = name1.split()[0]
            name2 = name2.split()[0]
            assert name1 not in names, 'Duplicate sequence name: '+name1
            assert name2 not in names, 'Duplicate sequence name: '+name2
            assert name1[:-4] == name2[:-4], 'Read pair with dissimilar names: '+name1+', '+name2
            names.add(name1)
            names.add(name2)
            


def write_fasta(f, name, sequence, qual=None):
    print >> f, '>' + name
    for i in xrange(0,len(sequence),70):
        print >> f, sequence[i:i+70] 

def write_fasta_single_line(f, name, sequence, qual=None):
    print >> f, '>' + name
    print >> f, sequence 

def write_fastq(f, name, sequence, qual):
    print >> f, '@' + name
    print >> f, sequence
    #for i in xrange(0,len(sequence),70):
    #    print >> f, sequence[i:i+70]
    print >> f, '+' 
    print >> f, qual
    #for i in xrange(0,len(qual),70):
    #    print >> f, qual[i:i+70]



def decode_evidence(desc):
    result = [ ]
    for item in desc.split():
        match = re.match('(.*)x([0-9]+)$', item)
        result.append( (match.group(1).replace('"',''), int(match.group(2))) )
        # Old evidence format example: "A"x42
        # New evidence format example: Ax42
        # Handle both
    return result

def read_evidence_file(filename):
    f = open(filename,'rb')
    f.readline()
    for line in f:
        parts = line.rstrip('\n').split('\t')
        yield int(parts[0]), parts[1], parts[2], parts[3]



class _Named_list(object):
    """ Abstract base class of named lists. 
        Behaves very much like a dictionary.
    """
    def __init__(self, values):
        assert len(values) == len(self._keys)
        if self._value_type:
            for item in values:
                assert isinstance(item, self._value_type)
        self._values = values
        
    def __len__(self):
        return len(self._keys)
    
    def __iter__(self):
        return iter(self._keys)
    
    def __getitem__(self, key):
        return self._values[self._key_map[key]]
    
    def __setitem__(self, key, value):
        self._values[self._key_map[key]] = value
    
    def __repr__(self):
        return '({%s})' % (', '.join( '%s:%s' % (repr(a),repr(b)) for a,b in zip(self._keys,self._values) ))

    def value_type(self):
        if self._value_type:
            return self._value_type

        assert self.values, 'Trying to get the type of values in an empty Named_list.'
        result = type(self.values[0])
        for item in self.values:
            assert type(item) == result, 'Trying to get the type of values in a Named_list containing several types of object.'
        return result

    @classmethod
    def keys(self):
        return self._keys
        
    def values(self):
        return self._values
    
    def items(self):
        return zip(self._keys, self._values)     

    @classmethod
    def iterkeys(self):
        return iter(self._keys)
    
    def itervalues(self):
        return iter(self._values)

    def iteritems(self):
        return itertools.izip(self._keys, self._values)


def named_list_type(keys, value_type=None):
    """ Create a named list class. Somewhat forgiving of duplicate names. 
    """
    class Named_list(_Named_list):
        _keys = keys
        _key_map = { }
        _key_bad = set()        
        _value_type = value_type
        
    for i, name in enumerate(keys):
        if name in Named_list._key_map:
            Named_list._key_bad.add(name)
            del Named_list._key_map[name]
        if name not in Named_list._key_bad:
            Named_list._key_map[name] = i

    return Named_list            

def named_list(items, value_type=None):
    """ Create a named list from a list of (name,value) pairs.
    """
    keys = [ a for a,b in items ]
    values = [ b for a,b in items ]
    return named_list_type(keys, value_type)(values)


class Table_reader(object):
    def __init__(self, filename):
        self.f = open(filename, 'rb')
        line = self.f.readline()
        self.groups = [ ]
        while line and line.startswith('#') or not line.strip():
            if line.startswith('#Groups'):
                self.groups = line.rstrip('\n').split(',')
            line = self.f.readline()    
        
        assert line, 'Table has not even a heading'
        
        if '\t' in line:
            self.parse = lambda line: line.rstrip('\n').split('\t')
        elif ',' in line:
            self.parse = lambda line: csv.reader([line]).next()
        else:
            assert False, 'Strange table'
        
        self.headings = self.parse(line)

        
        if not self.groups:
            #Is it an old counts file?
            i = 0
            while i < len(self.headings) and not self.headings[i].startswith('RPKM '):
                i += 1
            if i < len(self.headings):
                n = i-1
                self.groups = [''] + ['Count']*n + ['RPKM']*n + ['Annotation']*(len(self.headings)-n*2-1)
                
        if not self.groups:
            self.groups = [''] + ['All']*(len(self.headings)-1)
        
        if len(self.groups) < len(self.headings):
            self.groups.extend([''] * (len(self.headings)-len(self.groups)))
        
        self.groups[0] = ''
        for i in xrange(1,len(self.groups)):
            if not self.groups[i]:
                self.groups[i] = self.groups[i-1] or 'All'
        
        self.row_type = named_list_type(self.headings)
    
    def __iter__(self):
        return self
        
    def next(self):
        while True:
            line = self.f.readline()
            if not line: raise StopIteration()        
            if line.startswith('#') or not line.strip(): continue
            
            values = self.parse(line)
            if not values: continue
            
            assert len(values) == len(self.headings)
            #return collections.OrderedDict(zip(self.headings,values))
            return self.row_type(values)

read_table = Table_reader


def read_grouped_table(filename, group_cast={'All':str}):
    """ 
    Read some groups of columns from a grouped-column table file.
    
    A grouped column table file is
    - CSV (preferred) or tab separated
    - The first column is a row name column
    - May contain comments starting with #
    - May contain a line starting with #Groups specifying the group of each column.
      This is a comma separated list.
    
    If a #Groups line is not present, all columns belong to group 'All'.
    
    group_cast is a dictionary specifying a parser for the values in each group
    """

    reader = Table_reader(filename)

    group_types = { }
    groups = { }
    group_columns = { }
    for group in group_cast:
        groups[group] = [ ]
        group_columns[group] = [ ]
        for i, group1 in enumerate(reader.groups):
            if group == group1:
                group_columns[group].append(i)
        assert group_columns[group], '"%s" group is missing from table file' % group
        
        group_types[group] = named_list_type(
            [ reader.headings[index] for index in group_columns[group] ]
        )
    
    names = [ ]
    for record in reader:
        names.append(record._values[0])        
        for group in groups:
            groups[group].append(group_types[group]([
                group_cast[group]( record._values[index] ) for index in group_columns[group]
            ]))

    return dict(
        (group, named_list_type(names,group_types[group])(groups[group]))
        for group in groups
    )


def write_grouped_csv(filename, groups, rowname_name='Name', comments=[], group_line=True):
    """
    Write some groups of columns to a file in CSV format.
    
    groups should be a list of tuple (group name, data)
    where data is a named_list of named_lists
    """
    group_names = [ '#Groups' ]
    column_names = [ rowname_name ]
    rownames = groups[0][1].keys()
    for name, table in groups:
        group_names.extend([ name ] * len(table.value_type().keys()))
        column_names.extend(table.value_type().keys())
        assert table.keys() == rownames
    
    with open(filename, 'wb') as f:
        for line in comments:
            f.write('#%s\n' % line)
            
        writer = csv.writer(f)
        if group_line:
            writer.writerow(group_names)
        writer.writerow(column_names)
        for i, rowname in enumerate(rownames):
            writer.writerow(
                [ rowname ] +
                [ item #str(item)
                  for _, table in groups
                  for item in table.values()[i].values()
                ]
            )
        

def write_csv(filename, iterable, comments=[]):
    """ Write a sequence of OrderedDicts of strings as a CSV 
    
        Keys may be either simply a string or tuples of (group, column_name)
        The first item is the row name, and can't have a group
    """
    f = open(filename, 'wb')
    
    for line in comments:
        f.write('#%s\n' % line)
    
    writer = csv.writer(f)
    keys = None
    
    for record in iterable:
        if keys is None:
           keys = record.keys()
           
           groups = [ ]
           names = [ ]
           any_groups = False
           for item in keys:
               if isinstance(item,tuple):
                   group, name = item
                   groups.append(group)
                   names.append(name)
                   any_groups = True
               else:
                   groups.append('All')
                   names.append(item)
           
           if any_groups:
               print >> f, '#Groups,' + ','.join(groups[1:])
           
           writer.writerow(names)
        assert record.keys() == keys
        writer.writerow(record.values())
    f.close()







