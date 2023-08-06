# btc

Buy, sell, and transfer [bitcoin](http://bitcoin.org/en/) instantly in your
terminal!  (Powered by [Coinbase](https://coinbase.com/).)


## Why Coinbase?

[Coinbase](https://coinbase.com/) is a great bitcoin exchange because:

- They allow you to immediately add and verify a US bank account (this allows
  you to easily purchase and sell bitcoin without the hassle that other
  providers make you go through).
- They have a clean, simple website that makes using bitcoin a nice experience.
- They are backed by an incredible team of investors (see:
  https://coinbase.com/about).

**NOTE**: I am in no way affiliated with Coinbase.  I don't know anyone that
works there, have no relationship with the investing companies -- nothing.


## Why btc?

I spend a lot of my time at the terminal, and I greatly prefer using the command
line to buy, sell, and transfer bitcoin as it's a lot quicker than opening web
pages, navigating around, etc.

Using [Coinbase's API](https://coinbase.com/api/doc) was a logical next step for
me, as I could do everything I'd normally do through coinbase through a simple
CLI tool, `btc`.

Why should you use `btc`?  You should use `btc` if:

- You frequently buy / sell / transfer bitcoin.
- You use Coinbase.
- You prefer to use open source software to ensure your bitcoin are safe (anyone
  can view this project code).


## Prerequisites

Before using `btc`, there are a few things you should already have setup.

1. You should be familiar with bitcoin...  *Duh!*
2. You should have a coinbase account.  If you don't, you can create one here:
   https://coinbase.com/
3. You should add a valid US bank account to your coinbase account if you plan
   on purchasing or selling bitcoin.  If you only plan on using `btc` to
   transfer bitcoin from one account to another, this is not necessary.
4. You should create a coinbase API key.  This is what you will need below so
   that the `btc` program knows how to access your account.  You can do this
   here: https://coinbase.com/account/integrations


## Installation

You can install `btc` via [pip](http://pip.readthedocs.org/en/latest/):

```bash
$ sudo pip install btc
```

Once `btc` has been installed, you'll need to give it your coinbase API key so
it knows how to make requests.  You can find your coinbase API key here:
https://coinbase.com/account/integrations (make sure your API key is
*enabled*).

```bash
$ btc init
```

The `init` command will ask you for input, and walk you through the making sure
that `btc` is working properly.  Your API key will be stored in a file named
`~/.btc` in your home directory.  To remove your API key from `btc`, simply
delete that file.


## Usage

If you simply run `btc` on the command line, you'll get a list of help.

```bash
$ btc init      # activate btc by supplying your coinbase API key
$ btc address   # list your active bitcoin address for receiving money
$ btc balance   # list your account balance
$ btc request <btc> <email> [<note>]
                # send a payment request to the specified email address
$ btc send <btc> (<email> | <address>) [<note>]
                # send bitcoin to a person by email address or bitcoin address
$ btc test      # test your API key
$ btc logs      # display a list of recent transaction logs
$ btc rates     # show current exchange rates
$ btc buy 1.5   # purchase 1.5 bitcoin using your bank account on file
$ btc sell 1.5  # sell 1.5 bitcoin
$ btc -h        # display help information
```

All commands that have side effects will prompt you for confirmation before
doing anything for added security (so you don't accidentally spend tons of
money, or something).


## Changelog

v0.3: 04-18-2013

    - Setting ~/.btc to mode 0600 for additional security.

v0.2: 04-17-2013

    - Fixing some small documentation issues.

v0.1: 04-17-2013

    - First release!


## Like This?

If you've enjoyed using `btc`, feel free to send me some bitcoin!  My address
is:

**14m3gaa3TvEgN7Ltc4377v3MVCPnyunuqS**

<3

-Randall
