# py-mms (COEX MMS API Client)

The Python interface to MMS.

## Getting Started

    import mms
    mms_client = mms.api.MMSClient(API_URL, API_ID, API_KEY)
    email_message = mms_client.create_email_message(
        subject='Test e-mail',
        sender='john.doe@example.com',
        message_type=mms.choices.EMAIL_TRANSACTIONAL_EMAIL_MESSAGE_TYPE
    )

About us
--------

[COEX](http://www.coex-webdesign.com/) is small-sized company. We have been
creating custom webs and online applications since 2002. We communicate with
our clients in a way so that our solutions would be reasonable, provide
optimum service under the given circumstances and serve their purpose in
the long term.
