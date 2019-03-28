# -*- coding: UTF-8 -*-
import subprocess
import argparse
import random
import time
import os,shutil
import ctypes,sys
import heapq
import generate_input
import json

PROJECT_DIR = "/home/rm/Desktop/EVMFuzzer"    # NEED TO BE MODIFIED
contractPATH = PROJECT_DIR + "/contract/"
testPATH = PROJECT_DIR + "/TestOut/"

curC = 0
totalVarient = 0

X1 = 0         # different output
X2 = 0         # more gasUsed
X3 = 0         # less gasUsed
X4 = 0         # same gasUsed
X5 = 0         # more opSeqLen
X6 = 0         # less opSeqLen
X7 = 0         # same opSeqLen

fmt = '\033[0;3{}m{}\033[0m'.format
class color: 
    BLACK = 0    #黑 
    RED  = 1     #红 
    GREEN = 2    #绿 
    YELLOW = 3   #棕 
    BLUE  = 4    #蓝 
    PURPLE = 5   #紫 
    CYAN  = 6    #青 
    GRAY  = 7    #灰 

def show_help():
    """
    Show receving arguments
    """
    welcome = "WELCOME TO EVMFUZZer!"
    print(fmt(color.YELLOW, welcome.center(os.get_terminal_size().columns)))  # width: columns  height: lines
    print("\nVERSION:")
    print("   2.0.1")

    print("\nSTEPS:")
    print("   1 >> Download and setup the environment.")
    print("   2 >> Upload user's EVM and the interface.")
    print("   3 >> Fuzzing.")
    print("   4 >> Sending the report.")


def create_folder(dirPATH):
    """
    Create folders needed
    """
    binPATH = dirPATH + "bincode/"
    seedPATH = dirPATH + "seed/"
    outputPATH = dirPATH + "output/"

    if os.path.exists(binPATH) == False :
        os.makedirs(binPATH)
    if os.path.exists(seedPATH) == False :
        os.makedirs(seedPATH)
    if os.path.exists(outputPATH) == False :
        os.makedirs(outputPATH)
    return binPATH, seedPATH, outputPATH


def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='EVMFuzz')

    parser.add_argument('--file', dest='file', default="myContract.sol", type=str)
    parser.add_argument('--func', dest='func', default="multiPath", type=str)
    parser.add_argument('--bin', dest='bin', default="MyContract", type=str)
    parser.add_argument('--sig', dest='sig',
                        default="0x87f71cef00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000002",
                        type=str)
    args = parser.parse_args()
    return args


# delete pragma solidiy xxxx
# in case of compiler version problem
def preProcess(seedPATH, fileName):
    """
    Preprocess of smart contracts
    """
    f1 = open(contractPATH + fileName, 'r')
    f2 = open(seedPATH + "PreProcess_" + fileName, 'w')

    for _, line in enumerate(f1):
        if line.find("pragma") >= 0:
            pass
        else:
            f2.write(line)

    f1.close()
    f2.close()


def update_weight(dirPATH, fileName, combination):
    """
    Update mutator weights
    """
    # need mutator_diff_file.json
    diff_file = open(dirPATH + fileName, 'r')
    diff_list = diff_file.readlines()

    weight = {}  # an empty dict
    cnt = 0
    for i in range(len(diff_list)):
        cnt += int(diff_list[i])
    for i in range(len(diff_list)):
        weight[i+1] = float(int(diff_list[i]) / cnt)
    # print("Weight : {}".format(weight))

    # ret = list(map(weight.index, heapq.nlargest(len(weight), weight)))
    ret = sorted(weight.items(), key=lambda x: x[1], reverse=True)
    m_queue = []
    for i in range(len(ret)) :
        m_queue.append(ret[i][0])
    # print("Mutator_queue : {}".format(m_queue))

    choice = []
    if combination == 1 :
        # choice.append(m_queue[0])
        for i in range(len(m_queue)) :
            if i % 2 == 0 :
                choice.append(m_queue[i])
    elif combination == 2 :
        for i in range(len(m_queue)) :
            if i % 2 != 0 :
                choice.append(m_queue[i])
    elif combination == 3 :
        choice.append(m_queue[0])
        choice.append(m_queue[len(m_queue)-1])
    elif combination == 4 :
        choice.append(m_queue[random.randint(0, len(m_queue)-1)])

    return weight, choice

