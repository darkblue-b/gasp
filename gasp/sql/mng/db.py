"""
Database Information and Management
"""

from gasp.sql.c import psqlcon


"""
Databases Info
"""

def list_db(conParam):
    """
    List all PostgreSQL databases
    """
    
    con = psqlcon(conParam)
    
    cursor = con.cursor()
    
    cursor.execute("SELECT datname FROM pg_database")
    
    return [d[0] for d in cursor.fetchall()]


def db_exists(lnk, db):
    """
    Database exists
    """
    con = psqlcon(lnk)
        
    cursor = con.cursor()
    
    cursor.execute("SELECT datname FROM pg_database")
    
    dbs = [d[0] for d in cursor.fetchall()]
    
    return 1 if db in dbs else 0

"""
Dump Databases
"""

def dump_db(conPSQL, outSQL):
    """
    DB to SQL Script
    """
    
    from gasp import exec_cmd
    
    outcmd = exec_cmd("pg_dump -U {} -h {} -p {} -w {} > {}".format(
        conPSQL["USER"], conPSQL["HOST"], conPSQL["PORT"],
        conPSQL["DATABASE"], outSQL      
    ))
    
    return outSQL


"""
Copy data from one Database to another
"""

def copy_fromdb_todb(conFromDb, conToDb, tables, qForTbl=None, api='pandas'):
    """
    Send PGSQL Tables from one database to other
    """
    
    from gasp             import goToList
    
    api = 'pandas' if api != 'pandas' and api != 'psql' else api
    
    tables = goToList(tables)
    
    if api == 'pandas':
        from gasp.fm.sql import query_to_df
        from gasp.to.sql import df_to_db
    
        for table in tables:
            if not qForTbl:
                tblDf = query_to_df(conFromDb, "SELECT * FROM {}".format(
                    table), db_api='psql')
        
            else:
                if table not in qForTbl:
                    tblDf = query_to_df(conFromDb, "SELECT * FROM {}".format(
                        table), db_api='psql')
            
                else:
                    tblDf = query_to_df(conFromDb, qForTbl[table], db_api='psql')
        
            df_to_db(conToDb, tblDf, table, api='psql')
    
    else:
        import os
        from gasp.oss.ops     import create_folder, del_folder
        from gasp.sql.mng.tbl import dump_table
        from gasp.sql.mng.tbl import restore_table
        
        tmpFolder = create_folder(
            os.path.dirname(os.path.abspath(__file__)), randName=True
        )
        
        for table in tables:
            # Dump 
            sqlScript = dump_table(conFromDb, table, os.path.join(
                tmpFolder, table + ".sql"
            ))
            
            # Restore
            tblname = restore_table(conToDb, sqlScript, table)
        
        del_folder(tmpFolder)

