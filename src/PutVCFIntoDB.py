#!/usr/bin/env python
"""

Examples:
	PutVCFIntoDB.py -i /...vcf -u yh -c
	
Description:
	2011-2-4
"""
import sys, os, math
#bit_number = math.log(sys.maxint)/math.log(2)
#if bit_number>40:       #64bit
sys.path.insert(0, os.path.expanduser('~/lib/python'))
sys.path.insert(0, os.path.join(os.path.expanduser('~/script')))

import time, csv, getopt
import warnings, traceback, re

import AutismDB
from pymodule.util import runLocalCommand, getColName2IndexFromHeader

class PutVCFIntoDB(object):
	__doc__ = __doc__
	option_default_dict = {('drivername', 1,):['postgresql', 'v', 1, 'which type of database? mysql or postgresql', ],\
							('hostname', 1, ): ['localhost', 'z', 1, 'hostname of the db server', ],\
							('dbname', 1, ): ['autismdb', 'd', 1, 'database name', ],\
							('schema', 0, ): [None, 'k', 1, 'database schema name', ],\
							('db_user', 1, ): [None, 'u', 1, 'database username', ],\
							('db_passwd', 1, ): [None, 'p', 1, 'database password', ],\
							("input_fname", 1, ): [None, 'i', 1, 'genotype file stored in VCF format'],\
							("genotypeMethodName", 1, ): ['', 'n', 1, 'name designated in db for this batch of genotype data'],\
							("run_type", 1, int): [1, 'y', 1, ''],\
							('commit', 0, int):[0, 'c', 0, 'commit db transaction'],\
							('debug', 0, int):[0, 'b', 0, 'toggle debug mode'],\
							('report', 0, int):[0, 'r', 0, 'toggle report, more verbose stdout/stderr.']}
	
	def __init__(self,  **keywords):
		"""
		
		"""
		from pymodule import ProcessOptions
		self.ad = ProcessOptions.process_function_arguments(keywords, self.option_default_dict, error_doc=self.__doc__, class_to_have_attr=self)
	
	def addIndividualAndGenotypeFile(self, db, genotypeMethod, header, col_name2index):
		"""
		2011-2-11
		"""
		sys.stderr.write("Adding individuals and affiliated genotype files ...")
		no_of_cols = len(header)
		individual_name2fileHandler = {}
		counter = 0
		for i in xrange(9, no_of_cols):
			individualName = header[i]
			individualCode = individualName[:-4]	#get rid of .bam
			individual = db.getIndividual(individualCode)
			
			genotypeFile = db.getGenotypeFile(individual, genotypeMethod)
			fileHandler = csv.writer(open(genotypeFile.filename, 'w'), delimiter='\t')
			header = ['locus.id', 'allele_order', 'allele_type.id', 'seq.id', 'score', 'target_locus.id']
			fileHandler.writerow(header)
			individual_name2fileHandler[individualName] = fileHandler
			counter += 1
		sys.stderr.write("%s individuals added. Done.\n"%(counter))
		return individual_name2fileHandler
	
	def addOneFIle(self, db, input_fname, genotypeMethod):
		"""
		2011-2-4
		"""
		import csv
		session = db.session
		reader = csv.reader(open(input_fname), delimiter='\t')
		ref_allele_type = db.getAlleleType('reference')
		alt_allele_type = db.getAlleleType('substitution')
		missing_allele_type = db.getAlleleType('missing')
		
		individual_name2fileHandler = None
		col_name2index = None
		
		for row in reader:
			# to skip all prior comments
			if row[0][:2] == '##':
				pass
			elif row[0] =='#CHROM':
				row[0] = 'CHROM'	#discard the #
				header = row
				col_name2index = getColName2IndexFromHeader(header)
				individual_name2fileHandler = self.addIndividualAndGenotypeFile(db, genotypeMethod, header, col_name2index)
			else:
				chr = row[col_name2index['CHROM']]
				start = int(row[col_name2index['POS']])
				ref_seq = db.getUniqueSequence(row[col_name2index['REF']])
				alt_seq = db.getUniqueSequence(row[col_name2index['ALT']])
				locus  = db.getLocus(chr, start, ref_seq=ref_seq, alt_seq=alt_seq)
				
				format_column = row[col_name2index['FORMAT']]
				format_column_ls = format_column.split(':')
				format_column_name2index = getColName2IndexFromHeader(format_column_ls)
				for individual_name, fileHandler in individual_name2fileHandler.iteritems():
					individual_col_index = col_name2index[individual_name]
					genotype_data = row[individual_col_index]
					genotype_data_ls = genotype_data.split(':')
					genotype_call = genotype_data_ls[format_column_name2index['GT']]
					genotype_quality = genotype_data_ls[format_column_name2index['GQ']]
					if genotype_call=='./.':
						allele_type = missing_allele_type
						score = ''
						data_row_1 = [locus.id, 1, allele_type.id, '', score, '']
						data_row_2 = [locus.id, 2, allele_type.id, '', score, '']
					elif genotype_call =='1/0':
						score = float(genotype_quality)
						data_row_1 = [locus.id, 1, ref_allele_type.id, '', score, '']
						data_row_2 = [locus.id, 2, ref_allele_type.id, '', score, '']
					elif genotype_call =='1/1':
						score = float(genotype_quality)
						data_row_1 = [locus.id, 1, ref_allele_type.id, '', score, '']
						data_row_2 = [locus.id, 2, alt_allele_type.id, '', score, '']
					elif genotype_call =='0/1':
						score = float(genotype_quality)
						data_row_1 = [locus.id, 1, alt_allele_type.id, '', score, '']
						data_row_2 = [locus.id, 2, alt_allele_type.id, '', score, '']
					
					fileHandler.writerow(data_row_1)
					fileHandler.writerow(data_row_2)
	
	def run(self):
		"""
		2011-2-4
		"""
		if self.debug:
			import pdb
			pdb.set_trace()
			
		db = AutismDB.AutismDB(drivername=self.drivername, username=self.db_user,
						password=self.db_passwd, hostname=self.hostname, database=self.dbname, schema=self.schema)
		db.setup(create_tables=False)
		session = db.session
		#session.begin()
		
		dataDirEntry = AutismDB.README.query.filter_by(title='data_dir').first()
		if not dataDirEntry or not dataDirEntry.description or not os.path.isdir(dataDirEntry.description):
			# todo: need to test dataDirEntry.description is writable to the user
			sys.stderr.write("data_dir not available in db or not accessible on the harddisk. quit.\n")
			sys.exit(2)
		
		data_dir = dataDirEntry.description
		genotype_dir = os.path.join(data_dir, 'genotype')
		if not os.path.isdir(genotype_dir):
			os.makedirs(genotype_dir)
		
		genotypeMethod = db.findGenotypeMethodGivenName(session, self.genotypeMethodName)
		genotypeMethod.vcf_filename = os.path.join(genotype_dir, 'genotypeMethod%s.vcf'%genotypeMethod.id)
		
		runLocalCommand('cp %s %s'%(self.input_fname, genotypeMethod.vcf_filename), report_stderr=True, report_stdout=True)
		
		genotypeMethod.genotype_file_dir = os.path.join(genotype_dir, 'genotypeMethod%s'%(genotypeMethod.id))
		if not os.path.isdir(genotypeMethod.genotype_file_dir):
			os.makedirs(genotypeMethod.genotype_file_dir)
		
		self.addOneFIle(db, self.input_fname, genotypeMethod)
		
		
		if self.commit:
			session.commit()
			session.clear()
		else:	#default is rollback(). to demonstrate good programming
			session.rollback()

if __name__ == '__main__':
	from pymodule import ProcessOptions
	main_class = PutVCFIntoDB
	po = ProcessOptions(sys.argv, main_class.option_default_dict, error_doc=main_class.__doc__)
	
	instance = main_class(**po.long_option2value)
	instance.run()