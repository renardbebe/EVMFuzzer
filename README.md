EVMFuzzer
======

*An Detection Tool for Ethereum Virtual Machine (EVM).*

## Folder Structure

**Dependency Libraries：**

\> `py-evm`  Source code of EVM written in Python.

\> `aleth`  Source code of EVM written in CPP.

\> `jsEVM`  Source code of EVM written in JavaScript.

\> `myEVM`  Source code of User's EVM.

**Project Folders：**

\> `contract`  Library of smart contracts.

\> `TestOut`  Files generated during running.

**Executable Scripts：**

\> `Run` 


## Quick Start

To start the work, install all dependent libraries and platforms.

Guidance can be found in the following repositories:

[py-evm](https://github.com/pipermerriam/py-evm)   [aleth](https://github.com/ethereum/aleth)   [js-evm](https://github.com/ethereumjs/ethereumjs-vm)   [geth](https://github.com/ethereum/go-ethereum)

Execute a python virtualenv 

```
python -m virtualenv env
source env/bin/activate
```

The runtime environment is python3, and just run:

```
$ python3 Run.py
```

You are done! 
