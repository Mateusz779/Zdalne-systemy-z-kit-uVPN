#!/bin/sh

ifconfig > /tmp/ifconfig
cat /proc/cmdline > /tmp/cmdline
tar -cJf /tmp/zalacznik.tar /tmp/cmdline /tmp/ifconfig
xz -v /tmp/zalacznik.tar

MAILFILE=`mktemp /tmp/mailfile.XXXXXX`
BOUNDARY=`head -c 24 /dev/urandom |base64`
NOW=`date "+%Y-%m-%d %H:%M:%S"`

ATTACHEMENT=/tmp/attachement_`date +'%Y:%m:5d_%H%M%S'`.tar.xz
cat /tmp/zalacznik.tar.xz >$ATTACHEMENT

cat >$MAILFILE <<EOF
From: test@mkedziora.pl
To: admin@mkedziora.pl
Subject: Uruchomiono maszynę
Date: $NOW
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=$BOUNDARY

--$BOUNDARY
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: utf8
Content-Disposition: inline

Dzień dobry!

Uruchomiono maszynę o tokenie: $(sed 's/.*token=//;s/ .*//' /proc/cmdline)
w załączniku ip i konfiguracja kernela.

--$BOUNDARY
Content-Type: application/x-xz; name="report.tar.xz"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="report.tar.xz"

EOF
cat $ATTACHEMENT|base64 >>$MAILFILE
cat >>$MAILFILE <<EOF
--$BOUNDARY--
EOF

cat $MAILFILE |msmtp -C /etc/msmtprc -a notification admin@mkedziora.pl

rm -f $ATTACHEMENT $MAILFILE
