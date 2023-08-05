#This file is part of Ant Backup. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import subprocess
import logging


class Psql():

    @staticmethod
    def run(vals, options):
        host = vals.get('host','localhost')
        port = vals.get('port','5432')
        backdir = options.get('backdir')
        logfile = open(options.get('log'), 'a')

        logger = logging.getLogger('psql')

        for db in vals.get('dbs').split(','):
            conn = db.split(':')[0]
            database = db.split(':')[1]
            user = conn.split('@')[0]
            password = conn.split('@')[1]

            logger.info('Database: %s' % database)

            process = subprocess.Popen("""
                export PGPASSWORD=%s
                pg_dump %s -U %s > %s/backup/psql_%s.sql
                export PGPASSWORD=""" % (password, database, user, backdir, database), 
                shell=True, stdout=logfile, stderr=logfile)
            process.wait()
