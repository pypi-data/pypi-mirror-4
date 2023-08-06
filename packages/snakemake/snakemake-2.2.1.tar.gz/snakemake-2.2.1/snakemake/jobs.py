# -*- coding: utf-8 -*-

import os
import sys
import base64

from collections import defaultdict
from itertools import chain
from functools import partial

from snakemake.io import IOFile, Wildcards, _IOFile
from snakemake.utils import format, listfiles
from snakemake.exceptions import RuleException, ProtectedOutputException

__author__ = "Johannes Köster"


class Job:
    HIGHEST_PRIORITY = sys.maxsize

    def __init__(self, rule, targetfile=None, format_wildcards=None):
        self.rule = rule
        self.targetfile = targetfile
        self._hash = None
        self.wildcards_dict = self.rule.get_wildcards(targetfile)
        self.wildcards = Wildcards(fromdict=self.wildcards_dict)
        self._format_wildcards = (self.wildcards
            if format_wildcards is None
            else Wildcards(fromdict=format_wildcards))

        (self.input, self.output, self.params,
            self.log, self.ruleio) = rule.expand_wildcards(
            self.wildcards_dict)
        self.threads = rule.threads
        self.priority = rule.priority
        self._inputsize = None

        self.dynamic_output, self.dynamic_input = set(), set()
        self.temp_output, self.protected_output = set(), set()
        for f in self.output:
            f_ = self.ruleio[f]
            if f_ in self.rule.dynamic_output:
                self.dynamic_output.add(f)
            if f_ in self.rule.temp_output:
                self.temp_output.add(f)
            if f_ in self.rule.protected_output:
                self.protected_output.add(f)
        for f in self.input:
            if self.ruleio[f] in self.rule.dynamic_input:
                self.dynamic_input.add(f)

    @property
    def b64id(self):
        return base64.b64encode((self.rule.name +
            "".join(self.output)).encode("utf-8")).decode("utf-8")

    @property
    def inputsize(self):
        """
        Return the size of the input files.
        Input files need to be present.
        """
        if self._inputsize is None:
            self._inputsize = sum(map(os.path.getsize, self.input))
        return self._inputsize

    @property
    def message(self):
        """ Return the message for this job. """
        try:
            return (self.format_wildcards(self.rule.message)
                if self.rule.message else None)
        except AttributeError as ex:
            raise RuleException(str(ex), rule=self.rule)
        except KeyError as ex:
            raise RuleException("Unknown variable in message "
                "of shell command: {}".format(str(ex)), rule=self.rule)

    @property
    def shellcmd(self):
        """ Return the shell command. """
        try:
            return (self.format_wildcards(self.rule.shellcmd)
                if self.rule.shellcmd else None)
        except AttributeError as ex:
            raise RuleException(str(ex), rule=self.rule)
        except KeyError as ex:
            raise RuleException("Unknown variable in message "
                "of shell command: {}".format(str(ex)), rule=self.rule)

    @property
    def expanded_output(self):
        """ Iterate over output files while dynamic output is expanded. """
        for f, f_ in zip(self.output, self.rule.output):
            if f in self.dynamic_output:
                expansion = self.expand_dynamic(
                    f_,
                    restriction=self.wildcards,
                    omit_value=_IOFile.dynamic_fill)
                if not expansion:
                    yield f_
                for f, _ in expansion:
                    yield IOFile(f, self.rule)
            else:
                yield f

    @property
    def dynamic_wildcards(self):
        """ Return all wildcard values determined from dynamic output. """
        combinations = set()
        for f, f_ in zip(self.output, self.rule.output):
            if f in self.dynamic_output:
                for f, w in self.expand_dynamic(
                    f_,
                    restriction=self.wildcards,
                    omit_value=_IOFile.dynamic_fill):
                    combinations.add(tuple(w.items()))
        wildcards = defaultdict(list)
        for combination in combinations:
            for name, value in combination:
                wildcards[name].append(value)
        return wildcards

    @property
    def missing_input(self):
        """ Return missing input files. """
        return set(f for f in self.input if not f.exists)

    @property
    def output_mintime(self):
        """ Return oldest output file. """
        existing = [f.mtime for f in self.expanded_output if f.exists]
        if existing:
            return min(existing)
        return None

    def missing_output(self, requested=None):
        """ Return missing output files. """
        if requested is None:
            requested = set(self.output)
        files = set()

        for f, f_ in zip(self.output, self.rule.output):
            if f in requested:
                if f in self.dynamic_output:
                    if not self.expand_dynamic(
                    f_,
                    restriction=self.wildcards,
                    omit_value=_IOFile.dynamic_fill):
                        files.add("{} (dynamic)".format(f_))
                elif not f.exists:
                    files.add(f)
        return files

    def prepare(self):
        """
        Prepare execution of job.
        This includes creation of directories and deletion of previously
        created dynamic files.
        """
        protected = list(filter(lambda f: f.protected, self.expanded_output))
        if protected:
            raise ProtectedOutputException(self.rule, protected)
        if self.dynamic_output:
            for f, _ in chain(*map(
                partial(
                    self.expand_dynamic,
                    restriction=self.wildcards,
                    omit_value=_IOFile.dynamic_fill),
                self.rule.dynamic_output)):
                os.remove(f)
        for f, f_ in zip(self.output, self.rule.output):
            f.prepare()
        if self.log:
            self.log.prepare()

    def cleanup(self):
        """ Cleanup output files. """
        for f in self.expanded_output:
            if f.exists:
                f.remove()

    def format_wildcards(self, string):
        """ Format a string with variables from the job. """
        return format(string,
                      input=self.input,
                      output=self.output,
                      params=self.params,
                      wildcards=self._format_wildcards,
                      threads=self.threads,
                      log=self.log, **self.rule.workflow.globals)

    def __repr__(self):
        return self.rule.name

    def __eq__(self, other):
        if other is None:
            return False
        return self.rule == other.rule and (self.dynamic_output
            or self.wildcards_dict == other.wildcards_dict)

    def __lt__(self, other):
        return self.rule.__lt__(other.rule)

    def __gt__(self, other):
        return self.rule.__gt__(other.rule)

    def __hash__(self):
        if self._hash is None:
            self._hash = self.rule.__hash__()
            if not self.dynamic_output:
                for o in self.output:
                        self._hash ^= o.__hash__()
        return self._hash

    @staticmethod
    def expand_dynamic(pattern, restriction=None, omit_value=None):
        """ Expand dynamic files. """
        return list(listfiles(
            pattern, restriction=restriction, omit_value=omit_value))


class Reason:
    def __init__(self):
        self.updated_input = set()
        self.updated_input_run = set()
        self.missing_output = set()
        self.incomplete_output = set()
        self.forced = False
        self.noio = False

    def __str__(self):
        if self.forced:
            return "Forced execution"
        if self.missing_output:
            return "Missing output files: {}".format(
                ", ".join(self.missing_output))
        if self.incomplete_output:
            return "Incomplete output files: {}".format(
                ", ".join(self.incomplete_output))
        if self.updated_input:
            return "Updated input files: {}".format(
                ", ".join(self.updated_input))
        if self.updated_input_run:
            return "This run updates input files: {}".format(
                ", ".join(self.updated_input_run))
        if self.noio:
            return ("Rules with neither input nor "
                "output files are always executed")
        return ""

    def __bool__(self):
        return bool(self.updated_input or self.missing_output or self.forced
            or self.updated_input_run or self.noio)
