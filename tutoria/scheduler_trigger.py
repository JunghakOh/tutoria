# -*- coding: utf-8 -*-
"""
scheduler.py 

Created on Nov. 12, 2017
by Boxuan
"""
import argparse
import os
import sys
import random
from scheduler.models import Session
from django.utils import timezone
from dateutil import parser
from wallet.models import Transaction
from django.core.mail import send_mail

def begin_all_sessions(time):
    #print(time)

    # get all sessions start at specific time
    sessions = Session.objects.filter(start_time=time)
    
    for session in sessions:
        print("\nsession.id = ", session.id)
        records = session.bookingrecord_set.all()
        for record in records:
            if record.status == record.INCOMING:
                record.status = record.ONGOING
                record.save()
                print("set record (id: ", record.id, ") status from INCOMING to ONGOING")
        print("set session from ", session.status, " to ", session.CLOSED)
        session.status = session.CLOSED
        session.save()


def end_all_sessions(time):
    #print(time)

    # get all sessions end at specific time
    sessions = Session.objects.filter(end_time=time)

    for session in sessions:
        print("\nsession.id = ", session.id)
        records = session.bookingrecord_set.all()
        for record in records:
            if record.status == record.ONGOING:
                record.status = record.FINISHED
                record.save()
                print("set record (id: ", record.id, ") status from ONGOING to FINISHED")
                # only Private Tutor session has transaction
                if session.tutor.tutor_type == session.tutor.PRIVATE_TUTOR:
                    transaction = record.transaction
                    receiver = transaction.receiver
                    amount = transaction.amount
                    commission = transaction.commission

                    # tutor receives tuition fee
                    receiver.user.wallet_balance += amount
                    receiver.save()
                    
                    # send email to tutor about balance change
                    content = "Please check on Tutoria, your session " + str(session.id)
                    content += " has finished and your wallet balance has changed from "
                    content += str(receiver.user.wallet_balance - amount) + " to "
                    content += str(receiver.user.wallet_balance)
                    send_mail('Session Finished & Balance Change', content, 'noreply@hola-inc.top', [receiver.email], False)

                    # (todo) company receives commission

                    print("transaction id = ", transaction.id, "transfer tuition fee = ", amount, " to tutor = ", receiver)

                # send email to student (review reminder)
                content = "Please check on Tutoria, your session " + str(session.id)
                content += " has finished and you can give a comment to the tutor"
                send_mail('Session Finished, Please give your comment', content, 'noreply@hola-inc.top', [record.student.email], False)

def run(flag, time):
    # parse the time string to datetime format
    time = parser.parse(time)
    # make timezone aware
    time = timezone.make_aware(time, timezone.get_current_timezone())
    if (flag):
        begin_all_sessions(time)
    else:
        end_all_sessions(time)

def help():
    print("call run(flag, time) to start/end all sessions")
    print("=== example ===")
    print("run(True, \"Nov 17 2017 9:00AM\") means begin all sessions")

if __name__ == '__main__':
    run(True, "Nov 17 2017 9:00AM")
    ## create ArgumentParser() object
    #parser = argparse.ArgumentParser()
    ## add argument
    #parser.add_argument('--flag', required=True, help='True: begin_all_sessions; False: end_all_sessions')
    #parser.add_argument('--time', required=True, help='Type in a time')
    #
    ## parse argument
    #try:
    #    args = parser.parse_args()
    #except:
    #    parser.print_help()
    #    raise
    #run(args.flag, args.time)