#!/usr/bin/env python
"""
Examples:
	#setup database in postgresql
	AutismDB.py -v postgresql -u crocea -z localhost -d autismdb -k public
	
	#setup database in mysql
	AutismDB.py -u yh -z papaya.usc.edu
	
Description:
	2011-1-18
	This is a wrapper for the autism db database, build on top of elixir.
"""
import sys, os, math
from sqlalchemy.types import LargeBinary

bit_number = math.log(sys.maxint)/math.log(2)
if bit_number>40:	   #64bit
	sys.path.insert(0, os.path.expanduser('~/lib64/python'))
	sys.path.insert(0, os.path.join(os.path.expanduser('~/script64')))
else:   #32bit
	sys.path.insert(0, os.path.expanduser('~/lib/python'))
	sys.path.insert(0, os.path.join(os.path.expanduser('~/script')))

from sqlalchemy.engine.url import URL
from elixir import Unicode, DateTime, String, Integer, UnicodeText, Text, Boolean, Float, Binary, Enum
from elixir import Entity, Field, using_options, using_table_options
from elixir import OneToMany, ManyToOne, ManyToMany
from elixir import setup_all, session, metadata, entities
from elixir.options import using_table_options_handler	#using_table_options() can only work inside Entity-inherited class.
from sqlalchemy import UniqueConstraint, create_engine
from sqlalchemy.schema import ThreadLocalMetaData, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import and_, or_, not_

from datetime import datetime

from pymodule import SNPData
from pymodule.db import ElixirDB, TableClass
import os
import hashlib


__session__ = scoped_session(sessionmaker(autoflush=False, autocommit=True))
#__metadata__ = ThreadLocalMetaData()	#2008-10 not good for pylon

__metadata__ = MetaData()

class README(Entity, TableClass):
	#2008-08-07
	title = Field(String(2000))
	description = Field(String(60000))
	created_by = Field(String(128))
	updated_by = Field(String(128))
	date_created = Field(DateTime, default=datetime.now)
	date_updated = Field(DateTime)
	using_options(tablename='readme', metadata=__metadata__, session=__session__)
	using_table_options(mysql_engine='InnoDB')

class Individual(Entity, TableClass):
	firstname = Field(String(256))
	lastname = Field(String(256))
	sex = Field(Boolean)
	birthdate = Field(DateTime)
	birthplace = Field(String(256))
	created_by = Field(String(128))
	updated_by = Field(String(128))
	date_created = Field(DateTime, default=datetime.now)
	date_updated = Field(DateTime)
	using_options(tablename='individual', metadata=__metadata__, session=__session__)
	using_table_options(mysql_engine='InnoDB')

class Ind2Ind(Entity, TableClass):
	individual1 = ManyToOne('Individual', colname='individual1_id', ondelete='CASCADE', onupdate='CASCADE')
	individual2 = ManyToOne('Individual', colname='individual2_id', ondelete='CASCADE', onupdate='CASCADE')
	relationship_type = ManyToOne('RelationshipType', colname='relationship_type_id', ondelete='CASCADE', onupdate='CASCADE')
	created_by = Field(String(128))
	updated_by = Field(String(128))
	date_created = Field(DateTime, default=datetime.now)
	date_updated = Field(DateTime)
	using_options(tablename='ind2ind', metadata=__metadata__, session=__session__)
	using_table_options(mysql_engine='InnoDB')

class RelationshipType(Entity, TableClass):
	short_name = Field(String(256), unique=True)
	description = Field(String(1024))
	created_by = Field(String(128))
	updated_by = Field(String(128))
	date_created = Field(DateTime, default=datetime.now)
	date_updated = Field(DateTime)
	using_options(tablename='relationship_type', metadata=__metadata__, session=__session__)
	using_table_options(mysql_engine='InnoDB')

