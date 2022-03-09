
from asyncio import current_task
from classes.testsuite import Testsuite
from classes.bcolors import Bcolors
import yaml
from dacite import from_dict
import getopt, sys


def pretty_print():
    # Pretty print
    title = Bcolors.OKCYAN + """
    ________           _____              __________      
    ___  __/_____________  /___________  ____(_)_  /_____ 
    __  /  _  _ \_  ___/  __/_  ___/  / / /_  /_  __/  _ \\
    _  /   /  __/(__  )/ /_ _(__  )/ /_/ /_  / / /_ /  __/
    /_/    \___//____/ \__/ /____/ \__,_/ /_/  \__/ \___/ 

    Written by Louis Place.
    """ + Bcolors.ENDC
    print(title)


# Main method
pretty_print()

argumentList = sys.argv[1:]
options = "hvt:s:"
long_options = ["help", "verbose", "timeout=", "suite="]
stop = False
timeout = 0.5
verbose = False
run_custom_testsuite = None
try:

    arguments, values = getopt.getopt(argumentList, options, long_options)

    for currentArgument, currentValue in arguments:

        if currentArgument in ("-h", "--help"):
            help_msg = """
            -v or --verbose : Activate verbose mode to show commands executed
            -t <timeout in seconds> : Use a timeout of x seconds during tests
            -s <name of testsuite> or --suite <name of testsuite> : Run only the specified testsuite
            -h or --help : For help
            """
            print (help_msg)
            stop = True

        elif currentArgument in ("-v", "--verbose"):
            print (Bcolors.WARNING + Bcolors.BOLD + "[VERBOSE] " + Bcolors.ENDC + "Enabling verbose mode !\n")
            verbose = True

        elif currentArgument in ("-t", "--timeout"):
            print ((Bcolors.WARNING + Bcolors.BOLD + "[TIMEOUT] " + Bcolors.ENDC + "Enabling timeout of %r seconds\n") % (currentValue))
            timeout = int(currentValue)

        elif currentArgument in ("--suite", "-s"):
            print ((Bcolors.WARNING + Bcolors.BOLD + "[SUITE] " + Bcolors.ENDC + "Running only %r suite. \n") % (currentValue))
            if run_custom_testsuite == None:
                run_custom_testsuite = [currentValue]
            else:
                run_custom_testsuite.append(currentValue)

except getopt.error as err:
    print (str(err))

if not stop:
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
        if run_custom_testsuite != None and testsuite.name in run_custom_testsuite:
            (is_ok, nb_ok_tests) = testsuite.run(verbose, timeout)
        elif run_custom_testsuite == None:
            (is_ok, nb_ok_tests) = testsuite.run(verbose, timeout)
        else:
            continue
        list.append(testsuite)
        total_tests_ok += nb_ok_tests
        total_tests += len(testsuite.tests)
        if is_ok:
            total_suite_ok += 1
    print()
    print(Bcolors.WARNING + Bcolors.BOLD + "[RECAP] " + Bcolors.ENDC + "suites passed: %r/%r" % (total_suite_ok, len(list)))
    print( Bcolors.WARNING + Bcolors.BOLD + "[RECAP] " + Bcolors.ENDC + "tests passed: %r/%r" % (total_tests_ok, total_tests))