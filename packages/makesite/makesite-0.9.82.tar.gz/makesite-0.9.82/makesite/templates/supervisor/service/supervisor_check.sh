#!/bin/bash

. $(dirname $0)/utils.sh

# Check supervisor
check_program supervisord "Install supervisor package"
check_program supervisorctl "Install supervisor package"
