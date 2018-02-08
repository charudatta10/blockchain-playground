#include <iostream>
#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <vector>
#include <algorithm>

using namespace std;



bool IsOperation(string &line) {
    return isdigit(line[0]); //return line[0] >= '0' && line[0] <= '9';
}

/***
    parse the operation in to two range and an operator
    exp := <range><op><range>
    <range> := <number> | <number>,<number>
***/
void ParseOperation(string &line, int *range, char &op) {
    int index = 0;
    for (int i = 0; i < line.length();) {
        int num = 0;
        while (isdigit(line[i])) {
            num = num * 10 + (line[i++] - '0');
        }
        range[index++] = num; 
        if (line[i] == ',') {
            i++;
        } else {
            if (index % 2) {
                range[index] = range[index - 1];
                ++index;
            }
            op =  (line[i] >= 'a' && line[i] <= 'z') ? line[i++] : op;
        }
    }
    // cout<<line<<" "<<range[0]<<" "<<range[1]<<" "<<range[2]<<" "<<range[3]<<" "<<op<<endl;
}

void GetBlock (ifstream &diff_file, vector<string> &block) {
    string line;
    while (diff_file.peek()!= -1 && !isdigit(diff_file.peek())) {
        getline(diff_file,line);
        if (line[0] == '<' || line[0] == '-') {
            continue;
        }
        block.push_back(line.substr(2));
    }
    // for (int i = 0; i < block.size(); i++) {
    //     cout<<block[i]<<endl;
    // }
}

/*
    Add block of content to target_file;
*/

void Addlines(ofstream &target_file, vector<string> &block) {
    int size = block.size();
    for (int i = 0; i < size; i++) {
        target_file<<block[i]<<endl;
    }
}


/*
    Is better to skip number of lines.
*/
void Deletelines(ifstream &source_file, int num_lines) {
    string line;
    for (int i = 0; i < num_lines; i++) {
        getline(source_file, line);
    }
}



/*
    Write content to target file.

    a:= <number>a<range>
        copy content from pre_last_pos ~ leftrange to traget file
        add content after origin ranger : new pos from leftrange_l + 1

    d:=<range>d<range>
        copy content from pre_last_pos ~ leftrange - 1 to traget file
        delete content of origin range : leftrange_l ~ leftrange_r

    c:=<range>c<range>
        copy content from pre_last_pos ~ leftrange - 1 to traget file
        delete content of origin range : leftrange_l ~ leftrange_r
        add new content

*/
bool WriteTargetFile(ifstream &source_file, ofstream &target_file, int &source_pos, 
                    int *range, char &op, vector<string> &block) {
    string line;
    while(source_file.peek() != -1 && source_pos <= range[0]) {
        if (source_pos == range[0] && (op != 'a')) {
            break;
        }
        getline(source_file, line);
        target_file<<line<<endl;
        source_pos++;
    }
    int size;
    if (op == 'a') {
        Addlines(target_file, block);
    } else if (op == 'd') {
        Deletelines(source_file, range[1] - range[0] + 1);
        source_pos += range[1] - range[0] + 1;
    } else if (op == 'c') {
        Deletelines(source_file, range[1] - range[0] + 1);
        source_pos = range[1] + 1;
        Addlines(target_file, block);
    } else {
        cout<<"error : illegal operator."<<endl;
        return false;
    }
    return true;
}

void WriteLast(ifstream &source_file, ofstream &target_file) {
    string line;
    while (source_file.peek() != -1) {
        getline(source_file, line);
        target_file<<line<<endl;
    }
}

int main()
{
    
    ifstream source_file, diff_file;
    ofstream target_file;
    string line;
    vector<string> block;
    int source_pos, offset, same_file_num, total_case_num;
    int range[4];
    char op = 0;

    same_file_num = 0, total_case_num = 200;

    for (int i = 1; i <= total_case_num; i++) {
        target_file.open(string("./testcase/case") + to_string(i) + string("_target.txt"));
        source_file.open(string("./testcase/case") + to_string(i) + string("_1.txt"));
        diff_file.open(string("./testcase/case") + to_string(i) + string("_diff.txt"));
        
        source_pos = 1;
        while (!diff_file.eof()) {
            getline(diff_file,line);
            if (IsOperation(line)) {
                ParseOperation(line, range, op);
                GetBlock(diff_file, block);
                WriteTargetFile(source_file, target_file, source_pos, range, op, block);
            } else {
                break;
            }
            block.clear();
            memset(range, -1, sizeof(range));
        }
        WriteLast(source_file, target_file);

        diff_file.close();
        source_file.close();
        target_file.close();


        
        string cmd = "diff ";
        cmd += string("./testcase/case") + to_string(i) + string("_target.txt ");
        cmd += string("./testcase/case") + to_string(i) + string("_2.txt");
        if(system (cmd.c_str()) == 0) {
            ++same_file_num;
        } else {
            cout<<"error: file"<<i<<endl;
        }

    }
    printf("%d / %d\n", same_file_num, 200);

    return 0;
}