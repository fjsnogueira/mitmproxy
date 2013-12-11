import argparse
from libmproxy import cmdline
import tutils
import os.path


def test_parse_replace_hook():
    x = cmdline.parse_replace_hook("/foo/bar/voing")
    assert x == ("foo", "bar", "voing")

    x = cmdline.parse_replace_hook("/foo/bar/vo/ing/")
    assert x == ("foo", "bar", "vo/ing/")

    x = cmdline.parse_replace_hook("/bar/voing")
    assert x == (".*", "bar", "voing")

    tutils.raises(
        cmdline.ParseException,
        cmdline.parse_replace_hook,
        "/foo"
    )
    tutils.raises(
        "replacement regex",
        cmdline.parse_replace_hook,
        "patt/[/rep"
    )
    tutils.raises(
        "filter pattern",
        cmdline.parse_replace_hook,
        "/~/foo/rep"
    )
    tutils.raises(
        "empty clause",
        cmdline.parse_replace_hook,
        "//"
    )


def test_parse_setheaders():
    x = cmdline.parse_setheader("/foo/bar/voing")
    assert x == ("foo", "bar", "voing")

def test_shlex():
    """
    shlex.split assumes posix=True by default, we do manual detection for windows.
    Test whether script paths are parsed correctly
    """
    absfilepath = os.path.normcase(os.path.abspath(__file__))

    parser = argparse.ArgumentParser()
    cmdline.common_options(parser)
    opts = parser.parse_args(args=["-s",absfilepath])
    
    assert os.path.isfile(opts.scripts[0][0])

def test_common():
    parser = argparse.ArgumentParser()
    cmdline.common_options(parser)
    opts = parser.parse_args(args=[])

    assert cmdline.get_common_options(opts)

    opts.stickycookie_filt = "foo"
    opts.stickyauth_filt = "foo"
    v = cmdline.get_common_options(opts)
    assert v["stickycookie"] == "foo"
    assert v["stickyauth"] == "foo"

    opts.setheader = ["/foo/bar/voing"]
    v = cmdline.get_common_options(opts)
    assert v["setheaders"] == [("foo", "bar", "voing")]

    opts.setheader = ["//"]
    tutils.raises(
        "empty clause",
        cmdline.get_common_options,
        opts
    )
    opts.setheader = []

    opts.replace = ["/foo/bar/voing"]
    v = cmdline.get_common_options(opts)
    assert v["replacements"] == [("foo", "bar", "voing")]

    opts.replace = ["//"]
    tutils.raises(
        "empty clause",
        cmdline.get_common_options,
        opts
    )

    opts.replace = []
    opts.replace_file = [("/foo/bar/nonexistent")]
    tutils.raises(
        "could not read replace file",
        cmdline.get_common_options,
        opts
    )

    opts.replace_file = [("/~/bar/nonexistent")]
    tutils.raises(
        "filter pattern",
        cmdline.get_common_options,
        opts
    )

    p = tutils.test_data.path("data/replace")
    opts.replace_file = [("/foo/bar/%s"%p)]
    v = cmdline.get_common_options(opts)["replacements"]
    assert len(v) == 1
    assert v[0][2].strip() == "replacecontents"
