#!/usr/bin/python

# Apache 2 license 

import os

'''
Testing stub for query service returns mock metadata for any query
'''

class FakeQuery(object):
    ''' Takes a query string then queries the keyservice 
    returning a list of metadata matched for the query.
    '''

    def __init__(self, cancer_type="t", file_type="f", file_name="n"):
	''' constructor for setting the keynames that will be used 
	to describe what type of cancer, file and the filename'''
	self.cancer_type = cancer_type
	self.file_type = file_type
	self.file_name = file_name
	

    def run_query(self, query_string):
        ''' There is no clear set of parameters or options for the
        query as it is updated when the metadata is consumed and sent
        to a database of values.  We will asssume all errors are handled
        by the keyservice.
    
        Returns list of metdata for files
        '''

	# We format this as list of dicts ala JSON
	return [
	    {
		self.cancer_type: "fake_cancer",
		self.file_type: "bam",
		self.file_name: "test1.bam"
	    },
	    {
		self.cancer_type: "fake_cancer",
		self.file_type: "bam",
		self.file_name: "test2.bam"
	    }]

class FakeFileAssociate(object):
    ''' Returns a dictionary of filepath and names with the keys being
    symlinks to create and the values being the original files to be the
    targets of the links '''

    def __init__(self, old_dir='/tmp/qtool/olddir', new_dir='/tmp/qtool/newdir'):
	self.old_dir = old_dir
	self.new_dir = new_dir	


    def associate(self, metadata):
	''' Create files using the metadata dictionary.'''
	return { 
	    os.path.join(self.new_dir, 'test1.bam'):
		os.path.join(self.old_dir, 'test1.bam'),
	    os.path.join(self.new_dir, 'test2.bam'):
		os.path.join(self.old_dir, 'test2.bam')
	}

 
class FileMaker(object):
    ''' Given a dictionary of link names and targets create those symlinks
    '''

    def create_links(self, link_associations):
	''' Given a dictionary of link names and targets create those 
	symlinks'''
	for link_name, target in link_associations.items():
	    os.symlink(target, link_name)
 
