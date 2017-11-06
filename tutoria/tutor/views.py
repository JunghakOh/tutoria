"""Views for the Tutor App."""
from __future__ import print_function
from django.shortcuts import (render, redirect)
from django.http import HttpResponse
from account.models import Tutor, Student, User
from scheduler.models import Session, BookingRecord
from django.contrib.auth.decorators import login_required
from datetime import datetime
from wallet.models import Transaction
from django.views import generic


class DetailView(generic.DetailView):
    """A class for the detailed view of tutor profile."""

    model = Tutor
    template_name = 'detail.html'
    context_object_name = 'tutor'

    def get_context_data(self, **kwargs):
        """Get context data."""
        # TODO: add doc string - Jingran
        context = super(DetailView, self).get_context_data(**kwargs)
        context['phone_visible'] = False
        if self.request.user.is_authenticated:
            visitor = User.objects.get(
                username=self.request.session['username'])
            # check if current visitor is the tutor itself
            if visitor == self.get_object().user:
                context['phone_visible'] = True
            # check if current visitor has booked this tutor's session
            for record in self.get_object().bookingrecord_set.all():
                if visitor == record.student.user:
                    context['phone_visible'] = True
        return context

# -----------------------------------------------------------------------------
# ####### Book Session #######


@login_required(login_url='/auth/login/')
def confirm_booking(request, tutor_id):
    """Confirm booking a new session."""
    if request.method == 'POST':
        user = User.objects.get(username=request.session['username'])
        student = Student.objects.get(user=user)
        tutor = Tutor.objects.get(pk=tutor_id)
        new_session = Session.objects.get(
            pk=request.POST.get('session_id', ''))
        # Ignore commission for now because it might be saved by coupon
        if (student.wallet_balance - tutor.hourly_rate) < 0:
            return HttpResponse("Your balance is " +
                                str(student.wallet_balance) +
                                ". You don't have enough money.")
        if (tutor.username == student.username):
            # TODO: beautify
            return HttpResponse("You can't book your session.")
        # Check if student has already booked a session on that day.
        hist_booking_list = student.bookingrecord_set.all()
        for hist_booking in hist_booking_list:
            if hist_booking.session.start_time.date() == \
                    new_session.start_time.date() and \
                    hist_booking.tutor == tutor:
                return HttpResponse("You can only book one session per day!")
        return render(request, 'book.html',
                      {'tutor': tutor,
                       'session': new_session,
                       'balance': student.wallet_balance - tutor.hourly_rate * 1.05,
                       'commission': tutor.hourly_rate * 0.05,
                       'total': tutor.hourly_rate * 1.05})


# TODO: handle coupons (wait until Construction phase)
@login_required(login_url='/auth/login/')
def save_booking(request, tutor_id):
    """Save booking record and redirect to the dashboard."""
    if request.method == 'POST':
        user = User.objects.get(username=request.session['username'])
        student = Student.objects.get(user=user)
        session_id = request.POST.get('session_id', '')
        tutor = Tutor.objects.get(pk=tutor_id)
        session = Session.objects.get(pk=session_id)
        # TODO: mark session as selected
        if not session.status == session.BOOKABLE:
            # TODO: handle exception
            # return
            pass
        # added following lines for testing.  - Jiayao
        session.tutor = tutor
        session.status = session.BOOKED
        session.save()

        now = datetime.now()
        # TODO: django add timezone to naive datetime  - Jiayao
        # Create a new transaction and save it.
        transaction = Transaction(issuer=student, receiver=tutor,
                                  amount=tutor.hourly_rate,
                                  created_at=now,
                                  commission=tutor.hourly_rate * 0.05)
        transaction.save()
        # Create a new booking record and save it.
        bookRecord = BookingRecord(
            tutor=tutor, student=student, session=session, entry_date=now,
            transaction=transaction)
        bookRecord.save()

        # Deduct fee (including commission) from student's wallet
        student.wallet_balance -= tutor.hourly_rate * 1.05
        return redirect("/dashboard/mybookings/")
    else:
        return HttpResponse("not a legal POST request!")

# -----------------------------------------------------------------------------
