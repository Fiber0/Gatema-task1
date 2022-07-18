import os


def xy_evaluator(line_contents_str):  # used for getting value of X and Y from machine(CNC) command

    f = line_contents_str[0]
    if line_contents_str[0] == 'X':
        # used to detect, which axis is specified first
        last_axis = 'Y'
    else:
        last_axis = 'X'
    # code below modifies the machine(CNC) command into an executable string, for instance this command: X93.350Y116.850T01
    # will be modified to: X=93.350;Y=116.850#T01 and executed -> setting the value of X and Y
    line_contents_str = line_contents_str.replace(f, f'{f}=')
    line_contents_str = line_contents_str.replace(last_axis, f';{last_axis}=')
    if line_contents_str.find('T') != -1:
        line_contents_str = line_contents_str.replace('T', '#T')

    exec(line_contents_str, globals())
    return X, Y

    # (time complexity: O(1))


def function1(filename):
    partition_dict = {}  # later used to store all machine types(keys) and their commands(contents)
    # (quite memory inefficient, but quite good for sorting blocks of lines, this method also doesn't require fixed or completed(you can skip names - T01, T02, T04) ammount of CNC machines specified)
    print('processing: #', end='')
    last_key = 0
    file1 = open(filename, 'r+')
    all_lines = file1.readlines()  # stores all document lines inside variable (even more memory consuming, but other methods 
    #(such as storing the block of CNC commands or only one line at a time) will require much more computation power due to constant iterating through lines of file1)

    try:
        print(' #', end='')
        block_start = current_line_idx = all_lines.index('(M47, Zacatek bloku vrtani)\n') + 2

        while all_lines[current_line_idx + 3] != '(M47, Konec bloku vrtani)\n':

            current_line_str = all_lines[current_line_idx]
            xy_evaluator(current_line_str)

            if X > 50:
                current_line_str = current_line_str.replace(f'{Y}', f'{Y + 10}')  # replaces current value of Y by Y+ 10

            if current_line_str.find('T') != -1:  # if command contains T (new nachine)
                last_key = current_line_str[-3: -1]
                partition_dict[last_key] = current_line_str  # makes new key-value-pair
            else:
                partition_dict[last_key] += current_line_str  # store command inside dict under last key(machine name)

            current_line_idx += 1
        print(' #', end='')
        # cnc.txt - structuring ˇ
        script_path = os.path.dirname(os.path.realpath(__file__))  # gets location of this script
        new_file = open(rf'{script_path}\cnc.txt', 'w')
        doc_head = all_lines[: block_start]  # defines all lines from top to machine commands

        for o in doc_head:
            new_file.write(o)

        sorted_machines_list = sorted(partition_dict.keys())
        print(' #', end='\n')
        # sorts all partition keys and writes their values into new document in ascending order
        for p in sorted_machines_list:
            for a in partition_dict.get(p):
                new_file.write(a)

        doc_bottom = all_lines[all_lines.index('(M47, Konec bloku vrtani)\n')-3:]
        # defines part of document, which is located below machine commands
        for s in doc_bottom:
            new_file.write(s)
        print('..done')
    except ValueError:
        exit('! start or end of machine command block not found ! make sure you have marked it with:'
             ' (M47, Zacatek bloku vrtani) and end with: (M47, Konec bloku vrtani)')

    except KeyError:
        print('! first machine command is not marked with machine name or is invalid ! make sure it meets this format:'
              "'{CNC command}T01'")
    except Exception:
        print('! unexpected error happened ! make sure the specified files structure is expected')

    # (time complexity: O(n^2))


def funkce2(filename):
    try:
        file1 = open(filename, 'r')
        all_lines = file1.readlines()
        block_start = all_lines.index('(M47, Zacatek bloku vrtani)\n') + 2
        block_end = all_lines.index('(M47, Konec bloku vrtani)\n') - 3
        comm_block = all_lines[block_start: block_end]

        xy_evaluator(comm_block[0])
        sx_bx_ay_bx = [X, X, Y, Y]  # defines list storing both largest and smallest X and Y values
        for d in comm_block[1:]:

            xy_evaluator(d)
            if X < sx_bx_ay_bx[0]:
                sx_bx_ay_bx[0] = X
            elif X > sx_bx_ay_bx[1]:
                sx_bx_ay_bx[1] = X

            if Y < sx_bx_ay_bx[2]:
                sx_bx_ay_bx[2] = Y
            elif Y > sx_bx_ay_bx[3]:
                sx_bx_ay_bx[3] = Y
        return f'\nnejmenší hodnota X: {sx_bx_ay_bx[0]}\nnejvětší hodnota X: {sx_bx_ay_bx[1]}\n' \
               f'nejmenší hodnota Y: {sx_bx_ay_bx[2]}\nnejvětší hodnota Y: {sx_bx_ay_bx[3]}\n'
    except ValueError:

        exit('! start or end of machine command block not found ! make sure you have marked it with: '
             '(M47, Zacatek bloku vrtani) and end with: (M47, Konec bloku vrtani)')
    except Exception:
        print('! unexpected error ! make sure the specified files structure is expected')

    # (time complexity: O(n))


if __name__ == '__main__':
    while True:
        command = input('enter command: ')
        if command == 'exit' or command == 'quit':
            exit()
        elif command[:5] == 'start':
            try:
                path = input('enter file path: ')
                if command[6:] == 'f1':
                    function1(path)
                elif command[6:] == 'f2':
                    print(funkce2(path))
            except FileNotFoundError:
                print('! invalid directory or file !')

        elif command == 'help':
            print('\n-exit- quits the program\n'
                  '-start {function}- executes chosen function:\nf1- function 1(increases Y and sorts blocks of txt)\n'
                  'f2 - function 2(prints both largest and smallest X and Y values). usage example: start f2\n')
        else:
            print("invalid command type 'help' for help")

            
# if something didn't work right or something could work better, feel free to contact me or start a pull request
