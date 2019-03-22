#!/bin/bash

# Run this script from the project's main directory, e.g.
# cd python-interpreter
# ./scripts/make-python.sh


function antlr4() {
    java -jar ../scripts/antlr-4*.jar $@
}

cd grammar
antlr4 -Dlanguage=Python3 -o ../src/main/python/generated *.g4
