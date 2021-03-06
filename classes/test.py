from dataclasses import dataclass
from .bcolors import Bcolors
from .command import Command
import difflib
import re
from os import path

def _unidiff_output(expected, actual):
    """
    Helper function. Returns a string containing the unified diff of two multiline strings.
    """

    expected=expected.splitlines(keepends=True)
    actual=actual.splitlines(keepends=True)

    diff=difflib.unified_diff(expected, actual)

    return ''.join(diff)

@dataclass
class Test():
    name: str
    input: str
    exp_out: str = None
    exp_out_file: str = None
    exp_err_file: str = None
    exp_err_regex: str = None
    exp_err: str = None
    exp_errcode: int = None
    from_folder: bool = False
    print: str = None

    def __repr__(self) -> str:
        return "%s(== %r ==\ninput = %r\nexp_out = %r\nexp_err = %r\nexp_errcode = %r\n" % (self.__class__.__name__,
                                                                                            self.name, self.input,
                                                                                            self.exp_out,
                                                                                            self.exp_err,
                                                                                            self.exp_errcode)

    def run(self, baseInput="", verbose=False, timeout=0.5, auto_exp=False) -> bool:
        # Run command
        cmd = Command(baseInput + " " + self.input)
        cmd.run(timeout) 
        # ===

        # if a "exp_out" is in the path tests out from this folder
        if auto_exp and self.from_folder and self.input.rfind('/') != -1:
            path_to_exp_file = self.input[0:self.input.rfind('/'):] + "/exp_out/" + self.input[self.input.rfind('/') + 1:]
            if path.exists(path_to_exp_file):
                self.exp_out_file = path_to_exp_file

        result_error = '\t' + Bcolors.BOLD + Bcolors.FAIL + "[KO] " + Bcolors.WARNING + "case : %r\n" % (self.name) + Bcolors.ENDC + '\t'
        test_ok = True
        # Display result from result of execution of command

        if self.exp_out != None or self.exp_out_file != None:
            out = cmd.stdout.decode("utf-8")
            if self.exp_out_file != None:
                file = open(self.exp_out_file, "r")
                self.exp_out = file.read()
            res = _unidiff_output(self.exp_out, out)
            result_error += res
            test_ok = res == ""
        if self.exp_err != None or self.exp_err_file != None or self.exp_err_regex != None:
            err = cmd.stderr.decode("utf-8")
            
            if self.exp_err != None:

                if self.exp_err_file != None:
                    file = open(self.exp_err_file, "r")
                    self.exp_err = file.read()
            
                res = _unidiff_output(self.exp_err, err)
                result_error += res
                test_ok = res == ""

            elif self.exp_err_regex != None:
                reg_matcher = re.compile(self.exp_err_regex)
                mo = reg_matcher.search(err)
                res = ""
                if mo is None:
                    res += "Error message not matching provided regex"
                    test_ok = False
                result_error += res

        if self.exp_errcode != None:
            if self.exp_errcode != cmd.process.returncode:
                test_ok = False
                result_error += "Expected return code %r got %r.\n" % (self.exp_errcode, cmd.process.returncode)
        if not test_ok:
            self.print = result_error
        else:
            self.print = '\t' + Bcolors.BOLD + Bcolors.OKGREEN + "[OK] " + Bcolors.OKCYAN + "case : %r\n" % (self.name) + Bcolors.ENDC
        # ===

        # In case of verbose mode display command 
        if verbose:
            self.print += Bcolors.WARNING + "\t\t [VERBOSE] cmd: '" + baseInput + " " + self.input + "'" + Bcolors.ENDC + '\n'
            self.print += Bcolors.WARNING + "\t\t [VERBOSE] output :\n " + Bcolors.ENDC + cmd.stdout.decode("utf-8") + '\n'
            self.print += Bcolors.WARNING + "\t\t [VERBOSE] output_error :\n " + Bcolors.ENDC + cmd.stderr.decode("utf-8")
        # ===

        return test_ok