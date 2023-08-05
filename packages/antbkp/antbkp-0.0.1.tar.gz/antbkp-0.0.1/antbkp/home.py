#This file is part of Ant Backup. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import subprocess
import logging


class Home():

    @staticmethod
    def run(vals, options):
        backdir = options.get('backdir')
        logfile = open(options.get('log'), 'a')

        logger = logging.getLogger('home')

        for home in vals.get('homes').split(','):
            logger.info('Directory: %s' % home)

            process = subprocess.Popen("""
                tar -cf %s/backup/%s.tar /home/%s/""" % (backdir, home, home), 
                shell=True, stdout=logfile, stderr=logfile)
            process.wait()
