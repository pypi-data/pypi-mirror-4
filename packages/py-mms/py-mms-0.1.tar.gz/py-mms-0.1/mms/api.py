# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil import parser
from jsonrpc import ServiceProxy, JSONRPCException
from jsonrpc.json import JSONDecodeException

import choices
from utils import GroupIterator


class MMSClientApiError(Exception):
    def __init__(self, code, name, message):
        self.code = code
        self.message = message
        self.name = name

    def __str__(self):
        return repr(self.message)


class MMSBlackListedEmail(object):
    def __init__(self, mms_client, data):
        self.mms_client = mms_client
        self.data = data

    def get_email(self):
        return self.data['email']
    email = property(get_email)

    def get_listed_from(self):
        listed_from = self.data['listed_from']
        if listed_from:
            listed_from = parser.parse(listed_from)

        return listed_from
    listed_from = property(get_listed_from)

    def get_listed_to(self):
        listed_to = self.data['listed_to']
        if listed_to:
            listed_to = parser.parse(listed_to)

        return listed_to
    listed_to = property(get_listed_to)

    def get_listed_count(self):
        listed_count = self.data['listed_count']

        return listed_count
    listed_count = property(get_listed_count)

    def get_reason(self):
        reason = self.data['reason']

        return reason
    reason = property(get_reason)

    def get_is_listed(self):
        is_listed = self.data['is_listed']

        return is_listed
    is_listed = property(get_is_listed)


class MMSRecipient(object):
    def __init__(self, mms_client, email_message, data):
        self.mms_client = mms_client
        self.email_message = email_message
        self.id = data['recipient_id']
        self.data = data

    def get_state(self):
        state = self.data.get('status')
        if not state:
            if not hasattr(self, 'recipient'):
                self.recipient = self.mms_client.get_recipient(
                    email_message_id=self.email_message.id,
                    recipient_id=self.id
                )
                state = self.recipient['status']

        return state
    state = property(get_state)

    def get_email(self):
        return self.data['email']
    email = property(get_email)

    @property
    def is_sent(self):
        if self.state in [choices.RECIPIENT_STATUS_SENT,
                          choices.RECIPIENT_STATUS_TRACKED]:
            return True
        else:
            return False


class MMSEmailMessage(object):
    def __init__(self, mms_client, email_message_id):
        self.mms_client = mms_client
        self.id = email_message_id

    def get_scheduled_to(self):
        req = self.mms_client.process_request(
            method='scheduledTo',
            email_message_id=self.id,
        )

        return req

    def set_scheduled_to(self, datetime_timestamp):
        req = self.mms_client.process_request(
            method='setScheduledTo',
            email_message_id=self.id,
            timestamp=datetime_timestamp.isoformat()
        )

        return req
    scheduled_to = property(get_scheduled_to, set_scheduled_to)

    def get_recipients(self, **kwargs):
        req = self.mms_client.process_request(
            method='recipients',
            email_message_id=self.id,
            **kwargs
        )

        recipients = []
        for r in req:
            recipient = MMSRecipient(
                mms_client=self.mms_client,
                email_message=self,
                data=r
            )
            recipients.append(recipient)

        return recipients

    def get_recipients_count(self, **kwargs):
        req = self.mms_client.process_request(
            method='recipientsCount',
            email_message_id=self.id,
            **kwargs
        )

        return req

    def add_recipients(self, recipient_list, chunk_size=None):
        if chunk_size is None:
            chunk_size = len(recipient_list)

        add_recipient_stats = {
            "unique_added": 0,
            "duplicities": 0,
            "invalid": 0,
        }
        for chunk in GroupIterator(recipient_list, chunk_size):
            req = self.mms_client.process_request(
                method='addRecipients',
                email_message_id=self.id,
                recipients=chunk
            )
            for k, v in req.iteritems():
                add_recipient_stats[k] += v

        return add_recipient_stats
    recipients = property(get_recipients, add_recipients)

    def get_status(self):
        req = self.mms_client.process_request(
            method='status',
            email_message_id=self.id
        )

        return req
    status = property(get_status)

    def dispatch(self):
        req = self.mms_client.process_request(
            method='setToBeDispatched',
            email_message_id=self.id
        )

        return req

    def suspend(self):
        req = self.mms_client.process_request(
            method='setSuspended',
            email_message_id=self.id
        )

        return req

    def delete(self):
        req = self.mms_client.process_request(
            method='delete',
            email_message_id=self.id
        )

        return req

    @property
    def is_done(self):
        if self.status == choices.EMAIL_MESSAGE_STATUS_DONE:
            return True
        else:
            return False


class MMSClient(object):
    """
    Mass Mailing Python Wrapper
    """
    def __init__(self, API_URL, API_ID, API_KEY):
        self.API_ID = API_ID
        self.API_KEY = API_KEY
        self.api = ServiceProxy(API_URL)

    def process_request(self, method, **kwargs):
        """
        API request calling utility
        """
        api_namespace = kwargs.pop("api_namespace", "mail")
        api_namespace_handler = getattr(self.api, api_namespace)

        try:
            req = getattr(api_namespace_handler, method)(
                api_id=self.API_ID,
                api_key=self.API_KEY,
                **kwargs
            )
        except JSONRPCException, e:
            raise MMSClientApiError(
                code=e.error.get('code'),
                name=e.error.get('name'),
                message=e.error.get('message'),
            )
        except JSONDecodeException:
            raise MMSClientApiError(
                code=500,
                name='Invalid JSON response',
                message='Server returned non-standard response.',
            )
        else:
            return req

    def create_email_message(self, **kwargs):
        scheduled_to = kwargs.pop('scheduled_to', None)
        if isinstance(scheduled_to, datetime):
            scheduled_to = scheduled_to.isoformat()

        req = self.process_request(
            method='create',
            scheduled_to=scheduled_to,
            **kwargs
        )

        email_message_id = req
        email_message = self.get_email_message(email_message_id)
        return email_message

    def create_and_send_email_message(self, **kwargs):
        scheduled_to = kwargs.pop('scheduled_to', None)
        if isinstance(scheduled_to, datetime):
            scheduled_to = scheduled_to.isoformat()

        req = self.process_request(
            method='createAndSend',
            scheduled_to=scheduled_to,
            **kwargs
        )

        email_message_id = req
        email_message = self.get_email_message(email_message_id)
        return email_message

    def get_email_message(self, email_message_id):
        return MMSEmailMessage(
            mms_client=self,
            email_message_id=email_message_id
        )

    def test_spam(self, **kwargs):
        req = self.process_request(
            method='testSpamDry',
            **kwargs
        )

        return req

    def get_recipient(self, email_message_id, recipient_id):
        req = self.process_request(
            method='recipientDetail',
            email_message_id=email_message_id,
            recipient_id=recipient_id
        )

        return req

    def ses_verify_email(self, email):
        req = self.process_request(
            method="verifyEmailAddress",
            api_namespace="SESsender",
            email=email
        )

        return req

    def ses_get_email_verification_status(self, email):
        req = self.process_request(
            method="getEmailAddressVerificationStatus",
            api_namespace="SESsender",
            email=email
        )

        return req

    def filter_blacklisted(self, emails, chunk_size=None):
        if chunk_size is None:
            chunk_size = len(emails)

        blacklisted_emails = []
        for chunk in GroupIterator(emails, chunk_size):
            req = self.process_request(
                api_namespace='blacklist',
                method='list',
                emails=chunk,
            )

            for r in req:
                be = MMSBlackListedEmail(
                    mms_client=self,
                    data=r
                )
                blacklisted_emails.append(be)

        return blacklisted_emails
