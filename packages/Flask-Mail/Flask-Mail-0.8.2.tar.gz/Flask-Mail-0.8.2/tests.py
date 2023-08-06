# -*- coding: utf-8 -*-

from __future__ import with_statement

import base64
import email
import unittest
import time
import re

from flask import Flask
from flask_mail import Mail, Message, BadHeaderError


class TestCase(unittest.TestCase):

    TESTING = True
    MAIL_DEFAULT_SENDER = "support@mysite.com"

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object(self)
        self.assertTrue(self.app.testing)
        self.mail = Mail(self.app)
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def assertIn(self, member, container, msg=None):
        if hasattr(unittest.TestCase, 'assertIn'):
            return unittest.TestCase.assertIn(self, member, container, msg)
        return self.assertTrue(member in container)

    def assertNotIn(self, member, container, msg=None):
        if hasattr(unittest.TestCase, 'assertNotIn'):
            return unittest.TestCase.assertNotIn(self, member, container, msg)
        return self.assertFalse(member in container)

    def assertIsNone(self, obj, msg=None):
        if hasattr(unittest.TestCase, 'assertIsNone'):
            return unittest.TestCase.assertIsNone(self, obj, msg)
        return self.assertTrue(obj is None)

    def assertIsNotNone(self, obj, msg=None):
        if hasattr(unittest.TestCase, 'assertIsNotNone'):
            return unittest.TestCase.assertIsNotNone(self, obj, msg)
        return self.assertTrue(obj is not None)


