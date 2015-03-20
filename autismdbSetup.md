# Introduction #

  * create the database

```
    createdb autismdb
```

  * add pgsql language to the db

```
    postgres@autism:~$ createlang plpgsql autismdb
```

  * use elixirdb ORM to pop up the skeleton.

```
    yh@thinkpad:~/script/autismgenetics$ ./src/AutismDB.py  -v postgresql -u yh -z localhost -d autismdb -k public
```


  * install triggers for relevant tables

```
    schemaName=public;
    dbName=autismdb;
    for tbl in `~/script/pymodule/FindTablesWithLogColumns.py -d $dbName -u yh -k $schemaName `;
      do echo $tbl;
      ~/script/pymodule/OutputSQLTrigger.py -i $tbl | psql  $dbName -f -;
    done
```


  * grant all privileges on all tables/sequences to all users in **geschwindlab** group

```
    # in psql client
    create role autismTeam;
    grant autismTeam to user1;
    grant autismTeam to user2;
    grant autismTeam to user3;
```

```
    # in unix shell
    roleName=user;
    schemaName=public;
    dbName=autismdb;
    for tbl in `psql -qAt -c "select tablename from pg_tables where schemaname = '$schemaName';" $dbName`;
    do
      psql -c "grant all privileges on $tbl to $roleName" $dbName;
    done
    
    for tbl in `psql -qAt -c "select sequence_name from information_schema.sequences where sequence_schema = '$schemaName';" $dbName`;
    do
      psql -c "grant usage,update,select on $tbl to $roleName" $dbName ;
    done
```


  * add **data\_dir** variable into table readme

  * fill in table allele\_type

> data entries:
  1. missing
  1. reference
  1. substitution
  1. inversion
  1. deletion
  1. insertion
  1. translocation


Future incremental change to db (like adding some columns or changing column type) has to be carried out manually. Adding new table can be done through running `src/AutismDB.py` though.