class Locus(Entity, TableClass):
	chromosome = Field(String(64))
	position = Field(Integer)
	created_by = Field(String(128))
	updated_by = Field(String(128))
	date_created = Field(DateTime, default=datetime.now)
	date_updated = Field(DateTime)
	using_options(tablename='locus', metadata=__metadata__, session=__session__)
	using_table_options(mysql_engine='InnoDB')

class Allele(Entity, TableClass):
	locus = ManyToOne('Locus', colname='locus_id', ondelete='CASCADE', onupdate='CASCADE')
	allele_type = ManyToOne('AlleleType', colname='allele_type_id', ondelete='CASCADE', onupdate='CASCADE')
	sequence = Field(String(2048))
	created_by = Field(String(128))
	updated_by = Field(String(128))
	date_created = Field(DateTime, default=datetime.now)
	date_updated = Field(DateTime)
	using_options(tablename='allele', metadata=__metadata__, session=__session__)
	using_table_options(mysql_engine='InnoDB')

class AlleleType(Entity, TableClass):
	short_name = Field(String(256), unique=True)
	description = Field(String(1024))
	created_by = Field(String(128))
	updated_by = Field(String(128))
	date_created = Field(DateTime, default=datetime.now)
	date_updated = Field(DateTime)
	using_options(tablename='allele_type', metadata=__metadata__, session=__session__)
	using_table_options(mysql_engine='InnoDB')

class Genotype(Entity, TableClass):
	individual = ManyToOne('Individual', colname='individual_id', ondelete='CASCADE', onupdate='CASCADE')
	allele = ManyToOne('Allele', colname='allele_id', ondelete='CASCADE', onupdate='CASCADE')
	genotype_method = ManyToOne('GenotypeMethod', colname='genotype_method_id', ondelete='CASCADE', onupdate='CASCADE')
	created_by = Field(String(128))
	updated_by = Field(String(128))
	date_created = Field(DateTime, default=datetime.now)
	date_updated = Field(DateTime)
	using_options(tablename='genotype', metadata=__metadata__, session=__session__)
	using_table_options(mysql_engine='InnoDB')
	using_table_options(UniqueConstraint('individual_id', 'allele_id', 'genotype_method_id'))

class GenotypeMethod(Entity, TableClass):
	short_name = Field(String(256), unique=True)
	filename = Field(String(10000))
	description = Field(String(1024))
	created_by = Field(String(128))
	updated_by = Field(String(128))
	date_created = Field(DateTime, default=datetime.now)
	date_updated = Field(DateTime)
	using_options(tablename='genotype_method', metadata=__metadata__, session=__session__)
	using_table_options(mysql_engine='InnoDB')

class GenotypeFile(Entity, TableClass):
	individual = ManyToOne('Individual', colname='individual_id', ondelete='CASCADE', onupdate='CASCADE')
	filename = Field(String(10000))
	genotype_method = ManyToOne('GenotypeMethod', colname='genotype_method_id', ondelete='CASCADE', onupdate='CASCADE')
	comment = Field(String(4096))
	created_by = Field(String(128))
	updated_by = Field(String(128))
	date_created = Field(DateTime, default=datetime.now)
	date_updated = Field(DateTime)
	using_options(tablename='genotype_file', metadata=__metadata__, session=__session__)
	using_table_options(mysql_engine='InnoDB')

class Phenotype(Entity, TableClass):
	individual = ManyToOne('Individual', colname='individual_id', ondelete='CASCADE', onupdate='CASCADE')
	phenotype_method = ManyToOne('PhenotypeMethod', colname='phenotype_method_id', ondelete='CASCADE', onupdate='CASCADE')
	value = Field(Float)
	replicate = Field(Integer)
	created_by = Field(String(128))
	updated_by = Field(String(128))
	date_created = Field(DateTime, default=datetime.now)
	date_updated = Field(DateTime)
	using_options(tablename='phenotoype', metadata=__metadata__, session=__session__)
	using_table_options(mysql_engine='InnoDB')

