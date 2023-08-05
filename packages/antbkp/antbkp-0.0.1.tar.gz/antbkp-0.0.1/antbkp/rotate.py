#This file is part of Ant Backup. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import shutil
import os
import logging
import datetime


class Rotate():

    @staticmethod
    def run(vals, options):
        backdir = options.get('backdir')
        day_week = int(datetime.datetime.now().strftime("%w"))
        day_number = int(datetime.datetime.now().strftime("%d"))
        logfile = open(options.get('log'), 'a')

        def call_mv(src, dst):
            logger = logging.getLogger('rotate')
            logger.info('%s %s' % (src, dst))
            shutil.rmtree(dst)
            shutil.move(src, dst)

        def check_dir(directory, backdir):
            d = '%s/%s' % (backdir, directory)
            if not os.path.exists(d):
                logger = logging.getLogger('rotate')
                logger.info('Create directory: %s' % directory)
                os.makedirs(d)

        directories = ['backup', 'backup2', 'backup3', 'backup4', 'backup5', 'backup6', 
            'backup7', 'backup_w2', 'backup_w3', 'backup_w4', 'backup_m2', 'backup_m3', 
            'backup_m4', 'backup_m5', 'backup_m6', 'backup_m7', 'backup_m8', 'backup_m9', 'backup_m10', 
            'backup_m11', 'backup_m12']

        for directory in directories:
            check_dir(directory, backdir)

        os.system('gzip -f '+backdir+'/backup/*')

        if day_number == 1: # First day month
            call_mv(backdir+'/backup_m11', backdir+'/backup_m12')
            check_dir('backup_m11', backdir)
            call_mv(backdir+'/backup_m10', backdir+'/backup_m11')
            check_dir('backup_m0', backdir)
            call_mv(backdir+'/backup_m9', backdir+'/backup_m10')
            check_dir('backup_m9', backdir)
            call_mv(backdir+'/backup_m8', backdir+'/backup_m9')
            check_dir('backup_8', backdir)
            call_mv(backdir+'/backup_m7', backdir+'/backup_m8')
            check_dir('backup_m7', backdir)
            call_mv(backdir+'/backup_m6', backdir+'/backup_m7')
            check_dir('backup_m6', backdir)
            call_mv(backdir+'/backup_m5', backdir+'/backup_m6')
            check_dir('backup_m5', backdir)
            call_mv(backdir+'/backup_m4', backdir+'/backup_m5')
            check_dir('backup_m4', backdir)
            call_mv(backdir+'/backup_m3', backdir+'/backup_m4')
            check_dir('backup_m3', backdir)
            call_mv(backdir+'/backup_m2', backdir+'/backup_m3')
            check_dir('backup_m2', backdir)
            call_mv(backdir+'/backup_w4', backdir+'/backup_m2')
            check_dir('backup_w4', backdir) #create backup_m1 dir

        if day_week == 1: # first day week. Monday = 1
            call_mv(backdir+'/backup_w3', backdir+'/backup_w4')
            check_dir('backup_w3', backdir)
            call_mv(backdir+'/backup_w2', backdir+'/backup_w3')
            check_dir('backup_w2', backdir)
            call_mv(backdir+'/backup7', backdir+'/backup_w2')
            check_dir('backup7', backdir) #create backup_w1 dir

        call_mv(backdir+'/backup6', backdir+'/backup7')
        check_dir('backup6', backdir)
        call_mv(backdir+'/backup5', backdir+'/backup6')
        check_dir('backup5', backdir)
        call_mv(backdir+'/backup4', backdir+'/backup5')
        check_dir('backup4', backdir)
        call_mv(backdir+'/backup3', backdir+'/backup4')
        check_dir('backup3', backdir)
        call_mv(backdir+'/backup2', backdir+'/backup3')
        check_dir('backup2', backdir)
        call_mv(backdir+'/backup', backdir+'/backup2')
        check_dir('backup', backdir) #create backup dir
