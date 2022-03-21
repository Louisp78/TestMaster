from dataclasses import dataclass
from .bcolors import Bcolors
from .command import Command
import difflib

@dataclass
class Test():
    name: str
    input: str
    exp_out: str = None
    exp_err: str = None
    exp_errcode: int = None
    print: str = None

    def __repr__(self) -> str:
        return "%s(== %r ==\ninput = %r\nexp_out = %r\nexp_err = %r\nexp_errcode = %r\n" % (self.__class__.__name__,
                                                                                            self.name, self.input,
                                                                                            self.exp_out,
                                                                                            self.exp_err,
                                                                                            self.exp_errcode)

    def run(self, baseInput="", verbose=False, timeout=0.5) -> bool:
        # Run command
        cmd = Command(baseInput + " " + self.input)
        cmd.run(timeout)  # TODO timeout set here
        # ===

        result_error = '\t' + Bcolors.BOLD + Bcolors.FAIL + "[KO] " + Bcolors.WARNING + "case : %r\n" % (self.name) + Bcolors.ENDC + '\t'
        test_ok = True
        # Display result from result of execution of command
        if self.exp_out != None:
            res = ''.join(str(child) for child in (difflib.unified_diff(cmd.stdout.decode("utf-8"), self.exp_out, lineterm="\n\t")))
            result_error += res
            test_ok = "@" not in res
        if self.exp_err != None:
            res = ''.join(str(child) for child in (difflib.unified_diff(cmd.stderr.decode("utf-8"), self.exp_err, lineterm="\n\t")))
            result_error += res
            test_ok = "@" not in res
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
            self.print += Bcolors.WARNING + "\t\t [VERBOSE] output :\n " + Bcolors.ENDC + cmd.stdout.decode("utf-8")
        # ===

        return test_ok