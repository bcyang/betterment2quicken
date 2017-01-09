# betterment2quicken
convert Betterment .csv file to Quicken-importable .ofx

## Usage
```
# set up
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt

# run it
python betterment2quicken.py <transaction.csv>
```

## UI
To make this 10x useful, it would need a UI of some sort. Let's see if we can use the free tier of GAE to
host this. If not, Chrome App would be a good choice, too. (especially for the paranoid)


## Related Work
OK, everyone starts with Googling what they want.
Not surprising, I did find [ofxstatement](https://github.com/kedder/ofxstatement)
and [ofxstatement-betterment plugin](https://github.com/cmayes/ofxstatement-betterment).

Well, it didn't work. (Otherwise I wouldn't be creating this repo)

[upwork-qfx](https://github.com/joshuadwire/upwork-qfx) was the first one that I spotted where I can generate
an OFX that Quicken likes. By line-by-line comparison, it proved my suspicion that Quicken doesn't like some
perfectly-conforming OFX for some reason. It's the `<INTU.BID>` element!  You can either download
a Web Connect statement from some banks to obtain the number, or just do more Googling.
