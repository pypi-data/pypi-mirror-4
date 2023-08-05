###############################################################################
# Formic: An implementation of Apache Ant FileSet globs
# Copyright (C) 2012, Aviser LLP, Singapore.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

"""Tests on formic"""
#pylint: disable-all

from formic import get_version, MatchType, Matcher, ConstantMatcher, FNMatcher, \
    FormicError, Section, Pattern, PatternSet, FileSetState, FileSet
import pytest
import os

def match(matcher, original, expected):
    matched   = set()
    unmatched = set(original)
    matcher.match_files(matched, unmatched)
    assert set(expected) == matched
    assert unmatched == set(original) - matched

NOT_PRESENT = -1
MATCHED_INHERIT = 0
MATCHED_AND_SUBDIR = 1
MATCHED_NO_SUBDIR = 2
UNMATCHED = 3

def file_set_state_location(file_set_state, pattern, location):
    """A helper function that validates that the correct FileSetState
    contains the Pattern 'pattern'."""
    msg = ["MATCHED_INHERIT", "MATCHED_AND_SUBDIR", "MATCHED_NO_SUBDIR", "UNMATCHED"]
    locations = [ file_set_state.matched_inherit.patterns,
                  file_set_state.matched_and_subdir.patterns,
                  file_set_state.matched_no_subdir.patterns,
                  file_set_state.unmatched.patterns]
    found = [ pattern in patterns for patterns in locations ]
    count = len([b for b in found if b])
    if count == 0:
        if location == NOT_PRESENT:
            pass
        else:
            assert False, "{0} was not found anywhere in {1}".format(pattern, file_set_state)
    elif count > 1:
        assert False, "{0} was found in {1} locations in {2}".format(pattern, count, file_set_state)
    else:
        for i in range(0, 4):
            if found[i]:
                break
        if location == NOT_PRESENT:
            assert False, "{0} was in {1} but should have been NOT PRESENT for path {2}".\
                            format(pattern, msg[i], file_set_state.path_elements)

        else:
            if i != location:
                assert False, "{0} was in {1} but should have been in {2} for path {3}".\
                                format(pattern, msg[i], msg[location], file_set_state.path_elements)

def find_count(directory, pattern):
    """Platform-detecting way to count files matching a pattern"""
    if os.name == "posix":
        return find_count_posix(directory, pattern)
    elif os.name == "nt":
        return find_count_dos(directory, pattern)
    else:
        raise Exception("System is neither Posix not Windows")

def find_count_posix(directory, pattern):
    """Runs Unix find command on a directory counting how many files match
    the specified pattern"""
    if pattern is None:
        pattern = "*"
    import subprocess
    process = subprocess.Popen(["find", str(directory), "-type", "f", "-name", str(pattern)], stdout=subprocess.PIPE)
    lines = 0
    while True:
        line = process.stdout.readline()
        if line:
            lines += 1
        else:
            break
    print "find", directory, "-type f -name", pattern, ": found", lines, "files"
    return lines

def find_count_dos(directory, pattern):
    """Runs DOS dir /s command on a directory counting how many files match
    the specified pattern"""
    if pattern is None:
        pattern = "*.*"
    import subprocess
    process = subprocess.Popen(["dir", str(os.path.join(directory, pattern)), "/s", "/a-d", "/b"], stdout=subprocess.PIPE, shell=True)
    lines = 0
    while True:
        line = process.stdout.readline()
        if line:
            lines += 1
        else:
            break
    print "dir", str(os.path.join(directory, pattern)), "/s : found", lines, "files"
    return lines

def get_test_directory():
    """Return a platform-suitable directory for bulk-testing"""
    if os.name == "posix":
        return "/usr"
    elif os.name == "nt":
        return "C:\\WINDOWS"
    else:
        raise Exception("System is neither Posix not Windows")

def formic_count(directory, pattern):
    if pattern is None:
        pattern = "*"
    fs = FileSet(directory=directory, include="/**/" + pattern, default_excludes=False, symlinks=False)
    lines = sum(1 for file in fs.files())
    print "FileSet found", lines, "files"
    return lines

def compare_find_and_formic(directory, pattern=None):
    """Runs find and formic on the same directory with the same file pattern;
    both approaches should return the same number of files."""
    assert find_count(directory, pattern) == formic_count(directory, pattern)


