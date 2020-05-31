from jinja2 import Environment, FileSystemLoader
import datetime
import re
import os
from pathlib import Path


class Main:
    base = Path(__file__).parent.parent

    def __init__(self):
        self.path_output = Main.base.joinpath('output')
        self.path_template = Main.base.joinpath('template')
        self.template_file = 'hw_command.txt'
        self.path_input = Main.base.joinpath('input')
        self.file_txt = 'LDG03THA_CLI_input.txt'
        self.hostname = self.file_txt.split('.txt')[0]

    def main(self):
        pttr_split_command = '(?:<[\S]+>)display .*\n(?:(?!(?:<[\S]+>)display).*\n)*'
        # this is for other people use - for local please use # to block it
        #self.get_file_from_user()
        lst_file = os.listdir(self.path_input)
        for filename in lst_file:
            print(filename)
            path_file = self.path_input.joinpath(filename)
            self.hostname = filename.split('.txt')[0]
            file_string = self.read_file(path_file)
            # handle file and get information
            # split into 5 parts
            part_1, part_2, part_3, part_4, part_5 = re.findall(pttr_split_command, file_string, flags=re.MULTILINE)
            lst_tunnel = self.get_list_tunnel(part_1)
            lst_int = self.get_list_interface(part_2)
            lst_vsi = self.get_list_vsi(part_3)
            lst_vpn = self.get_list_vpn(part_4)
            lst_vlan = self.get_list_vlan(part_5)
            self.writefile(lst_tunnel, lst_int, lst_vsi, lst_vpn, lst_vlan)

    @staticmethod
    def get_list_tunnel(part_1):
        pttr = 'Tunnel.*\n'
        lst_temp = re.findall(pttr, part_1, flags=re.MULTILINE)
        lst_tunnel = list(map(lambda x: x.split()[0].strip(), lst_temp))
        # print(lst_tunnel)
        return lst_tunnel

    @staticmethod
    def get_list_interface(part_2):
        pttr = '\s+(?:\*Client Interface).*\n'
        lst_temp = re.findall(pttr, part_2, flags=re.MULTILINE)
        lst_interface = list(map(lambda x: x.split(':')[1].strip(), lst_temp))
        #print(lst_interface)
        return lst_interface

    @staticmethod
    def get_list_vsi(part_3):
        pttr = '(?:\S+\s+){4}vlan\s+.*\n'
        lst_temp = re.findall(pttr, part_3, flags=re.MULTILINE)
        lst_vsi =list(map(lambda x: x.split()[0].strip() , lst_temp))
        #print(lst_vsi)
        return lst_vsi

    @staticmethod
    def get_list_vpn(part_4):
        pttr = '.*ipv4.*\n'
        lst_temp = re.findall(pttr, part_4, flags=re.MULTILINE)
        lst_vpn = list(map(lambda x: x.split()[0].strip(), lst_temp))
        #print(lst_vpn)
        return lst_vpn

    @staticmethod
    def get_list_vlan(part_5):
        pttr = '\s+Interface list.*\n(?:.*\n)*'
        lst_temp = re.findall(pttr, part_5, flags=re.MULTILINE)
        lst_vlan = []

        if len(lst_temp) > 0:
            lst_line = lst_temp[0].splitlines()
            # remove '' element
            for line in lst_line:
                if line.strip() == '':
                    lst_line.remove(line)
            #print(len(lst_line))
            for i in range(0, len(lst_line)):
                first_element = lst_line[i].split(',')[0].strip()
                if i == 0:
                    vlan = first_element.split(':')[1].strip()
                else:
                    vlan = first_element
                #print('vlan: ' + vlan)
                if vlan != '':
                    # for now this line have one Vlanif - maybe in the future they have multiple value
                    if vlan.startswith('Vlanif'):
                        lst_vlan.append(vlan.split('Vlanif')[1].strip())
                    else:
                        lst_vlan.append(vlan)
                #print(lst_vlan)
        #print(lst_vlan)
        return lst_vlan

    @staticmethod
    def read_file(path_file):
        if os.path.isfile(path_file):
            with open(path_file, 'r') as data_file:
                return data_file.read()
        else:
            raise ValueError(f"file: {path_file}")

    def writefile(self, lst_tunnel, lst_int, lst_vsi, lst_vpn, lst_vlan):
        template_env = Environment(autoescape=False, loader=FileSystemLoader(self.path_template), trim_blocks=False)
        hw_command = {'lst_tunnel': lst_tunnel,
                      'lst_int': lst_int,
                      'lst_vsi': lst_vsi,
                      'lst_vpn': lst_vpn,
                      'lst_vlan': lst_vlan}
        file_ouput = self.path_output.joinpath('HW_Command-' + self.hostname + '-' + '-'.join(str(datetime.datetime.now()).split(":")) + ".txt")
        with open(file_ouput, 'w') as f:
            f_txt = template_env.get_template(self.template_file).render(hw_command)
            f.write(f_txt)
        print("create file successful")

    def get_file_from_user(self):
        if os.name == 'nt':
            self.slash = '\\'
        flag = True
        while flag:
            #print('FIRST: enter the directory, SECOND: enter name of file.txt: ')
            path = input("Enter directory: ")
            flag = False
            self.path_file_txt = path
            self.path_output = path


if __name__ == '__main__':
    Main().main()
