#!/bin/bash

lsb_release -a| grep 'Description' | awk '{print $2,$3,$4}' | sed 's/^1000//'| grep Raspbian