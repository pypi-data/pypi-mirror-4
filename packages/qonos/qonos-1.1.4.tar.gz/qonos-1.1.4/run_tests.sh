#!/bin/bash

function usage {
  echo "Usage: $0 [OPTION]..."
  echo "Run QonoS' test suite(s)"
  echo ""
  echo "  -V, --virtual-env        Always use virtualenv.  Install automatically if not present"
  echo "  -N, --no-virtual-env     Don't use virtualenv.  Run tests in local environment"
  echo "  -f, --force              Force a clean re-build of the virtual environment. Useful when dependencies have been added."
  echo "  --unittests-only         Run unit tests only, exclude functional tests."
  echo "  -p, --pep8               Just run pep8"
  echo "  -h, --help               Print this usage message"
  echo ""
  echo "Note: with no options specified, the script will try to run the tests in a virtual environment,"
  echo "      If no virtualenv is found, the script will ask if you would like to create one.  If you "
  echo "      prefer to run tests NOT in a virtual environment, simply pass the -N option."
  exit
}

function process_option {
  case "$1" in
    -h|--help) usage;;
    -V|--virtual-env) let always_venv=1; let never_venv=0;;
    -N|--no-virtual-env) let always_venv=0; let never_venv=1;;
    -p|--pep8) let just_pep8=1;;
    -f|--force) let force=1;;
    --unittests-only) noseopts="$noseopts --exclude-dir=qonos/tests/functional";;
    -c|--coverage) noseopts="$noseopts --with-coverage --cover-package=qonos";;
    -*) noseopts="$noseopts $1";;
    *) noseargs="$noseargs $1"
  esac
}

venv=.venv
with_venv=tools/with_venv.sh
always_venv=0
never_venv=0
force=0
noseopts=
noseargs=
wrapper=""
just_pep8=0

export NOSE_WITH_OPENSTACK=1
export NOSE_OPENSTACK_COLOR=1
export NOSE_OPENSTACK_RED=0.05
export NOSE_OPENSTACK_YELLOW=0.025
export NOSE_OPENSTACK_SHOW_ELAPSED=1
export NOSE_OPENSTACK_STDOUT=1

for arg in "$@"; do
  process_option $arg
done

function run_tests {
  # Cleanup *pyc
  ${wrapper} find . -type f -name "*.pyc" -delete
  # Just run the test suites in current environment
  ${wrapper} rm -f tests.sqlite
  ${wrapper} $NOSETESTS
}

function run_pep8 {
  # Files of interest
  # NOTE(esheffield): Pulled from nova...
  # NOTE(lzyeval): Avoid selecting qonos-api-paste.ini and qonos.conf in qonos/bin
  #                when running on devstack.
  # NOTE(lzyeval): Avoid selecting *.pyc files to reduce pep8 check-up time
  #                when running on devstack.
  srcfiles=`find qonos -type f -name "*.py" ! -wholename "qonos\/openstack*"`
  srcfiles+=" `find bin -type f ! -name "qonos.conf*" ! -name "*api-paste.ini*" ! -name "*~"`"
  srcfiles+=" `find tools -type f -name "*.py"`"
  srcfiles+=" `find smoketests -type f -name "*.py"`"
  srcfiles+=" setup.py"

  # Until all these issues get fixed, ignore.
  ignore='--ignore=E125,E126,E12,E711,E721,E712,H302,H403,H404'

  echo "Running hacking.py self test"
  ${wrapper} python tools/hacking.py --doctest

  # Then actually run it
  echo "Running pep8"
  ${wrapper} python tools/hacking.py ${ignore} ${srcfiles}

  ${wrapper} bash tools/unused_imports.sh

  #echo "Running pep8 ..."
  #PEP8_EXCLUDE=".venv,.tox,dist,doc,openstack"
  #PEP8_OPTIONS="--exclude=$PEP8_EXCLUDE --repeat"
  #PEP8_IGNORE="--ignore=E125,E126,E711,E712"
  #PEP8_INCLUDE="."
  # ${wrapper} pep8 $PEP8_OPTIONS $PEP8_INCLUDE $PEP8_IGNORE
}


NOSETESTS="nosetests $noseopts $noseargs"

if [ $never_venv -eq 0 ]
then
  # Remove the virtual environment if --force used
  if [ $force -eq 1 ]; then
    echo "Cleaning virtualenv..."
    rm -rf ${venv}
  fi
  if [ -e ${venv} ]; then
    wrapper="${with_venv}"
  else
    if [ $always_venv -eq 1 ]; then
      # Automatically install the virtualenv
      python tools/install_venv.py
      wrapper="${with_venv}"
    else
      echo -e "No virtual environment found...create one? (Y/n) \c"
      read use_ve
      if [ "x$use_ve" = "xY" -o "x$use_ve" = "x" -o "x$use_ve" = "xy" ]; then
        # Install the virtualenv and run the test suite in it
        python tools/install_venv.py
	wrapper=${with_venv}
      fi
    fi
  fi
fi

if [ $just_pep8 -eq 1 ]; then
    run_pep8
    exit
fi

run_tests || exit

if [ -z "$noseargs" ]; then
  run_pep8
fi