class PhenotypeMethod(Entity, TableClass):
	short_name = Field(String(256), unique=True)
	description = Field(String(1024))
	created_by = Field(String(128))
	updated_by = Field(String(128))
	date_created = Field(DateTime, default=datetime.now)
	date_updated = Field(DateTime)
	using_options(tablename='phenotype_method', metadata=__metadata__, session=__session__)
	using_table_options(mysql_engine='InnoDB')

class AutismDB(ElixirDB):
	__doc__ = __doc__
	option_default_dict = {('drivername', 1,):['postgresql', 'v', 1, 'which type of database? mysql or postgresql', ],\
						('hostname', 1, ):['localhost', 'z', 1, 'hostname of the db server', ],\
						('database', 1, ):['autismdb', 'd', 1, '',],\
						('schema', 0, ): [None, 'k', 1, 'database schema name', ],\
						('username', 1, ):[None, 'u', 1, 'database username',],\
						('password', 1, ):[None, 'p', 1, 'database password', ],\
						('port', 0, ):[None, 'o', 1, 'database port number'],\
						('pool_recycle', 0, int):[3600, 'l', 1, 'the length of time to keep connections open before recycling them.'],\
						('sql_echo', 0, bool):[False, 's', 0, 'display SQL Statements'],\
						('echo_pool', 0, bool):[False, 'e', 0, 'if True, the connection pool will log all checkouts/checkins to the logging stream, which defaults to sys.stdout.'],\
						('commit',0, int): [0, 'c', 0, 'commit db transaction'],\
						('debug', 0, int):[0, 'b', 0, 'toggle debug mode'],\
						('report', 0, int):[0, 'r', 0, 'toggle report, more verbose stdout/stderr.']}
	def __init__(self, **keywords):
		"""
		2008-10-06
			add option 'pool_recycle' to recycle connection. MySQL typically close connections after 8 hours.
			__metadata__.bind = create_engine(self._url, pool_recycle=self.pool_recycle)
		2008-07-09
		"""
		from pymodule import ProcessOptions
		ProcessOptions.process_function_arguments(keywords, self.option_default_dict, error_doc=self.__doc__, \
												class_to_have_attr=self)
		
		if self.echo_pool:	#2010-9-19 passing echo_pool to create_engine() causes error. all pool log disappeared.
			#2010-9-19 Set up a specific logger with our desired output level
			import logging
			#import logging.handlers
			logging.basicConfig()
			#LOG_FILENAME = '/tmp/sqlalchemy_pool_log.out'
			my_logger = logging.getLogger('sqlalchemy.pool')
	
			# Add the log message handler to the logger
			#handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1000000, backupCount=5)
			# create formatter
			#formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
			# add formatter to handler
			#handler.setFormatter(formatter)
			#my_logger.addHandler(handler)
			my_logger.setLevel(logging.DEBUG)
		if getattr(self, 'schema', None):	#for postgres
			for entity in entities:
				if entity.__module__==self.__module__:	#entity in the same module
					using_table_options_handler(entity, schema=self.schema)
		
		#2008-10-05 MySQL typically close connections after 8 hours resulting in a "MySQL server has gone away" error.
		__metadata__.bind = create_engine(self._url, pool_recycle=self.pool_recycle, echo=self.sql_echo)
		
		self.metadata = __metadata__
		self.session = __session__
	
	def setup(self, create_tables=True):
		"""
		2008-09-07
			expose option create_tables, default=True. assign it to False if no new table is to be created.
		"""
		setup_all(create_tables=create_tables)	#create_tables=True causes setup_all to call elixir.create_all(), which in turn calls metadata.create_all()
		#2008-08-26 setup_all() would setup other databases as well if they also appear in the program. Seperate this to be envoked after initialization
		# to ensure the metadata of other databases is setup properly.

if __name__ == '__main__':
	from pymodule import ProcessOptions
	main_class = AutismDB
	po = ProcessOptions(sys.argv, main_class.option_default_dict, error_doc=main_class.__doc__)
	instance = main_class(**po.long_option2value)
	instance.setup()
	import pdb
	pdb.set_trace()