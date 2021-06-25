# Bruty

[![Actions Status](https://github.com/lyz-code/bruty/workflows/Build/badge.svg)](https://github.com/lyz-code/bruty/actions)

Bruteforce dynamic web applications with Selenium.

## Installing

```bash
pip install bruty
```

It's assumed that you've got installed Chromium under `/usr/bin/chromium` and
that the
[chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
of the same version is found in your `PATH`.

## Usage

If you want to content from the https://fake.web website that is not found by
crawlers, you can create a list of uris in a file such as:

```
admin
wp-login
```

Then run:

```bash
bruty https://fake.web -f uris.txt
```

If you don't want to wait until the command ends to see the results use the `-v`
flag.

### Fake 404 pages

Some sites return a 200 status code for the 404, if it's your case, inspect the
code of one of them and create a regular expression to catch them, imagine it's
`404 error`.

To test that it works run `bruty` against two urls, one that exists and another
that returns the fake 404, making sure that only the existent one is printed.

```bash
bruty https://fake.web -u index.html -u fake_404.html -n '404 error'
```

Once you know it works, run it against all the uris:

```bash
bruty https://fake.web -f uris.txt -n '404 error'
```

### Untrusted return codes

Some websites use the 200 status code when they should use 404 or even 30X. Use
the `-i` flag to ignore the checking of the status code. It should be used with
the `-n` flag to tell the right urls from the wrong.

```bash
bruty https://fake.web -f uris.txt -i -n '404 error'
```

### Parallelization

Bruty doesn't yet support parallelization, so you'll have to do it manually,
split your uris file into the number of processes you want with `split` and
launch a `bruty` process for each of them.

## Contributing

For guidance on setting up a development environment, and how to make
a contribution to *bruty*, see [Contributing to
bruty](https://lyz-code.github.io/bruty/contributing).

## License

GPLv3
