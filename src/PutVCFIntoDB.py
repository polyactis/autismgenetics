#!/usr/bin/env python
"""

Examples:
	PutVCFIntoDB.py -i /...vcf -u yh -c
	
	PutVCFIntoDB.py -i /home//alden/batch020411_new/tau_cons_recal.vcf
		-u yh -c -b -n test_data_from_alden_tau_cons_recal
	
Description:
	2011-2-4
		This program imports genotype data in a VCF file (both plain and gzipped) into db.
			It adds individuals (column name excluding ".bam" if present in vcf) into db if they are not there,
				also inserts relevant data into GenotypeMethod, GenotypeFile, Locus, AlleleType, Sequence.
			If 'GQ' is not available in vcf file, 'DP' is taken as score.
		Right now, it only deals with SNPs (reference, alternative, missing).
		
"""
import sys, os, math
#bit_number = math.log(sys.maxint)/math.log(2)
#if bit_number>40:       #64bit
sys.path.insert(0, os.path.expanduser('~/lib/python'))
sys.path.insert(0, os.path.join(os.path.expanduser('~/script')))

import time, csv, getopt
import warnings, traceback, re, gzip

import AutismDB
from pymodule.utils import runLocalCommand, getColName2IndexFromHeader

class PutVCFIntoDB(object):
	__doc__ = __doc__
	option_default_dict = {('drivername', 1,):['postgresql', 'v', 1, 'which type of database? mysql or postgresql', ],\
							('hostname', 1, ): ['localhost', 'z', 1, 'hostname of the db server', ],\
							('dbname', 1, ): ['autismdb', 'd', 1, 'database name', ],\
							('schema', 0, ): [None, 'k', 1, 'database schema name', ],\
							('db_user', 1, ): [None, 'u', 1, 'database username', ],\
							('db_passwd', 1, ): [None, 'p', 1, 'database password', ],\
							("input_fname", 1, ): [None, 'i', 1, 'genotype file stored in VCF format'],\
							("genotype_method_name", 1, ): ['', 'n', 1, 'name designated in db for this batch of genotype data'],\
							("run_type", 1, int): [1, 'y', 1, ''],\
							('commit', 0, int):[0, 'c', 0, 'commit db transaction'],\
							('debug', 0, int):[0, 'b', 0, 'toggle debug mode, transaction mode disabled.'],\
							('report', 0, int):[0, 'r', 0, 'toggle report, more verbose stdout/stderr.']}
	
	def __init__(self,  **keywords):
		"""
		
		"""
		from pymodule import ProcessOptions
		self.ad = ProcessOptions.process_function_arguments(keywords, self.option_default_dict, error_doc=self.__doc__, class_to_have_attr=self)
	
	def addIndividualAndGenotypeFile(self, db, genotypeMethod, header, col_name2index, sampleStartingColumn=9,\
						genotype_file_header = ['locus.id', 'allele_order', 'allele_type.id', 'seq.id', 'score', 'target_locus.id']):
		"""
		2011-3-4
			adjust the col_name2index because sometimes individual names are not same as the column names if they contain a trailing .bam
		2011-3-1
			column name excluding the trailing ".bam" (if it's present) in vcf is taken as Individual.code.
		2011-2-11
			This function adds individuals and affiliated genotype file entries into db.
			It returns a dictionary mapping individual's column name to a genotype file handler.
		"""
		sys.stderr.write("Adding individuals and affiliated genotype files into db ...")
		no_of_cols = len(header)
		individual_name2fileHandler = {}	#individual's column name -> an opened file handler to store genetic data
		counter = 0
		for i in xrange(sampleStartingColumn, no_of_cols):
			individualName = header[i]
			col_index = col_name2index.get(individualName)	#2011-3-4
			if not individualName:	#ignore empty column
				continue
			if individualName[:-4]=='.bam':
				individualCode = individualName[:-4]	#get rid of .bam
			else:
				individualCode = individualName
			col_name2index[individualCode] = col_index	#2011-3-4
			individual = db.getIndividual(individualCode)
			
			genotypeFile = db.getGenotypeFile(individual, genotypeMethod)
			genotype_file_abs_path = os.path.join(db.data_dir, genotypeFile.filename)
			if os.path.isfile(genotype_file_abs_path):
				sys.stderr.write("Warning: %s already exists. Program exits.\n"%(genotype_file_abs_path))
				sys.exit(3)
			fileHandler = csv.writer(open(genotype_file_abs_path, 'w'), delimiter='\t')
			fileHandler.writerow(genotype_file_header)
			individual_name2fileHandler[individualName] = fileHandler
			counter += 1
		sys.stderr.write("%s individuals added. Done.\n"%(counter))
		return individual_name2fileHandler
	
	def addOneFIle(self, db, input_fname, genotypeMethod):
		"""
		2011-2-25
			can deal with gzipped vcf file now.
			if 'GQ' is not available, 'DP' is taken as score.
		2011-2-4
			one VCF file.
		"""
		sys.stderr.write("Adding genotype data from %s into db ...\n"%(input_fname))
		import csv
		if input_fname[-2:]=='gz':
			inf = gzip.open(input_fname, 'rb')
		else:
			inf = open(input_fname)
		reader = csv.reader(inf, delimiter='\t')
		ref_allele_type = db.getAlleleType('reference')
		alt_allele_type = db.getAlleleType('substitution')
		missing_allele_type = db.getAlleleType('missing')
		
		individual_name2fileHandler = None
		col_name2index = None
		counter = 0
		for row in reader:
			if row[0][:2] == '##': 		# to skip all prior comments
				pass
			elif row[0] =='#CHROM':
				row[0] = 'CHROM'	#discard the #
				header = row
				col_name2index = getColName2IndexFromHeader(header, skipEmptyColumn=True)
				individual_name2fileHandler = self.addIndividualAndGenotypeFile(db, genotypeMethod, header, col_name2index)
			else:
				chr = row[col_name2index['CHROM']]
				if chr[:3]=='chr':	#get rid of "chr"
					chr = chr[3:]
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
					genotype_quality_index = format_column_name2index.get('GQ')
					if genotype_quality_index is None:
						genotype_quality_index = format_column_name2index.get('DP')
					genotype_quality = genotype_data_ls[genotype_quality_index]
					if genotype_call=='./.':
						score = ''
						data_row_1 = [locus.id, 1, missing_allele_type.id, '', score, '']
						data_row_2 = [locus.id, 2, missing_allele_type.id, '', score, '']
					elif genotype_call =='1/0':		# treated same as 0/1
						score = float(genotype_quality)
						data_row_1 = [locus.id, 1, ref_allele_type.id, ref_seq.id, score, '']
						data_row_2 = [locus.id, 2, alt_allele_type.id, alt_seq.id, score, '']
					elif genotype_call =='1/1':
						score = float(genotype_quality)
						data_row_1 = [locus.id, 1, alt_allele_type.id, alt_seq.id, score, '']
						data_row_2 = [locus.id, 2, alt_allele_type.id, alt_seq.id, score, '']
					elif genotype_call =='0/1':
						score = float(genotype_quality)
						data_row_1 = [locus.id, 1, ref_allele_type.id, ref_seq.id, score, '']
						data_row_2 = [locus.id, 2, alt_allele_type.id, alt_seq.id, score, '']
					elif genotype_call =='0/0':
						score = float(genotype_quality)
						data_row_1 = [locus.id, 1, ref_allele_type.id, ref_seq.id, score, '']
						data_row_2 = [locus.id, 2, ref_allele_type.id, ref_seq.id, score, '']
					fileHandler.writerow(data_row_1)
					fileHandler.writerow(data_row_2)
				counter += 1
			if counter>0 and counter%5000==0:
				sys.stderr.write("%s\t%s"%('\x08'*80, counter))
		sys.stderr.write("\t %s total genotypes Done.\n"%counter)
	
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
		if not self.debug:	#in debug mode, disable transaction to see db commit immediately.
			session.begin()
		
		if not db.data_dir:
			sys.stderr.write("Filesystem storage is not available. Exit.\n")
			sys.exit(0)
		
		genotype_dir = 'genotype'
		genotype_data_abs_path =  os.path.join(db.data_dir, genotype_dir)
		if not os.path.isdir(genotype_data_abs_path):
			os.makedirs(genotype_data_abs_path)
		
		genotypeMethod = db.findGenotypeMethodGivenName(self.genotype_method_name)
		if self.input_fname[-2:]=='gz':
			db_vcf_filename_suffix = 'vcf.gz'
		else:
			db_vcf_filename_suffix = 'vcf'
		genotypeMethod.vcf_filename = os.path.join(genotype_dir, 'genotypeMethod%s.%s'%\
												(genotypeMethod.id, db_vcf_filename_suffix))
		vcf_abs_path = os.path.join(db.data_dir, genotypeMethod.vcf_filename)
		if os.path.isfile(vcf_abs_path):
			sys.stderr.write("Warning: %s already exists. No overwriting it by copying input file."%(vcf_abs_path))
			sys.exit(2)
		else:
			runLocalCommand('cp %s %s'%(self.input_fname, vcf_abs_path), report_stderr=True, report_stdout=True)
		
		genotypeMethod.genotype_file_dir = os.path.join(genotype_dir, 'genotypeMethod%s'%(genotypeMethod.id))
		genotype_file_dir_abs_path = os.path.join(db.data_dir, genotypeMethod.genotype_file_dir)
		if not os.path.isdir(genotype_file_dir_abs_path):
			os.makedirs(genotype_file_dir_abs_path)
		
		self.addOneFIle(db, self.input_fname, genotypeMethod)
		
		
		if self.commit:
			session.commit()
		else:	#default is rollback(). to demonstrate good programming
			session.rollback()

if __name__ == '__main__':
	from pymodule import ProcessOptions
	main_class = PutVCFIntoDB
	po = ProcessOptions(sys.argv, main_class.option_default_dict, error_doc=main_class.__doc__)
	
	instance = main_class(**po.long_option2value)
	instance.run()
