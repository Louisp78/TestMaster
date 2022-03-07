from email.mime import base
import subprocess
import threading
import yaml
from dataclasses import dataclass
from dacite import from_dict
import difflib

from os import walk

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.stdout = None
        self.stderr = None

    def run(self, timeout):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = self.process.communicate()
            self.stdout = stdout
            self.stderr = stderr

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()

class Result:
    def __init__(self, out, err, err_code) -> None:
        self.out = out
        self.err = err
        self.err_code = err_code


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

    def run(self, baseInput="") -> bool:
        cmd = Command(baseInput + " " + self.input)
        cmd.run(timeout=3)  # TODO timeout set here
        result_error = '\t' + bcolors.BOLD + bcolors.FAIL + "[KO] " + bcolors.WARNING + "case : %r\n" % (self.name) + bcolors.ENDC + '\t'
        test_ok = True
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
            self.print = '\t' + bcolors.BOLD + bcolors.OKGREEN + "[OK] " + bcolors.OKCYAN + "case : %r\n" % (self.name) + bcolors.ENDC
        
        return test_ok


@dataclass
class Testsuite:
    name: str
    baseInput: str = ""
    tests: list[Test] = None
    tests_from_folder: str = None

    def __repr__(self) -> str:
        return "== %r ==\nbaseInput: %r\ntests:\n%r" % (
            self.name,
            self.baseInput,
            self.tests)

    def run(self):

        if self.tests == None:
            if self.tests_from_folder == None:
                raise ValueError("tests must be specified either tests_from_folder")
            
            filenames = next(walk(self.tests_from_folder), (None, None, []))[2]
            tests = []
            for file in filenames:
                tests.append(Test(name=file, input=self.tests_from_folder + file, exp_errcode=0))
            self.tests = tests

        nb_test_ok = 0
        for test in self.tests:
            if test.run(self.baseInput):
                nb_test_ok += 1
        if nb_test_ok != len(self.tests):
            print(bcolors.BOLD + bcolors.FAIL + "[KO] " + bcolors.WARNING + "suite : %r\t\ttests passed: %r/%r" % (self.name, nb_test_ok, len(self.tests)) + bcolors.ENDC)
        else :
            print(bcolors.BOLD + bcolors.OKGREEN + "[OK] " + bcolors.OKCYAN + "suite : %r\t\ttests passed: %r/%r" % (self.name, nb_test_ok, len(self.tests)) + bcolors.ENDC)
        for test in self.tests:
            print(test.print, end="")
        print()
        return nb_test_ok == len(self.tests), nb_test_ok

list_map = []
with open("tests.yaml", "r") as stream:
    try:
        list_map = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
list = []
total_tests_ok = 0
total_suite_ok = 0
total_tests = 0
for map in list_map:
    testsuite = from_dict(data_class=Testsuite, data=map)
    list.append(testsuite)
    (is_ok, nb_ok_tests) = testsuite.run()
    total_tests_ok += nb_ok_tests
    total_tests += len(testsuite.tests)
    if is_ok:
        total_suite_ok += 1
print()
print(bcolors.WARNING + bcolors.BOLD + "[RECAP] " + bcolors.ENDC + "suites passed: %r/%r" % (total_suite_ok, len(list)))
print( bcolors.WARNING + bcolors.BOLD + "[RECAP] " + bcolors.ENDC + "tests passed: %r/%r" % (total_tests_ok, total_tests))