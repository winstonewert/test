import os
import tempfile
import shutil
from stylus import execute_stylus_plan
from data import BLACKLIST, IGNORE
from util import drop_extension
import xml.parsers.expat

def find_plans():
    for filename in os.listdir('test_data'):
        try:
            int(filename)
        except ValueError:
            yield filename + ".xml"

def find_genes():
    for path, directories, filenames in os.walk('test_data'):
        for filename in filenames:
            if filename.endswith('.gene'):
                yield filename
def as_xml_elements(source):
    data = []

    parser = xml.parsers.expat.ParserCreate()
    def start_element(name, attrs):
        for element in IGNORE.get(name, ()):
            del attrs[element]
        data.append( ('start', name, attrs) )
    parser.StartElementHandler = start_element
    def end_element(name):
        data.append( ('end', name) )
    parser.EndElementHandler = end_element
    def char_data(cdata):
        data.append( ('data', cdata) )
    parser.CharacterDataHandler = char_data

    parser.Parse( open(source).read() )
    return data

class XMLDifferenceError(Exception):
    pass

def xml_file_compare(correct_file, current_file):
    correct_elements = as_xml_elements(correct_file)
    current_elements = as_xml_elements(current_file)
    for correct_element, current_element in zip(correct_elements, current_elements):
        if correct_element != current_element:
            message = """Baseline File: %s
Current File: %s
XML Files differ!
%s
%s""" % (correct_file, current_file, correct_element, current_element)
            raise XMLDifferenceError(message)

def xml_directory_compare(correct, current):
    for filename in os.listdir(correct):
        if filename.endswith('.xml'):
            correct_file = os.path.join(correct, filename)
            current_file = os.path.join(current, filename)
            xml_file_compare(correct_file, current_file)

def verify_result(plan, gene):
    data_dir = tempfile.mkdtemp()
    try:
        print "Testing", plan, gene
        execute_stylus_plan(gene, plan, './test_data', './sample',
            './sample', './sample/plans', data_dir)
        xml_directory_compare( 
            os.path.join('test_data', drop_extension(plan), drop_extension(gene) ),
            os.path.join(data_dir, drop_extension(gene) )
        )
    finally:
        shutil.rmtree(data_dir)



def main():
    plans = list(find_plans())
    genes = list(find_genes())

    for plan in plans:
        for gene in genes:
            if (drop_extension(gene), drop_extension(plan)) not in BLACKLIST:
                verify_result(plan, gene)

    

if __name__ == '__main__':
    main()