def editLine(dirPATH, filename, lineno, diff):
    fro = open(dirPATH+filename, "r")

    current_line = 0
    while current_line < lineno:
        fro.readline()
        current_line += 1

    seekpoint = fro.tell()
    frw = open(dirPATH+filename, "r+")
    frw.seek(seekpoint, 0)

    # read the line we want to discard
    test = fro.readline()  # 读入一行进内存 同时！ 文件指针下移实现删除
    test = diff
    frw.writelines(test)


    # now move the rest of the lines in the file
    # one line back
    chars = fro.readline()
    while chars:
        frw.writelines(chars)
        chars = fro.readline()

    fro.close()
    frw.truncate()
    frw.close()


def del_folder(path) :
    """
    Empty the folder
    """
    for i in os.listdir(path) :
        path_file = os.path.join(path, i)
        if os.path.isfile(path_file) :
            os.remove(path_file)
        else :
            del_folder(path_file)


def scheduling(contractList, diff_pri, time_pri):
    """
    Dynamic Priority Scheduling Algorithm
    """
    # print(contractList, diff_pri, time_pri)
    sortList = []
    priority = {}
    for i in range(len(contractList)):
        priority[i] = 0.7 * diff_pri[contractList[i]] + 0.3 * time_pri[contractList[i]]
    # sorted by priority
    data = [(pri, name) for pri, name in zip(priority, contractList)]
    data.sort(reverse=True)
    sortList = [name for pri, name in data]
    # update time priority
    for i in range(1, len(contractList)):
        time_pri[contractList[i]] += 1
    return sortList

