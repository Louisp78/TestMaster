from dataclasses import dataclass
from .bcolors import Bcolors
from .test import Test
from os import walk

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

    # Run testsuite all subtests of it
    # Print result in stdout
    def run(self, verbose=False, timeout=0.5):

        # In case of auto-generated tests from a folder specified
        if self.tests == None:
            if self.tests_from_folder == None:
                raise ValueError("tests must be specified either tests_from_folder")
            
            filenames = next(walk(self.tests_from_folder), (None, None, []))[2]
            tests = []
            for file in filenames:
                tests.append(Test(name=file, input=self.tests_from_folder + file, exp_errcode=0, from_folder=True))
            self.tests = tests
        # ===

        nb_test_ok = 0
        # Run all subtests
        for test in self.tests:
            if test.run(self.baseInput, verbose, timeout):
                nb_test_ok += 1
        # ===

        # Display
        if nb_test_ok != len(self.tests):
            print(Bcolors.BOLD + Bcolors.FAIL + "[KO] " + Bcolors.WARNING + "suite : %r\t\ttests passed: %r/%r" % (self.name, nb_test_ok, len(self.tests)) + Bcolors.ENDC)
        else :
            print(Bcolors.BOLD + Bcolors.OKGREEN + "[OK] " + Bcolors.OKCYAN + "suite : %r\t\ttests passed: %r/%r" % (self.name, nb_test_ok, len(self.tests)) + Bcolors.ENDC)
        for test in self.tests:
            print(test.print, end="")
        print()

        return nb_test_ok == len(self.tests), nb_test_ok