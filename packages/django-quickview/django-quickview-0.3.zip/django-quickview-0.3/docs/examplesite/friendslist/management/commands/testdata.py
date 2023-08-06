# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from friendslist.models import *


class Command(BaseCommand):
    args = ''
    help = 'Creates a lot of test data.'

    def handle(self, *args, **options):

        self.stdout.write('Adding user ...');
        for username in ('thomas',):
            user = User.objects.create_user(username, '%s@example.org' % username, 'test')
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()

        friendslist = (
            'Thomas Weholt',
            'Guido VanRossum',
            'Jean Reno',
            'Linus Torvalds',
            'Jacob KRoss'
        )

        for friend in friendslist:
            firstname, lastname = friend.split(' ')
            Friend.objects.create(
                name = friend,
                email = '%s@%s.com' % (firstname,lastname),
                address = 'Hollywood Bld. 1911',
                city = 'Los Angeles',
                zip_code = '02-666',
                country = 'America',
                phone = '555 - 42 - 666'
            )


        self.stdout.write('Successfully created initial data.')
