import csv
import sys

import pytz
from dateutil import parser as dtparser
from docopt import docopt

USAGE = '''Usage:
    betterment2quicken.py <transactions.csv>
'''

EXPECTED_HEADERS = ['Goal Name', 'Account Name', 'Transaction Description',
                    'Amount', 'Ending Balance',
                    'Date Created', 'Date Completed']

STATEMENT_TEMPLATE = '''
<!--
OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:UTF-8
CHARSET:NONE
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE
-->

<OFX>
    <SIGNONMSGSRSV1>
        <SONRS>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            <DTSERVER>{last_record_dt}</DTSERVER>
            <LANGUAGE>ENG</LANGUAGE>
            <INTU.BID>10898</INTU.BID>
        </SONRS>
    </SIGNONMSGSRSV1>
    <BANKMSGSRSV1>
        <STMTTRNRS>
            <TRNUID>0</TRNUID>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            <STMTRS>
                <BANKACCTFROM>
                    <BANKID>Betterment</BANKID>
                    <ACCTID>{account_id}</ACCTID>
                    <ACCTTYPE>CHECKING</ACCTTYPE>
                </BANKACCTFROM>
                <BANKTRANLIST>
                    <DTSTART>{first_record_dt}</DTSTART>
                    <DTEND>{last_record_dt}</DTEND>
                    {records}
                </BANKTRANLIST>
                <LEDGERBAL>
                    <BALAMT>{ending_balance}</BALAMT>
                    <DTASOF>{last_record_dt}</DTASOF>
                </LEDGERBAL>
            </STMTRS>
        </STMTTRNRS>
    </BANKMSGSRSV1>
</OFX>
'''

RECORD_TEMPLATE = '''
                    <STMTTRN>
                        <TRNTYPE>{type}</TRNTYPE>
                        <DTPOSTED>{date_created}</DTPOSTED>
                        <DTAVAIL>{date_completed}</DTAVAIL>
                        <TRNAMT>{amount}</TRNAMT>
                        <FITID>{id}</FITID>
                        <MEMO>{transaction_description}</MEMO>
                    </STMTTRN>'''


class OFX(object):
    def __init__(self, filename):
        with(open(opts['<transactions.csv>'])) as csvfile:
            reader = csv.reader(csvfile)
            self.headers = reader.next()
            self.rows = list(reader)

        # the key we will use to construct dict for format()
        # we convert the CVS headers into keys so we don't have to think / re-invent
        # another set of keys
        self.keys = [o.replace(' ', '_').lower() for o in self.headers]

    @staticmethod
    def datetime_str(str):
        # per OFX Spec, this should be UTC, YYYYMMDDHHMMSS is good enough
        return dtparser.parse(str).astimezone(pytz.utc).strftime('%Y%m%d%H%M%S')

    def render_ofx(self):
        records = []
        rendered_dts = set()
        ending_balance = None
        account_id = None

        for row in self.rows:
            ctx = dict(zip(self.keys, row))
            # they are supposedly to be the same
            if account_id is None:
                account_id = ctx['goal_name']

            # the records comes ordered by date_created or date_complete, descending
            if ending_balance is None:
                ending_balance = ctx['ending_balance']

            # use DEP (Deposit) for deposits
            # use ? for Withdraw (I haven't needed to do it yet), not sure what the description looks like
            # use XFER (Transfer) for anything else (e.g. Market Changes)
            ctx['type'] = 'DEP' if 'Deposit' in ctx['transaction_description'] else 'XFER'

            # convert datetime to OFX datetime format
            for datekey in ['date_created', 'date_completed']:
                ctx[datekey] = self.datetime_str(ctx[datekey])
                # we will use these timestamps later
                rendered_dts.add(ctx[datekey])

            # construct a pseudo-unique transaction id. Quicken use this to determine if
            # a record has been imported. (date, description, amount) should be achieving
            # the desired affect
            ctx['id'] = str(abs(hash((ctx['date_created'],
                                      ctx['transaction_description'],
                                      ctx['amount']))))

            # render the record
            records.append(RECORD_TEMPLATE.format(**ctx))

        return STATEMENT_TEMPLATE.format(**{
            'account_id': account_id,
            'ending_balance': ending_balance,
            'last_record_dt': max(rendered_dts),
            'first_record_dt': min(rendered_dts),
            'records': '\n'.join(records)
        })


if __name__ == '__main__':
    opts = docopt(USAGE)

    ofx = OFX(opts['<transactions.csv>'])
    if ofx.headers != EXPECTED_HEADERS:
        print "CSV file header mismatch, expecting: %s" % ','.join(EXPECTED_HEADERS)
        sys.exit(-1)

    print ofx.render_ofx()
