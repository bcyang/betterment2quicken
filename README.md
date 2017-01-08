# betterment2quicken
convert Betterment .csv file to Quicken-importable .ofx

## Related Work
OK, everyone starts with Googling what they want.
Not surprising, I did find [ofxstatement](https://github.com/kedder/ofxstatement)
and [ofxstatement-betterment plugin](https://github.com/cmayes/ofxstatement-betterment).

Well, it didn't work. (Otherwise I wouldn't be creating this repo)

## Usage
```
# set up
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt

# run it
python betterment2quicken.py <transaction.csv>
```

## Other

[upwork-qfx](https://github.com/joshuadwire/upwork-qfx) was the first one that I spotted where I can generate
an OFX that Quicken likes. As suspected, Quicken only _likes_ an OFX with <INTU.BID>. You can either download
a Web Connect statement from some banks to obtain the number, or just do more Googling.