class TestMessage(TestCase):

    def test_initialize(self):
        msg = Message(subject="subject",
                      recipients=["to@example.com"])
        self.assertEqual(msg.sender, None)
        self.assertEqual(msg.recipients, ["to@example.com"])

    def test_recipients_properly_initialized(self):
        msg = Message(subject="subject")
        self.assertEqual(msg.recipients, [])
        msg2 = Message(subject="subject")
        msg2.add_recipient("somebody@here.com")
        self.assertEqual(len(msg2.recipients), 1)

    def test_sendto_properly_set(self):
        msg = Message(subject="subject", recipients=["somebody@here.com"],
                      cc=["cc@example.com"], bcc=["bcc@example.com"])
        self.assertEqual(len(msg.send_to), 3)
        msg.add_recipient("cc@example.com")
        self.assertEqual(len(msg.send_to), 3)

    def test_add_recipient(self):
        msg = Message("testing")
        msg.add_recipient("to@example.com")
        self.assertEqual(msg.recipients, ["to@example.com"])

    def test_sender_as_tuple(self):
        msg = Message(subject="testing",
                      sender=("tester", "tester@example.com"))
        self.assertEqual('tester <tester@example.com>', msg.sender)

    def test_reply_to(self):
        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      sender="spammer <spammer@example.com>",
                      reply_to="somebody <somebody@example.com>",
                      body="testing")
        response = msg.as_string()
        self.assertIn("Reply-To: somebody <somebody@example.com>", str(response))

    def test_send_without_sender(self):
        self.app.extensions['mail'].default_sender = None
        msg = Message(subject="testing", recipients=["to@example.com"], body="testing")
        self.assertRaises(AssertionError, self.mail.send, msg)

    def test_send_without_recipients(self):
        msg = Message(subject="testing",
                      recipients=[],
                      body="testing")
        self.assertRaises(AssertionError, self.mail.send, msg)

    def test_bcc(self):
        msg = Message(sender="from@example.com",
                      subject="testing",
                      recipients=["to@example.com"],
                      body="testing",
                      bcc=["tosomeoneelse@example.com"])
        response = msg.as_string()
        self.assertNotIn("tosomeoneelse@example.com", str(response))

    def test_cc(self):
        msg = Message(sender="from@example.com",
                      subject="testing",
                      recipients=["to@example.com"],
                      body="testing",
                      cc=["tosomeoneelse@example.com"])
        response = msg.as_string()
        self.assertIn("Cc: tosomeoneelse@example.com", str(response))

    def test_attach(self):
        msg = Message(subject="testing",
                      recipients=["to@example.com"],
                      body="testing")
        msg.attach(data="this is a test",
                   content_type="text/plain")
        a = msg.attachments[0]
        self.assertIsNone(a.filename)
        self.assertEqual(a.disposition, 'attachment')
        self.assertEqual(a.content_type, "text/plain")
        self.assertEqual(a.data, "this is a test")

    def test_bad_header_subject(self):
        msg = Message(subject="testing\n\r",
                      sender="from@example.com",
                      body="testing",
                      recipients=["to@example.com"])
        self.assertRaises(BadHeaderError, self.mail.send, msg)

    def test_bad_header_sender(self):
        msg = Message(subject="testing",
                      sender="from@example.com\n\r",
                      recipients=["to@example.com"],
                      body="testing")

        self.assertIn('From: from@example.com', msg.as_string())

    def test_bad_header_reply_to(self):
        msg = Message(subject="testing",
                      sender="from@example.com",
                      reply_to="evil@example.com\n\r",
                      recipients=["to@example.com"],
                      body="testing")

        self.assertIn('From: from@example.com', msg.as_string())
        self.assertIn('To: to@example.com', msg.as_string())
        self.assertIn('Reply-To: evil@example.com', msg.as_string())

    def test_bad_header_recipient(self):
        msg = Message(subject="testing",
                      sender="from@example.com",
                      recipients=[
                          "to@example.com",
                          "to\r\n@example.com"],
                      body="testing")

        self.assertIn('To: to@example.com\n', msg.as_string())

    def test_emails_are_sanitized(self):
        msg = Message(subject="testing",
                      sender="sender\r\n@example.com",
                      reply_to="reply_to\r\n@example.com",
                      recipients=["recipient\r\n@example.com"])
        self.assertIn('sender@example.com', msg.as_string())
        self.assertIn('reply_to@example.com', msg.as_string())
        self.assertIn('recipient@example.com', msg.as_string())

    def test_plain_message(self):
        plain_text = "Hello Joe,\nHow are you?"
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["to@example.com"],
                      body=plain_text)
        self.assertEqual(plain_text, msg.body)
        self.assertIn('Content-Type: text/plain', msg.as_string())

    def test_message_str(self):
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["to@example.com"],
                      body="some plain text")
        self.assertEqual(msg.as_string(), str(msg))

    def test_plain_message_with_attachments(self):
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["to@example.com"],
                      body="hello")

        msg.attach(data="this is a test",
                   content_type="text/plain")

        self.assertIn('Content-Type: multipart/mixed', msg.as_string())

    def test_html_message(self):
        html_text = "<p>Hello World</p>"
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["to@example.com"],
                      html=html_text)

        self.assertEqual(html_text, msg.html)
        self.assertIn('Content-Type: multipart/alternative', msg.as_string())

    def test_html_message_with_attachments(self):
        html_text = "<p>Hello World</p>"
        plain_text = 'Hello World'
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["to@example.com"],
                      body=plain_text,
                      html=html_text)
        msg.attach(data="this is a test",
                   content_type="text/plain")

        self.assertEqual(html_text, msg.html)
        self.assertIn('Content-Type: multipart/alternative', msg.as_string())

        parsed = email.message_from_string(msg.as_string())
        self.assertEqual(len(parsed.get_payload()), 2)

        body, attachment = parsed.get_payload()
        self.assertEqual(len(body.get_payload()), 2)

        plain, html = body.get_payload()
        self.assertEqual(plain.get_payload(), plain_text)
        self.assertEqual(html.get_payload(), html_text)
        self.assertEqual(base64.b64decode(attachment.get_payload()), 'this is a test')

    def test_date_header(self):
        before = time.time()
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["to@example.com"],
                      body="hello",
                      date=time.time())
        after = time.time()

        self.assertTrue(before <= msg.date <= after)
        dateFormatted = email.utils.formatdate(msg.date, localtime=True)
        self.assertIn('Date: ' + dateFormatted, msg.as_string())

    def test_msgid_header(self):
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["to@example.com"],
                      body="hello")

        # see RFC 5322 section 3.6.4. for the exact format specification
        r = re.compile(r"<\S+@\S+>").match(msg.msgId)
        self.assertIsNotNone(r)
        self.assertIn('Message-ID: ' + msg.msgId, msg.as_string())

    def test_unicode_sender_tuple(self):
        msg = Message(subject="subject",
                      sender=(u"ÄÜÖ → ✓", 'from@example.com>'),
                      recipients=["to@example.com"])

        self.assertIn('From: =?utf-8?b?w4TDnMOWIOKGkiDinJM=?= <from@example.com>', msg.as_string())

    def test_unicode_sender(self):
        msg = Message(subject="subject",
                      sender=u'ÄÜÖ → ✓ <from@example.com>>',
                      recipients=["to@example.com"])

        self.assertIn('From: =?utf-8?b?w4TDnMOWIOKGkiDinJM=?= <from@example.com>', msg.as_string())

    def test_unicode_headers(self):
        msg = Message(subject="subject",
                      sender=u'ÄÜÖ → ✓ <from@example.com>',
                      recipients=[u"Ä <t1@example.com>", u"Ü <t2@example.com>"],
                      cc=[u"Ö <cc@example.com>"])

        self.assertIn('From: =?utf-8?b?w4TDnMOWIOKGkiDinJM=?= <from@example.com>', msg.as_string())
        self.assertIn('To: =?utf-8?b?w4Q=?= <t1@example.com>, =?utf-8?b?w5w=?= <t2@example.com>', msg.as_string())
        self.assertIn('Cc: =?utf-8?b?w5Y=?= <cc@example.com>', msg.as_string())

    def test_extra_headers(self):
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["to@example.com"],
                      body="hello",
                      extra_headers={'X-Extra-Header': 'Yes'})
        self.assertIn('X-Extra-Header: Yes', msg.as_string())

    def test_message_charset(self):
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["foo@bar.com"],
                      charset='us-ascii')

        # ascii body
        msg.body = "normal ascii text"
        self.assertIn('Content-Type: text/plain; charset="us-ascii"', msg.as_string())

        # ascii html
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["foo@bar.com"],
                      charset='us-ascii')
        msg.body = None
        msg.html = "<html><h1>hello</h1></html>"
        self.assertIn('Content-Type: text/html; charset="us-ascii"', msg.as_string())

        # unicode body
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["foo@bar.com"])
        msg.body = u"ünicöde ←→ ✓"
        self.assertIn('Content-Type: text/plain; charset="utf-8"', msg.as_string())

        # unicode body and unicode html
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["foo@bar.com"])
        msg.html = u"ünicöde ←→ ✓"
        self.assertIn('Content-Type: text/plain; charset="utf-8"', msg.as_string())
        self.assertIn('Content-Type: text/html; charset="utf-8"', msg.as_string())

        # unicode body and attachments
        msg = Message(sender="from@example.com",
                      subject="subject",
                      recipients=["foo@bar.com"])
        msg.html = None
        msg.attach(data="foobar", content_type='text/csv')
        self.assertIn('Content-Type: text/plain; charset="utf-8"', msg.as_string())


