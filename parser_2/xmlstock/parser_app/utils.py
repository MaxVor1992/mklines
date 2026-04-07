HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

engines = {
    11: "yandex native",
    12: "yandex XML",
    13: "yandex Live",
    21: "google native",
    22: "google XML"
}


def print_error(s, **kwargs):
    print(f"{FAIL}{s}{ENDC}")


def print_ok(s, **kwargs):
    print(f"{OKGREEN}{s}{ENDC}")


def print_warning(s, **kwargs):
    print(f"{WARNING}{s}{ENDC}")
