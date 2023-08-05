import re, os
from autograde.models import *
from django.core.files import File
from zipfile import ZipFile


def parse(directory):
    """
    Parses the README file and creates the required models
    """
    def flushBuffer(buf, results):
        results[current_header] = buf
        return [], results
    header_patt = r'-{5}-*([a-zA-Z]*)'
    results = {} # maps section names to a list containing the content from the section
    sections = ['description', 'dependencies', 'tests', 'verification', 'student']
    with open(directory+'/README.txt') as readme:
        section_buffer = []
        current_header = re.match(header_patt, readme.readline()).groups()[0]
        for line in readme:
            line = line.split('\n')[0]
            match = re.match(header_patt, line)
            if match:
                section_buffer, results = flushBuffer(section_buffer, results)
                current_header = match.groups()[0].lower()
                if current_header not in sections:
                    raise ValueError('Invalid header name: ' + current_header)
            else:
                section_buffer.append(line)
    section_buffer, results = flushBuffer(section_buffer, results)
    p = makeModels(results,directory)
    return p

def makeModels(readme_sections, root_dir):
    proj = Project()
    proj.save()
    files = []
    print readme_sections, root_dir
    def makeDescription():
        files = []
        results = {}
        subsection_patt = r'^\s*#(.*)'
        subsection_buffer = []
        current_header = ''
        def flushSubsection(buf, results):
            if buf == []:
                return [], results
            else:
                results[current_header] = buf
                return [], results
        for line in readme_sections['description']:
            line = line.split('\n')[0]
            match = re.match(subsection_patt, line)
            if match:
                subsection_buffer, results = flushSubsection(subsection_buffer, results)
                current_header = match.groups()[0].lower()
            else:
                subsection_buffer.append(line)
        subsection_buffer, results = flushSubsection(subsection_buffer, results)
        for k,v in results.items():
            p = KVPair(key=k, value=v)
            p.save()
            proj.settings.add(p)

    def makeDependencies():
        files = []
        for line in readme_sections['dependencies']:
            line = line.split('\n')[0]
            for direc in os.walk(root_dir+'/'+line):
                for f in direc[2]:
                    p = ProjectFile(my_file=File(open(f, 'rw')))
                    p.project = proj
                    p.save()
                    files.append(root_dir+'/'+line)
        return files
    
    def makeTests():
        # only working for single level directories
        files = []
        for line in readme_sections['tests']:
            path = root_dir+'/'+line.split('\n')[0]
            for direc in os.walk(path):
                for f in direc[2]:
                    with open(path+'/'+f, 'rw') as g:
                        p = TestCase(my_file=File(g))
                        p.project = proj
                        p.save()
                        files.append(path+'/'+f)
        return files

    def makeStudent():
        regex_patt = r'/(".*)'
        current_folder = ''
        for line in readme_sections['student']:
            line = line.split('\n')[0]
            match = re.search(regex_patt, line)
            if match:
                p = KVPair(key=current_folder, value=match.groups()[0])
                p.save()
                proj.student_files.add(p)
            else:
                current_folder = line

    makeDescription()
    #files.exetend(makeDependencies())
    makeStudent()
    files.extend(makeTests())
    #files.extend(makeVerification())
    zipped = ZipFile('zipped_files.zip', mode='w')
    for f in files:
        zipped.write(f)
    zipped.close()
    proj.zipped = File(file('zipped_files.zip'))
    proj.save()
    from os import unlink
    os.unlink('zipped_files.zip')
    #print 'proj.zipped', proj.zipped
    return True