class TestMail(TestCase):

    def test_send(self):

        with self.mail.record_messages() as outbox:
            msg = Message(subject="testing",
                          recipients=["tester@example.com"],
                          body="test")
            self.mail.send(msg)
            self.assertIsNotNone(msg.date)
            self.assertEqual(len(outbox), 1)

    def test_send_message(self):

        with self.mail.record_messages() as outbox:
            self.mail.send_message(subject="testing",
                                   recipients=["tester@example.com"],
                                   body="test")
            self.assertEqual(len(outbox), 1)
            msg = outbox[0]
            self.assertEqual(msg.subject, "testing")
            self.assertEqual(msg.recipients, ["tester@example.com"])
            self.assertEqual(msg.body, "test")


class TestConnection(TestCase):

    def test_send_message(self):
        with self.mail.record_messages() as outbox:
            with self.mail.connect() as conn:
                conn.send_message(subject="testing",
                                  recipients=["to@example.com"],
                                  body="testing")
            self.assertEqual(len(outbox), 1)

    def test_send_single(self):
        with self.mail.record_messages() as outbox:
            with self.mail.connect() as conn:
                msg = Message(subject="testing",
                              recipients=["to@example.com"],
                              body="testing")
                conn.send(msg)
            self.assertEqual(len(outbox), 1)

    def test_send_many(self):
        with self.mail.record_messages() as outbox:
            with self.mail.connect() as conn:
                for i in xrange(100):
                    msg = Message(subject="testing",
                                  recipients=["to@example.com"],
                                  body="testing")
                    conn.send(msg)
            self.assertEqual(len(outbox), 100)