class TestMatchers(object):
    def test_basic(self):
        assert Matcher("test") == Matcher("test")
        assert Matcher("a") != Matcher("b")

        # Test Constant matcher
        assert isinstance(Matcher.create("a"), ConstantMatcher)
        assert Matcher.create("a").match("a")
        assert not Matcher.create("a").match("b")
        assert Matcher.create("a") == Matcher.create("a")
        assert Matcher.create("test") == Matcher.create("test")

        # Test FNMatcher
        assert isinstance(Matcher.create("a*"), FNMatcher)
        assert Matcher.create("a*").match("abc")
        assert Matcher.create("a*").match("ape")
        assert not Matcher.create("a*").match("bbc")
        assert Matcher.create("a?").match("ab")
        assert not Matcher.create("a?").match("ba")


class TestSections(object):
    def test_basic(self):
        s = Section(['test'])
        assert s.str == "test"
        assert s.elements[0] == ConstantMatcher("test")

        s = Section(["test", "bin"])
        assert s.str == "test/bin"
        assert s.elements[0] == ConstantMatcher("test")
        assert s.elements[1] == ConstantMatcher("bin")

        s = Section(["????", "test", "bin"])
        assert s.str == "????/test/bin"
        assert s.elements[0] == FNMatcher("????")
        assert s.elements[1] == ConstantMatcher("test")
        assert s.elements[2] == ConstantMatcher("bin")

    def test_match_single_no_bindings(self):
        s = Section(['test'])
        path = []
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 1 ] == matches

        path = "not".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test/util/bin/test/last/test".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 1, 4, 6 ] == matches

        path = "not/util/bin/test/last/not".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 4 ] == matches

    def test_match_single_bound_start(self):
        s = Section(['test'])
        s.bound_start = True
        path = []
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 1 ] == matches

        path = "not".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test/util/bin/test/last/test".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 1 ] == matches

        path = "not/util/bin/test/last/not".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

    def test_match_single_bound_end(self):
        s = Section(['test'])
        s.bound_end = True
        path = []
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 1 ] == matches

        path = "not".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test/util/bin/test/last/test".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 6 ] == matches

        path = "not/util/bin/test/last/not".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

    def test_match_twin_elements_no_bindings(self):
        s = Section(['test', "a*"])
        path = []
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test/bin".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test/andrew".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 2 ] == matches

        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 2, 5, 7 ] == matches

        path = "not/util/bin/test/ast/not".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 5 ] == matches

    def test_match_twin_elements_bound_start(self):
        s = Section(['test', "a*"])
        s.bound_start = True
        path = []
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test/bin".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test/andrew".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 2 ] == matches

        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 2 ] == matches

        path = "not/util/bin/test/ast/not".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

    def test_match_twin_elements_bound_end(self):
        s = Section(['test', "a*"])
        s.bound_end = True
        path = []
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test/bin".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test/andrew".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 2 ] == matches

        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 7 ] == matches

        path = "not/util/bin/test/ast/not".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

    def test_single_match_not_beginning(self):
        s = Section(['test'])
        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [ index for index in s.match_iter(path, 2) ]
        assert [ 4, 6 ] == matches
        matches = [ index for index in s.match_iter(path, 3) ]
        assert [ 4, 6 ] == matches
        matches = [ index for index in s.match_iter(path, 4) ]
        assert [ 6 ] == matches
        matches = [ index for index in s.match_iter(path, 5) ]
        assert [ 6 ] == matches
        matches = [ index for index in s.match_iter(path, 6) ]
        assert [ ] == matches
        matches = [ index for index in s.match_iter(path, 7) ]
        assert [ ] == matches
        matches = [ index for index in s.match_iter(path, 8) ]
        assert [ ] == matches

    def test_multi_match_not_beginning(self):
        s = Section(['test', 'a*'])
        path = "test".split("/")
        matches = [ index for index in s.match_iter(path, 1) ]
        assert [ ] == matches

        path = "test/andrew".split("/")
        matches = [ index for index in s.match_iter(path, 1) ]
        assert [ ] == matches

        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [ index for index in s.match_iter(path, 2) ]
        assert [ 5, 7 ] == matches
        matches = [ index for index in s.match_iter(path, 3) ]
        assert [ 5, 7 ] == matches
        matches = [ index for index in s.match_iter(path, 4) ]
        assert [ 7 ] == matches
        matches = [ index for index in s.match_iter(path, 5) ]
        assert [ 7 ] == matches
        matches = [ index for index in s.match_iter(path, 6) ]
        assert [ ] == matches
        matches = [ index for index in s.match_iter(path, 7) ]
        assert [ ] == matches
        matches = [ index for index in s.match_iter(path, 8) ]
        assert [ ] == matches

    def test_match_bound_start(self):
        s = Section(['test', "a*"])
        s.bound_start = True
        path = "test".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ ] == matches

        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [ index for index in s.match_iter(path, 0) ]
        assert [ 2 ] == matches

        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [ index for index in s.match_iter(path, 1) ]
        assert [ ] == matches


