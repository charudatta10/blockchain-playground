from diffparser import DiffParser


# test code
import os
import random
import subprocess
import copy


def dice():
    return random.randint(1, 6)


def random_line():
    ret = ''.join([chr(ord('a') + random.randint(0, 25)) for _ in range(random.randint(5, 15))])
    ret += "\n"
    return ret


def store_badcase(source, target, lines, diff_path, id):
    with open("case_%d_source.txt"%id, 'w') as f:
        f.writelines(source)
    with open("case_%d_target.txt"%id, 'w') as f:
        f.writelines(target)
    with open("case_%d_output.txt"%id, 'w') as f:
        f.writelines(lines)
    p = subprocess.Popen("cp %s case_%d_diff.txt"%(diff_path, id))
    p.wait()



def run_one_test(id = 0):
    src_file = 'source.txt'
    tar_file = 'target.txt'
    gen_file = 'generate.txt'
    diff_file = 'diff.txt'

    source = []
    for i in range(100):
        source.append(random_line())
    with open(src_file, 'w') as f:
        f.writelines(source)
    
    target = copy.copy(source)
    for i in range(20):
        d = dice()
        if d == 1:
            idx = random.randint(0, len(target)-1)
            target.remove(target[idx])
        elif d == 2:
            idx = random.randint(0, len(target)-1)
            target.insert(idx, random_line())
        elif d == 3:
            idx = random.randint(0, len(target)-1)
            target[idx] = random_line()
    
    with open(tar_file, 'w') as f:
        f.writelines(target)

    # generate correct diff result
    with open(diff_file, 'w') as f:
        p = subprocess.Popen("diff %s %s"%(src_file, tar_file), stdout=f)
        p.wait()

    # generate result
    with open(src_file, 'r') as f:
        source = f.readlines()
    with open(diff_file, 'r') as f:
        diff = f.readlines()

    parser = DiffParser()
    lines = parser.Parse(source, diff)
    with open(gen_file, 'w') as f:
        f.writelines(lines)
    with open(tar_file, 'r') as f:
        target = f.readlines()

    # compare correct result and generated result
    if len(target) != len(lines):
        store_badcase(source, target, lines, diff_file, id)
        return False
    
    for i in range(len(target)):
        if target[i] != lines[i]:
            store_badcase(source, target, lines, diff_file, id)
            return False
    
    return True
    

n_correct = 0
n_testcase = 200
for i in range(n_testcase):
    if run_one_test(id = i+1):
        n_correct += 1

print "# correct parsed:", n_correct, "/", n_testcase