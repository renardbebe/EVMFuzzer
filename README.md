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

To start the work, there are THREE steps need to be done.

First, install all dependent libraries and platforms.
```
$ bash init.sh
```
More details can be found in the following repositories:

[py-evm](https://github.com/pipermerriam/py-evm)   [aleth](https://github.com/ethereum/aleth)   [js-evm](https://github.com/ethereumjs/ethereumjs-vm)   [geth](https://github.com/ethereum/go-ethereum)

Next, clone the responstory, put the **source code** of your EVM in **myEVM/** folder and modify the PROJECT_PATH in Run.py.

Finally, you can execute a python virtualenv just in case.

```
$ python -m virtualenv env
$ source env/bin/activate
```

The runtime environment is python3, and just run the script and follow the guidance:

```
$ python3 Run.py
```

You are done! 