def main():
    # args = parse_args()
    
    if os.path.exists(testPATH) :
        shutil.rmtree(testPATH)
    os.makedirs(testPATH)
    
    global curC
    global totalVarient

    global X1
    global X2
    global X3
    global X4
    global X5
    global X6
    global X7

    # upload user's interface
    print(fmt(color.RED, "\nPlease put your source code under **myEVM folder** and provide the trasaction interface."))
    print(fmt(color.RED, "The interface form should like: xxxxxx --code A --input B"))
    print(fmt(color.RED, "where A is the runtime code of contract, and B is the input data for transaction."))
    print(fmt(color.YELLOW, "E.g.  python3 /home/usr/project/myEVM/runTx.py --code A --data B"))
    ori = input()

    need_prefix = True
    print(fmt(color.RED, "Does the input data need '0x' prefix? The default setting is Yes. (Y/N)"))
    flag = input().upper()
    if flag.find("N") >= 0 :
        need_prefix = False

    ### For Test run
    ori = "python3 " + PROJECT_DIR + "/myEVM/runTx.py --code A --data B"

    for _, _, filenames in os.walk(contractPATH, followlinks=True):
        # Step 1.遍历合约
        for fileName in filenames:
            curC += 1
            dirPATH = testPATH + "contract" + str(curC) + "/" 
            binPATH, seedPATH, outputPATH = create_folder(dirPATH)
            
            contractList = []
            diff_pri = {}  # an empty dict
            time_pri = {}

            # 清空 diffHis文件 bincode/ seed/
            # if os.path.exists(dirPATH + "diffHis") :
            #     diffhistory = open(dirPATH + "diffHis", 'w')
            #     diffhistory.seek(0)
            #     diffhistory.truncate()
            #     diffhistory.close()
            # del_folder(binPATH)
            # del_folder(seedPATH)

            preProcess(seedPATH, fileName)
            fileName = "PreProcess_" + fileName

            # 生成函数签名
            retcode = subprocess.call("solc " + seedPATH + fileName + " --hashes -o " + dirPATH, shell=True)
            if(retcode == 1):
                os.remove(seedPATH + fileName)
                continue

            # 初始种子
            contractList.append(fileName)

            for f in os.listdir(dirPATH):
                if os.path.splitext(f)[1] == '.signatures':
                    sigfile = open(dirPATH + f, "r")
                    line = sigfile.read().splitlines()

                    # Step 2.遍历函数
                    for signature in line:
                        pos1 = signature.find('(')
                        pos2 = signature.find(')')
                        funcName = signature[10:pos1]

                        sig = "0x" + signature[:8]
                        dataList = signature[pos1+1:pos2].split(',')
                        # check parameter type
                        canDeal = True
                        for i, val in enumerate(dataList) :  
                            if (val.find('bool') == -1) and (val.find('uint') == -1) and (val.find('int') == -1) and (val.find('address') == -1):
                                canDeal = False
                                break
                            if (val.find('[') != -1) and (val.find(']') != -1) : # 数组
                                canDeal = False
                                break
                        if canDeal == False :
                            continue

                        inputData = generate_input.make(dataList) 
                        sigName = sig + inputData
                        print("Select contract: {}, function: {}".format(fileName, funcName))
                        print("Input data: {}".format(sigName))

                        choice = []
                        weight = {}
                        index = 0

                        # 循环50次
                        while index < 50:
                            # a = index % (len(contractList))
                            # fileName = contractList[a]

                            if index == 0:
                                pass
                            else:
                                contractList = scheduling(contractList, diff_pri, time_pri)
                            fileName = contractList[0]

                            if index == 0:
                                contract = fileName
                            else:
                                select = random.randint(1, 4)
                                select_name = ['EvenComb', 'OddComb', 'ExtremeComb', 'RandomComb']
                                print("Selected combined strategy in #iter{}: {}".format(index, select_name[select-1]))
                                weight, choice = update_weight(dirPATH, "mutator_diff", select) # combined strategy
                                shutil.copyfile(seedPATH + fileName, seedPATH + fileName.split(".sol")[0] + "_" + str(index) + ".sol" )

                                print("Combined mutators: {}".format(choice))
                                for i in range(len(choice)) :
                                    retcode = subprocess.call(
                                        "python3 " + PROJECT_DIR + "/mutators_weight.py --file " + fileName.split(".sol")[0] + "_" + str(index) + ".sol" 
                                        + " --dir " + seedPATH + " --func " + funcName + " --select " + str(choice[i]),
                                        shell=True)
                                    if retcode == 1 :
                                        continue

                                    contract = fileName.split(".sol")[0] + "_" + str(index) + ".sol"


                            # 删除bin文件夹 solc编译
                            # subprocess.call("rm -rf " + dirPATH + "bincode", shell=True)
                            print("Generating bytecode.")
                            retcode = subprocess.call("solc --bin-runtime " + seedPATH + contract + " -o " + binPATH + "bincode_" + funcName + "_" + str(index), shell=True)
                            
                            if(retcode == 1):
                                print(retcode, contract)
                                # os._exit(0)
                                os.remove(seedPATH + contract)
                                if contract in contractList :
                                    contractList.remove(contract)
                                continue
                            print("Done!")

                            # 读取bincode
                            path_list = binPATH + "bincode_" + funcName + "_" + str(index) + "/"
                            for f in os.listdir(path_list):
                                if os.path.splitext(f)[1] == '.bin-runtime':  # 判断文件后缀
                                    codefile = open(path_list + f, "r")
                            bincode = codefile.read()
                            codefile.close()
                            shutil.copyfile(seedPATH + contract, path_list + contract)


                            # 4个平台运行
                            retcode = subprocess.call(
                                "/usr/local/bin/node " + PROJECT_DIR + "/jsEVM/js_runcode.js --code " + bincode + "--sig " + sigName + " > " + outputPATH + "jsout.json",
                                shell=True)
                            if retcode == 0 :
                                print("jsevm Success!")
                            else :
                                print("jsevm Fail!")

                            retcode = subprocess.call(
                                "python3 " + PROJECT_DIR + "/py-evm/test_tx.py --data " + bincode + " --sig " + sigName + " > " + outputPATH + "pyout.json",
                                shell=True)
                            if retcode == 0 :
                                print("pyevm Success!")
                            else :
                                print("pyevm Fail!")

                            retcode = subprocess.call(
                                "./evm --debug --json --code " + bincode + " --input " + sigName[2:] + " run > " + outputPATH + "gethout.json",
                                shell=True)
                            if retcode == 0 :
                                print("geth Success!")
                            else :
                                print("geth Fail!")

                            # aleth trace
                            retcode = subprocess.call(
                                "./aleth-vm trace --code " + bincode + " --mnemonics --input " + sigName + " > " + outputPATH + "aletraceout",
                                shell=True)

                            retcode = subprocess.call(
                                "python3 " + PROJECT_DIR + "/cpp_convert_json_1.py " + outputPATH + "aletraceout " + " > " + outputPATH + "alethout.json",
                                shell=True)

                            # aleth output
                            retcode = subprocess.call(
                                "./aleth-vm stats --code " + bincode + " --mnemonics --input " + sigName + " > " + outputPATH + "aleresultout",
                                shell=True)

                            retcode = subprocess.call(
                                "python3 " + PROJECT_DIR + "/cpp_convert_json_2.py " + outputPATH + "aleresultout " + " >> " + outputPATH + "alethout.json",
                                shell=True)
                            if retcode == 0 :
                                print("aleth Success!")
                            else :
                                print("aleth Fail!")

                            # test EVM
                            tmp = ori.replace("A", bincode)
                            if need_prefix:
                                cmd = tmp.replace("B", sigName)
                            else :
                                cmd = tmp.replace("B", sigName[2:])
                            # print(cmd)
                            retcode = subprocess.call(cmd + " > " + outputPATH + "myout.json",
                                shell=True)
                            if retcode == 0 :
                                print("TestEVM Success!")
                            else :
                                print("TestEVM Fail!")

                            time.sleep(5)

                            # 比较结果 diff
                            retcode = subprocess.call(
                                "/usr/local/bin/node " + PROJECT_DIR + "/jsEVM/evmfuzz_cmp.js --js_file " 
                                + outputPATH + "jsout.json" + " --py_file " 
                                + outputPATH + "pyout.json" + " --cpp_file " 
                                + outputPATH + "gethout.json" + " --geth_file " 
                                + outputPATH + "alethout.json" + " --ret_dir "
                                + dirPATH + "newdiff" + " --txdata " + sigName + " --resfile " + dirPATH + "result" ,
                                shell=True)
                            # print("Compare diff.")
                            time.sleep(5)

                            try :
                                open(dirPATH + "newdiff", "r")
                            except :
                                os.mknod(dirPATH + "newdiff")
                            newdiffFile = open(dirPATH + "newdiff", "r")
                            if os.path.getsize(dirPATH + "newdiff") == 0:
                                newdiff = 0
                            else :
                                newdiff = int(newdiffFile.read().strip())
                            newdiffFile.close()

                            try :
                                open(dirPATH + "diff", "r")
                            except :
                                os.mknod(dirPATH + "diff")
                            diffFile = open(dirPATH + "diff", "r")
                            if os.path.getsize(dirPATH + "diff") == 0:
                                olddiff = 0
                            else :
                                olddiff = int(diffFile.read().strip())
                            diffFile.close()

                            if newdiff > olddiff:
                                # 更新diff文件
                                diffFile = open(dirPATH + "diff", "w")
                                diffFile.write(str(newdiff))
                                diffFile.close()

                                contractList.append(contract)
                                # record priority
                                diff_pri[contract] = newdiff
                                time_pri[contract] = 0

                            if index == 0 :
                                diff_pri[contract] = newdiff
                                time_pri[contract] = 0


                            # 写 diff history 文件
                            if index == 0:
                                diffhistory = open(dirPATH + "diffHis", "a")
                                diffhistory.write(contract + "_" + "first" + "_" + str(newdiff).strip() + '\n')
                                # write mutator weight
                                diffhistory.write(str(weight) + '\n')
                                diffhistory.close()
                            else:
                                diffhistory = open(dirPATH + "diffHis", "a")
                                diffhistory.write(contract + "_" + str(choice) + "_" + str(newdiff).strip() + '\n')
                                # write mutator weight
                                diffhistory.write(str(weight) + '\n')
                                diffhistory.close()
                            # print("Update contract diff.")


                            # 写 mutator_diff 文件
                            if index == 0:
                                mutatordiffFile = open(dirPATH + "mutator_diff", "w")
                                for i in range(1, 9):
                                    mutatordiffFile.write(str(newdiff).strip()+'\n')
                                mutatordiffFile.close()
                            else:
                                for i in range(len(choice)):
                                    editLine(dirPATH, "mutator_diff", choice[i]-1, str(newdiff).strip()+'\n')
                                # mutatordiffFile = open(dirPATH + "mutator_diff", "w")
                                # for i in range(1, 6):
                                #     if choice==i:
                                #         mutatordiffFile.write(str(newdiff).strip() + '\n')
                                # mutatordiffFile.close()
                            # print("Update mutator diff.")

                            # record Testing result
                            print("Collecting information.")
                            jsFile = open(outputPATH + "jsout.json", 'r', encoding='utf-8')
                            pyFile = open(outputPATH + "pyout.json", 'r', encoding='utf-8')
                            gethFile = open(outputPATH + "gethout.json", 'r', encoding='utf-8')
                            alethFile = open(outputPATH + "alethout.json", 'r', encoding='utf-8')
                            myFile = open(outputPATH + "myout.json", 'r', encoding='utf-8')

                            js_output, py_output, geth_output, aleth_output, my_output = "", "", "", "", ""
                            js_gas, py_gas, geth_gas, aleth_gas, my_gas = 0, 0, 0, 0, 0
                            js_op, py_op, geth_op, aleth_op, my_op = 0, 0, 0, 0, 0

                            for line in jsFile.readlines():
                                if line.find("output") >= 0 :
                                    dic = json.loads(line)
                                    js_output = dic['output']
                                    js_gas = int(dic['gasUsed'], 16)
                                else:
                                    js_op += 1
                            jsFile.close()

                            for line in pyFile.readlines():
                                if line.find("output") >= 0 :
                                    dic = json.loads(line)
                                    py_output = dic['output']
                                    py_gas = int(dic['gasUsed'], 16)
                                else:
                                    py_op += 1
                            pyFile.close()

                            for line in gethFile.readlines():
                                if line.find("output") >= 0 :
                                    dic = json.loads(line)
                                    geth_output = dic['output']
                                    geth_gas = int(dic['gasUsed'], 16)
                                else:
                                    geth_op += 1
                            gethFile.close()

                            for line in alethFile.readlines():
                                if line.find("output") >= 0 :
                                    dic = json.loads(line)
                                    aleth_output = dic['output']
                                    aleth_gas = int(dic['gasUsed'], 16)
                                else:
                                    aleth_op += 1
                            alethFile.close()

                            for line in myFile.readlines():
                                if line.find("output") >= 0 :
                                    dic = json.loads(line)
                                    my_output = dic['output']
                                    my_gas = int(dic['gasUsed'], 16)
                                else:
                                    my_op += 1
                            myFile.close()

                            # compare and count
                            avg_gas = int((js_gas + py_gas + geth_gas + aleth_gas) / 4)
                            avg_op = int((js_op + py_op + geth_op + aleth_op) / 4)
                            # output
                            if (my_output != js_output) and (my_output != py_output) and (my_output != geth_output) and (my_output != aleth_output):
                                X1 += 1
                            # gasUsed
                            if my_gas > int(1.3 * avg_gas) :
                                X2 += 1
                            elif my_gas < int(0.8 * avg_gas) :
                                X3 += 1
                            else :
                                X4 += 1
                            # opcode sequence
                            if my_op > int(1.55 * avg_op) :
                                X5 += 1
                            elif my_op < int(1.45 * avg_op) :
                                X6 += 1
                            else :
                                X7 += 1
                            print("Done!")
                            
                            index += 1
                            totalVarient += 1
    

