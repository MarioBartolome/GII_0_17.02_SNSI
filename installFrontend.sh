#!/bin/bash
#############
# Author: Mario Bartolome
# Date: Apr 14, 2018
#
# This file will install all the necessary python packages to
# deploy and run this solution. 
#
#############

createEnv()
{
    echo "[+] Creating environment on ../$1..."
    mkdir ../$1 && python3 -m venv ../$1 && echo "[*] Python environment created on parent folder!"
    isEnv=1
}

sigKillDetected()
{
      echo "[!] Could not finish the process!"
      if [ "x$1" != "x" ] && [ -d ../$1 ]; then
        echo "Cleaning up..."
        rm -rf ../$1
      fi
      exit 1
}

trap 'sigKillDetected $1' INT

if [ $# -ne 1 ]; then
    echo "[!] USAGE: $0 VirtualEnvName" >&2
    exit 1
fi

echo "[+] Prior to attempt to install Python dependencies, make sure your system has the following packages installed:"
echo -e "\t gcc - I'm gonna need to compile some stuff..."
echo -e "\t python3-dev - To compile some Python dependencies"
echo -e "\t python3-venv - To create a virtual environment"
echo -e "\t python3-setuptools - To setup the Python dependencies"
echo "otherwise the setup will fail"

echo -e "\nDo you want to continue and create $1 virtualEnv?[enter]"
read

isEnv=0

if [ -d "../$1" ]; then
    echo "[!] Uh oh, it seems $1 already exists on the parent directory"
    if [ -f "../$1/pyvenv.cfg" ]; then
        isEnv=1
        echo "[!] It also seems to be an existing Python Environment with the following packages on it: "
        ../$1/bin/pip list --format=columns
    fi
    echo "[!] Do you want to overwrite it(yes/no)?"
    read answer
    if [ $answer = "yes" ]; then
        rm -r ../$1
        isEnv=0
        echo "[*] Previous environment deleted"
        createEnv $1
    fi
else
    createEnv $1
fi

if [ $isEnv -eq 1 ]; then
    echo "[+] Activating $1..."
    source ../$1/bin/activate
    echo "[*] Python environment successfully activated"
    echo "[+] Installing dependencies, this may take a while..."
    python3 setupWebUI.py install
    echo "[*] Done! Use "
    echo -e "\tsource ../$1/bin/activate"
    echo "to enable the Virtual Environment"
else
    echo "[!] $1 does not seem to be a Python VirtualEnvironment"
    exit 1
fi
