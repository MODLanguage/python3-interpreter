# Minimal Object Description Language (MODL) Interpreter

## Building

> **NOTE:** Java runtime is required. The ANTLR4 JAR itself is
> currently included in the scripts directory.


From the root of this project, execute the following:

```bash
./scripts/make-python.sh
```

This will generate the Python parser files in `src/main/python/generated` -
the contents will look something like this:

```
MODLLexer.interp	MODLParser.interp	MODLParserListener.py
MODLLexer.py		MODLParser.py		README.txt
MODLLexer.tokens	MODLParser.tokens
```   