def send_report(time1, time2):
    """
    Show final report
    """
    # print(totalVarient, X1, X2, X3, X4, X5, X6, X7)
    title = "Detection Report"
    print(fmt(color.YELLOW, title.center(os.get_terminal_size().columns)))

    if totalVarient == 0:
        print("ERROR! Exception occurs and no work done.")
        return 0
    
    per1 = round((100.0 * X1 / totalVarient), 2)
    per2 = round((100.0 * X2 / totalVarient), 2)
    per3 = round((100.0 * X3 / totalVarient), 2)
    per4 = round((100.0 * X4 / totalVarient), 2)
    per5 = round((100.0 * X5 / totalVarient), 2)
    per6 = round((100.0 * X6 / totalVarient), 2)
    per7 = round((100.0 * X7 / totalVarient), 2)
    
    print("\nAfter {:.2f}s running, EVMFuzzer successfully generated {} seeds.".format((time2-time1), totalVarient))
    print("   > In ", end='')
    print(fmt(color.RED, str(per1)+'%'), end='')
    print(" ({}/{}) of the tests, the output results are different from the standard execution.".format(X1, totalVarient))

    print("   > In ", end='')
    print(fmt(color.RED, str(per2)+'%'), end='')
    print(" ({}/{}) of the tests, the gas consuming are more than the average value.".format(X2, totalVarient))

    print("   > In ", end='')
    print(fmt(color.RED, str(per3)+'%'), end='')
    print(" ({}/{}) of the tests, the gas consuming are less than the average value.".format(X3, totalVarient))

    print("   > In ", end='')
    print(fmt(color.RED, str(per4)+'%'), end='')
    print(" ({}/{}) of the tests, the gas consuming are equal to the average value.".format(X4, totalVarient))

    print("   > In ", end='')
    print(fmt(color.RED, str(per5)+'%'), end='')
    print(" ({}/{}) of the tests, the execution sequence are more than the average value.".format(X5, totalVarient))

    print("   > In ", end='')
    print(fmt(color.RED, str(per6)+'%'), end='')
    print(" ({}/{}) of the tests, the execution sequence are less than the average value.".format(X6, totalVarient))

    print("   > In ", end='')
    print(fmt(color.RED, str(per7)+'%'), end='')
    print(" ({}/{}) of the tests, the execution sequence are equal to the average value.".format(X7, totalVarient))

    # make conclusion
    print("\nFinal Conslusion:")
    if per1 < 1.0 :
        print(fmt(color.YELLOW, "1. The code implementation of test EVM is relatively complete, can be used for Ethereum."))
    else :
        print(fmt(color.YELLOW, "1. The code implementation of test EVM is incomplete, cannot be used for Ethereum."))
    if per3 <= 50.0 and per2 <= 50:
        print(fmt(color.YELLOW, "2. The calculation of gas is accurate, "), end='')
    else :
        print(fmt(color.YELLOW, "2. The deviation of gas calculation is large, "), end='')
    if per3 > 0.0 :
        print(fmt(color.YELLOW, "there exists dynamic optimization during the calculation process, "), end='')
    else :
        print(fmt(color.YELLOW, "there is no dynamic optimization during the calculation process, "), end='')
    if per3 > per2 :
        print(fmt(color.YELLOW, "and the optimization effect is good."))
    else :
        print(fmt(color.YELLOW, "which need further improvement."))

    if per6 <= 50.0 and per5 <= 50:
        print(fmt(color.YELLOW, "3. The execution path planning is correct, "), end='')
    else :
        print(fmt(color.YELLOW, "3. The deviation of executing sequence is large, "), end='')
    if per6 > 0.0 :
        print(fmt(color.YELLOW, "there exists dynamic optimization during the executing procedure, "), end='')
    else :
        print(fmt(color.YELLOW, "there is no dynamic optimization during the executing procedure, "), end='')
    if per6 > per5 :
        print(fmt(color.YELLOW, "and the optimization effect is good."))
    else :
        print(fmt(color.YELLOW, "which need further improvement."))


if __name__ == '__main__':
    show_help()
    start_time = time.time()
    main()
    end_time = time.time()
    send_report(start_time, end_time)
