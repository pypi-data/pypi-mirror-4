#This file is part of Ant Backup. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import subprocess
import logging


class Mysql():

    @staticmethod
    def run(vals, options):
        host = vals.get('host', 'localhost')
        port = vals.get('port', '3306')
        user = vals.get('user', 'root')
        password = vals.get('password')
        backdir = options.get('backdir')
        logfile = open(options.get('log'), 'a')

        logger = logging.getLogger('mysql')

        for database in vals.get('dbs').split(','):
            logger.info('Database: %s' % database)

            process = subprocess.Popen("""
                mysqldump --opt --password=%s --user=%s %s > %s/backup/mysql_%s.sql
                """ % (password, user, database, backdir, database), 
                shell=True, stdout=logfile, stderr=logfile)
            process.wait()