class TestPattern(object):
    def test_illegal_glob(self):
        with pytest.raises(FormicError):
            Pattern("/test/../**")

    def test_glob_with_pointless_curdir(self):
        simple = ['**', 'test', 'test']
        assert simple ==  Pattern._simplify(['**', '.', 'test', 'test'])
        assert simple ==  Pattern._simplify(['**', 'test', '.', 'test'])
        assert simple ==  Pattern._simplify(['**', 'test', 'test', '.'])

        assert simple ==  Pattern._simplify(['**', '**', 'test', 'test'])
        assert simple ==  Pattern._simplify(['**', '**', '**', 'test', 'test'])

        simple = ['**', 'test', '**', 'test']
        assert simple ==  Pattern._simplify(['**', 'test', '**', '**', 'test'])

    def test_compilation_and_str(self):
        # Syntax for the dictionary:
        # The key is the normative string, and the value is a list of patterns that generate the normative
        patterns = {"/*.py":["/*.py"],
                    "/test/*.py":["/test/*.py"],
                    "/test/dir/**/*":["/test/dir/", "/test/dir/**", "/test/dir/**/*"],
                    "/start/**/test/*.py":["/start/**/test/*.py"],
                    "/start/**/test/**/*.py":["/start/**/test/**/*.py"],
                    "**/test/*.py":["test/*.py", "**/test/*.py"],
                    "**/test/*":["test/*", "**/test/*"],
                    "**/test/**/*":["test/**", "test/**/*", "**/test/**", "**/test/**/*"],
                    "**/test/**/*.py":["test/**/*.py", "**/test/**/*.py"],
                    "**/start/**/test/**/*.py":["start/**/test/**/*.py", "**/start/**/test/**/*.py"],
                    }
        for normative, options in patterns.iteritems():
            for option in options:
                print "Testing that Pattern('{0}') == '{1}'".format(option, normative)
                assert normative == str(Pattern(option))

    def test_compilation_bound_start(self):
        p = Pattern("/*.py")
        assert p.bound_start is True
        assert p.bound_end is True
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [ ]

        p = Pattern("/test/*.py")
        assert p.bound_start is True
        assert p.bound_end is True
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [ Section(["test"]) ]

        p = Pattern("/test/dir/")
        assert p.bound_start is True
        assert p.bound_end is False
        assert p.file_pattern == "*"
        assert p.sections == [ Section(["test", "dir"]) ]

        p = Pattern("/start/**/test/*.py")
        assert p.bound_start is True
        assert p.bound_end is True
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [Section(["start"]), Section(["test"])]

        p = Pattern("/start/**/test/**/*.py")
        assert p.bound_start is True
        assert p.bound_end is False
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [Section(["start"]), Section(["test"])]

    def test_compilation_unbound_start(self):
        p = Pattern("*.py")
        assert p.bound_start is False
        assert p.bound_end is False
        assert str(p.file_pattern) == "*.py"
        assert p.sections == []

        p = Pattern("test/*.py")
        assert p.bound_start is False
        assert p.bound_end is True
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [ Section(["test"]) ]

        p = Pattern("**/test/*.py")
        assert p.bound_start is False
        assert p.bound_end is True
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [Section(["test"])]

        p = Pattern("**/test/**")
        assert p.bound_start is False
        assert p.bound_end is False
        assert p.file_pattern == "*"

        assert p.sections == [Section(["test"])]

        p = Pattern("**/test/")
        assert p.bound_start is False
        assert p.bound_end is False
        assert p.file_pattern == "*"

        assert p.sections == [Section(["test"])]

        p = Pattern("**/test/**/*.py")
        assert p.bound_start is False
        assert p.bound_end is False
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [Section(["test"])]

        p = Pattern("start/**/test/**/*.py")
        assert p.bound_start is False
        assert p.bound_end is False
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [Section(["start"]), Section(["test"])]

    def test_complex_compilation(self):
        p1 = Pattern("dir/file.txt")
        p2 = Pattern("**/dir/file.txt")
        p3 = Pattern("/**/dir/file.txt")
        assert p1.sections == p2.sections
        assert p2.sections == p3.sections
        assert p1.bound_start is False
        assert p1.bound_start == p2.bound_start == p3.bound_start
        assert p1.bound_end == True
        assert p1.bound_end == p2.bound_end == p3.bound_end

    def test_match_pure_file_pattern(self):
        # No sections - all must match
        p = Pattern("test.py")
        assert p.match_directory([]) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("some/where/".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES

    def test_match_bound_start_file_pattern(self):
        p = Pattern("/test.py")
        assert p.match_directory([]) == MatchType.MATCH_BUT_NO_SUBDIRECTORIES
        assert p.match_directory("test".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p.match_directory("test/sub/".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p.match_directory("some/where/".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES

    def test_match_single_bound_start_no_sub(self):
        p = Pattern("/test/*.py")
        assert p.match_directory([]) == MatchType.NO_MATCH
        assert p.match_directory("test".split("/")) == MatchType.MATCH_BUT_NO_SUBDIRECTORIES
        assert p.match_directory("some/where/".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES

    def test_match_single_bound_start_any_sub(self):
        p = Pattern("/test/**/*")
        assert p.match_directory([]) == MatchType.NO_MATCH
        assert p.match_directory("test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("some/where/test".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p.match_directory("some/where/".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES

    def test_match_single_unbound_directory(self):
        p = Pattern("test/")
        assert p.match_directory([]) == MatchType.NO_MATCH
        assert p.match_directory("test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("some/where/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("middle/test/middle".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("not/a/hope".split("/")) == MatchType.NO_MATCH

        p = Pattern("**/test/**")
        assert p.match_directory([]) == MatchType.NO_MATCH
        assert p.match_directory("test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("some/where/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("middle/test/middle".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("not/a/hope".split("/")) == MatchType.NO_MATCH

    def test_match_single_bound_end_directory(self):
        p = Pattern("test/*")
        assert p.match_directory([]) == MatchType.NO_MATCH
        assert p.match_directory("test".split("/")) == MatchType.MATCH
        assert p.match_directory("some/where/test".split("/")) == MatchType.MATCH
        assert p.match_directory("middle/test/middle".split("/")) == MatchType.NO_MATCH
        assert p.match_directory("not/a/hope".split("/")) == MatchType.NO_MATCH

    def test_match_twin_unbound_directories(self):
        p = Pattern("some/**/test/")
        assert p.match_directory([]) == MatchType.NO_MATCH
        assert p.match_directory("test/test/test/test".split("/")) == MatchType.NO_MATCH
        assert p.match_directory("some/some/some".split("/")) == MatchType.NO_MATCH
        assert p.match_directory("some/where/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("a/some/where/test/b".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("some/where/else/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("some/where/a/long/way/apart/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("not/a/hope".split("/")) == MatchType.NO_MATCH

    def test_match_twin_directories(self):
        p = Pattern("/test/**/test/")
        assert p.match_directory("test/test/test/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("test/where/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("test/a/very/long/way/apart/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES

        assert p.match_directory([]) == MatchType.NO_MATCH
        assert p.match_directory("test".split("/")) == MatchType.NO_MATCH
        assert p.match_directory("not/a/hope".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p.match_directory("a/test/where/test/b".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p.match_directory("some/some/some".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES

        p = Pattern("/test/**/test/*.py")
        assert p.match_directory("test/test/test/test".split("/")) == MatchType.MATCH
        assert p.match_directory("test/where/test".split("/")) == MatchType.MATCH
        assert p.match_directory("test/a/very/long/way/apart/test".split("/")) == MatchType.MATCH

        assert p.match_directory([]) == MatchType.NO_MATCH
        assert p.match_directory("test".split("/")) == MatchType.NO_MATCH
        assert p.match_directory("not/a/hope".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p.match_directory("a/test/where/test/b".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p.match_directory("some/some/some".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES

    def test_match_multiple_unbound_directories(self):
        p = Pattern("a/**/b/**/c/**/d/")
        assert p.match_directory("test/a/test/test/b/c/test/test/d/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("test/a/test/a/test/b/c/test/c/test/d/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("test/a/test/b/test/test/d/test/c/test".split("/")) == MatchType.NO_MATCH

    def test_file_pattern(self):
        p = Pattern("*.py")
        match(p, [], [])
        match(p, ["a.no", "py"], [])
        match(p, ["x.px", "a.py", "a.pz", "b.py", "py"], ["a.py", "b.py"])
        p = Pattern("?bc.txt")
        match(p, ["a.no", "py"], [])
        match(p, ["abc.txt", "bbc.txt", "not.txt"], ["abc.txt", "bbc.txt"])

    def test_no_file_pattern(self):
        p = Pattern("")
        assert p.file_pattern == "*"

        match(p, [], [])
        s = ["a.py", "b.py"]
        match(p, s, s)
        s = ["x.px", "a.py", "a.pz", "b.py", "py"]
        match(p, s, s)

        p = Pattern("*")
        assert p.file_pattern == "*"
        match(p, [], [])
        s = ["a.py", "b.py"]
        match(p, s, s)
        s = ["x.px", "a.py", "a.pz", "b.py", "py"]
        match(p, s, s)


class TestPatternSet(object):
    def test_basic(self):
        py = Pattern("*.py")
        cvs = Pattern("**/CVS/")
        pycache = Pattern("__pycache__/")

        ps = PatternSet()
        assert ps.all_files() is False
        assert [ pat for pat in ps.iter() ] == []
        s = ["a.py", "b.py"]
        match(ps, s, [])

        ps.append(py)
        assert ps.all_files() is False
        assert [ pat for pat in ps.iter() ] == [ py ]
        s = ["a.py", "b.py"]
        match(ps, s, s)
        s = ["a.py", "b.py", "anything.goes"]
        match(ps, s, ["a.py", "b.py"])

        ps.append(cvs)
        assert ps.all_files() is True
        assert [ pat for pat in ps.iter() ] == [ py, cvs ]
        match(ps, s, s)

        ps.remove(cvs)
        ps.append(pycache)
        assert ps.all_files() is True
        assert [ pat for pat in ps.iter() ] == [ py, pycache ]
        match(ps, s, s)

        ps.remove(pycache)
        assert ps.all_files() is False
        assert [ pat for pat in ps.iter() ] == [ py ]
        match(ps, s, ["a.py", "b.py"])

    def test_extend(self):
        py = Pattern("*.py")
        cvs = Pattern("**/CVS/")
        pycache = Pattern("__pycache__/")

        ps1 = PatternSet()
        ps1.extend([py, cvs, pycache])
        assert [ pat for pat in ps1.iter() ] == [ py, cvs, pycache ]

        ps2 = PatternSet()
        ps2.extend(ps1)
        assert [ pat for pat in ps2.iter() ] == [ py, cvs, pycache ]

        ps1 = PatternSet()
        ps1.extend([py])
        assert [ pat for pat in ps1.iter() ] == [ py ]
        ps1.extend([cvs, pycache])
        assert [ pat for pat in ps1.iter() ] == [ py, cvs, pycache ]


class TestFileSetState(object):
    def test_parent(self):
        root = FileSetState("Label", "")
        a = FileSetState("Label", "a", root)
        assert a.parent == root
        b = FileSetState("Label", os.path.join("a", "b"), a)
        assert b.parent == a
        c = FileSetState("Label", os.path.join("a", "b", "c"), b)
        assert c.parent == b
        # Test the abrupt change from /a/b/c to /d
        d = FileSetState("Label", "d", c)
        assert d.parent == root

    def test_patterns_root(self):
        bound_start_top_all = Pattern("/test/*")
        bound_start_top_py  = Pattern("/test/*.py")
        bound_start_sub_all = Pattern("/test/")
        bound_start_sub_py  = Pattern("/test/**/*.py")
        bound_end_all       = Pattern("**/test/*")
        bound_end_py        = Pattern("**/test/*.py")
        bound_start_end     = Pattern("/test/**/test/*.py")
        unbound_all         = Pattern("**/*")
        unbound_py          = Pattern("**/*.py")

        all = [ bound_start_top_all, bound_start_top_py,
                bound_start_sub_all, bound_start_sub_py,
                bound_end_all,       bound_end_py,
                bound_start_end,
                unbound_all,         unbound_py ]

        # Test matches for the root directory
        fst = FileSetState("Label", "", None, all)
        file_set_state_location(fst, bound_start_top_all, UNMATCHED)
        file_set_state_location(fst, bound_start_top_py,  UNMATCHED)
        file_set_state_location(fst, bound_start_sub_all, UNMATCHED)
        file_set_state_location(fst, bound_start_sub_py,  UNMATCHED)
        file_set_state_location(fst, bound_end_all,       UNMATCHED)
        file_set_state_location(fst, bound_end_py,        UNMATCHED)
        file_set_state_location(fst, bound_start_end,     UNMATCHED)
        file_set_state_location(fst, unbound_all,         MATCHED_INHERIT)
        file_set_state_location(fst, unbound_py,          MATCHED_INHERIT)
        assert fst.no_possible_matches_in_subdirs() is False
        assert fst.matches_all_files_all_subdirs() is True

    def test_patterns_test_matching_dir(self):
        bound_start_top_all = Pattern("/test/*")
        bound_start_top_py  = Pattern("/test/*.py")
        bound_start_sub_all = Pattern("/test/")
        bound_start_sub_py  = Pattern("/test/**/*.py")
        bound_end_all       = Pattern("**/test/*")
        bound_end_py        = Pattern("**/test/*.py")
        bound_start_end     = Pattern("/test/**/test/*.py")
        unbound_all         = Pattern("**/*")
        unbound_py          = Pattern("**/*.py")

        all = [ bound_start_top_all, bound_start_top_py,
                bound_start_sub_all, bound_start_sub_py,
                bound_end_all,       bound_end_py,
                bound_start_end,
                unbound_all,         unbound_py ]

        # Test matches for the root directory
        fst = FileSetState("Label", "test", None, all)
        file_set_state_location(fst, bound_start_top_all, MATCHED_NO_SUBDIR)
        file_set_state_location(fst, bound_start_top_py,  MATCHED_NO_SUBDIR)
        file_set_state_location(fst, bound_start_sub_all, MATCHED_INHERIT)
        file_set_state_location(fst, bound_start_sub_py,  MATCHED_INHERIT)
        file_set_state_location(fst, bound_end_all,       MATCHED_AND_SUBDIR)
        file_set_state_location(fst, bound_end_py,        MATCHED_AND_SUBDIR)
        file_set_state_location(fst, bound_start_end,     UNMATCHED)
        file_set_state_location(fst, unbound_all,         MATCHED_INHERIT)
        file_set_state_location(fst, unbound_py,          MATCHED_INHERIT)
        assert fst.no_possible_matches_in_subdirs() is False
        assert fst.matches_all_files_all_subdirs() is True

    def test_patterns_test_no_match(self):
        bound_start_top_all = Pattern("/test/*")
        bound_start_top_py  = Pattern("/test/*.py")
        bound_start_sub_all = Pattern("/test/")
        bound_start_sub_py  = Pattern("/test/**/*.py")
        bound_end_all       = Pattern("**/test/*")
        bound_end_py        = Pattern("**/test/*.py")
        bound_start_end     = Pattern("/test/**/test/*.py")
        unbound_all         = Pattern("**/*")
        unbound_py          = Pattern("**/*.py")

        all = [ bound_start_top_all, bound_start_top_py,
                bound_start_sub_all, bound_start_sub_py,
                bound_end_all,       bound_end_py,
                bound_start_end,
                unbound_all,         unbound_py ]

        # Test matches for the root directory
        fst = FileSetState("Label", "nottest", None, all)
        file_set_state_location(fst, bound_start_top_all, NOT_PRESENT)
        file_set_state_location(fst, bound_start_top_py,  NOT_PRESENT)
        file_set_state_location(fst, bound_start_sub_all, NOT_PRESENT)
        file_set_state_location(fst, bound_start_sub_py,  NOT_PRESENT)
        file_set_state_location(fst, bound_end_all,       UNMATCHED)
        file_set_state_location(fst, bound_end_py,        UNMATCHED)
        file_set_state_location(fst, bound_start_end,     NOT_PRESENT)
        file_set_state_location(fst, unbound_all,         MATCHED_INHERIT)
        file_set_state_location(fst, unbound_py,          MATCHED_INHERIT)
        assert fst.no_possible_matches_in_subdirs() is False
        assert fst.matches_all_files_all_subdirs() is True

    def test_patterns_test_no_possible_match(self):
        bound_start_top_all = Pattern("/test/*")
        bound_start_top_py  = Pattern("/test/*.py")
        bound_start_sub_all = Pattern("/test/")
        bound_start_sub_py  = Pattern("/test/**/*.py")
        bound_start_end     = Pattern("/test/**/test/*.py")

        all = [ bound_start_top_all, bound_start_top_py,
                bound_start_sub_all, bound_start_sub_py,
                bound_start_end
                ]

        # Test matches for the root directory
        fst = FileSetState("Label", "nottest", None, all)
        file_set_state_location(fst, bound_start_top_all, NOT_PRESENT)
        file_set_state_location(fst, bound_start_top_py,  NOT_PRESENT)
        file_set_state_location(fst, bound_start_sub_all, NOT_PRESENT)
        file_set_state_location(fst, bound_start_sub_py,  NOT_PRESENT)
        file_set_state_location(fst, bound_start_end,     NOT_PRESENT)
        assert fst.no_possible_matches_in_subdirs() is True
        assert fst.matches_all_files_all_subdirs() is False

    def test_patterns_inherit_with_file(self):
        pattern1  = Pattern("/a/**/*.a")
        pattern2  = Pattern("**/b/**/*.b")
        pattern3  = Pattern("/a/b/c/*.c")
        all_files = [ "not", "a.a", "b.b", "c.c"]
        a_files   = [ "a.a", "aa.a"]

        # Test matches for the root directory
        root = FileSetState("Label", "", None, [pattern1, pattern2, pattern3])
        file_set_state_location(root, pattern1, UNMATCHED)
        file_set_state_location(root, pattern2, UNMATCHED)
        file_set_state_location(root, pattern3, UNMATCHED)
        assert not root.match([])
        assert not root.match(all_files)
        assert not root.match(a_files)

        a = FileSetState("Label", "a", root)
        file_set_state_location(a, pattern1, MATCHED_INHERIT)
        file_set_state_location(a, pattern2, UNMATCHED)
        file_set_state_location(a, pattern3, UNMATCHED)
        assert not a.match([])
        assert {"a.a"} == a.match(all_files)
        assert {"a.a", "aa.a"} == a.match(a_files)

        b = FileSetState("Label", os.path.join("a", "b"), a)
        file_set_state_location(b, pattern1, NOT_PRESENT) # In parent
        file_set_state_location(b, pattern2, MATCHED_INHERIT)
        file_set_state_location(b, pattern3, UNMATCHED)
        assert not b.match([])
        assert {"a.a", "b.b"} == b.match(all_files)
        assert {"a.a", "aa.a"} == b.match(a_files)

        c = FileSetState("Label", os.path.join("a", "b", "c"), b)
        file_set_state_location(c, pattern1, NOT_PRESENT) # In grandparent
        file_set_state_location(c, pattern2, NOT_PRESENT) # In parent
        file_set_state_location(c, pattern3, MATCHED_NO_SUBDIR)
        assert not c.match([])
        assert {"a.a", "b.b", "c.c"} == c.match(all_files)
        assert {"a.a", "aa.a"} == c.match(a_files)

        d = FileSetState("Label", os.path.join("a", "b", "c", "d"), b)
        file_set_state_location(d, pattern1, NOT_PRESENT) # In great-grandparent
        file_set_state_location(d, pattern2, NOT_PRESENT) # In grandparent
        file_set_state_location(d, pattern3, NOT_PRESENT) # Not applicable
        assert not d.match([])
        assert {"a.a", "b.b"} == d.match(all_files)
        assert {"a.a", "aa.a"} == b.match(a_files)

    def test_patterns_inherit_all_files(self):
        pattern1  = Pattern("/a/**/*")
        all_files = [ "not", "a.a", "b.b", "c.c"]

        # Test matches for the root directory
        root = FileSetState("Label", "", None, [pattern1])
        file_set_state_location(root, pattern1, UNMATCHED)
        assert not root.match([])
        assert not root.match(all_files)

        a = FileSetState("Label", "a", root)
        file_set_state_location(a, pattern1, MATCHED_INHERIT)
        assert not a.match([])
        assert set(all_files) == a.match(all_files)

        b = FileSetState("Label", os.path.join("a", "b"), a)
        file_set_state_location(b, pattern1, NOT_PRESENT) # In parent
        file_set_state_location(a, pattern1, MATCHED_INHERIT)
        assert not b.match([])
        assert b.parent == a
        assert set(all_files) == b.match(all_files)


class TestFileSet(object):
    def test_basic(self):
        root = os.path.dirname(os.path.dirname(__file__))
        pattern_all = os.path.sep + os.path.join("**", "*")
        pattern_py  = os.path.sep + os.path.join("**", "*.py")
        pattern_pyc = os.path.sep + os.path.join("**", "*.pyc")
        pattern_txt = os.path.sep + os.path.join("**", "*.txt")
        print "Formic directory=", root, "include=", pattern_all
        definitive_count = find_count(root, "*.py")

        fs = FileSet(directory=root, include=pattern_py, symlinks=False)
        files = [ os.path.join(root, dir, file) for dir, file in fs.files() ]
        assert definitive_count == len(files)
        assert [] == [ file for file in files if not os.path.isfile(file) ]
        assert files == [ file for file in files if file.endswith(".py") ]

        fs = FileSet(directory=root, include=pattern_all, exclude=[pattern_pyc, pattern_txt])
        files = [ os.path.join(root, dir, file) for dir, file in fs.files() ]
        assert definitive_count <= len(files)
        assert [] == [ file for file in files if not os.path.isfile(file) ]
        assert [] == [ file for file in files if file.endswith(".pyc") ]
        assert [] == [ file for file in files if file.endswith(".txt") ]

    def test_bound_root(self):
        """Unit test to pick up Issue #1"""
        original_dir = os.getcwd()
        curdir = os.path.dirname(os.path.dirname(__file__))
        os.chdir(curdir)
        try:
            import glob
            actual = glob.glob("*.py")

            fs = FileSet(include="/*.py", default_excludes=False)
            count = 0
            for file in fs:
                count += 1
                print "File:", file
                head, tail = os.path.split(file)
                assert curdir == head
                assert tail in actual
                assert tail.endswith(".py")
            assert len(actual) == count
        finally:
            os.chdir(original_dir)

    def test_cwd(self):
        fs = FileSet(include="*")
        assert fs.directory is None
        assert os.getcwd() == fs.get_directory()

        directory = os.path.dirname(__file__) + os.path.sep + os.path.sep + os.path.sep
        fs = FileSet(directory=directory, include="*")
        assert fs.directory == os.path.dirname(__file__)
        assert fs.get_directory() == os.path.dirname(__file__)

    def test_vs_find(self):
        compare_find_and_formic(get_test_directory())
        compare_find_and_formic(get_test_directory(), "a*")

    def test_iterator(self):
        fs = FileSet(include="*.py")
        i = fs.__iter__()
        assert { f for f in fs.qualified_files() } == { f for f in i }


class TestMiscellaneous(object):
    def test_version(self):
        assert "0.9beta6" == get_version()

    def test_rooted(self):
        curdir = os.getcwd()
        dir = os.path.dirname(os.path.dirname(__file__))
        wild = "**/*.rst"
        os.chdir(dir)
        try:
            fileset = FileSet(include=wild, directory=dir)
            for filename in fileset.qualified_files():
                print filename
            print "Absolute, starting at ", dir
            absolute = [ filename for filename in FileSet(include=wild, directory=dir) ]
            print "Relative"
            relative = [ filename for filename in FileSet(include=wild)]
            print "Absolute, starting at /"
            rooted   = [ filename for filename in FileSet(include=dir + os.path.sep + wild, directory=os.path.sep)]
            assert len(rooted) == len(relative) == len(absolute)
            combined = zip(rooted, relative, absolute)
            for root, rel, abso in combined:
                print root, "<->", rel, "<->", abso
                assert root.endswith(rel)
                assert abso.endswith(rel)
        finally:
            os.chdir(curdir)