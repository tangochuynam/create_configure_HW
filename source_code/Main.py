from jinja2 import Environment, FileSystemLoader
import datetime
import re
import os


class Main:

    def __init__(self):
        self.path_input_txt = 'input'
        self.path_input_template = 'template'
        self.path_output = 'output'
        self.template_file = 'hw_command.txt'
        self.file_txt = 'LDG03THA_CLI_input.txt'
        self.hostname = ''

    def main(self):
        pttr_split_command = '(?:<[\S]+>)display .*\n(?:(?!(?:<[\S]+>)display).*\n)*'
        file_string = self.read_file()
        if len(file_string) == 0:
            raise ValueError(self.file_txt + " does not exist")
        else:
            self.hostname = self.file_txt.split('.txt')[0]
            # handle file and get information
            # split into 5 parts
            part_1, part_2, part_3, part_4, part_5 = re.findall(pttr_split_command, file_string, flags=re.MULTILINE)
            lst_tunnel = self.get_list_tunnel(part_1)
            lst_int = self.get_list_interface(part_2)
            lst_vsi = self.get_list_vsi(part_3)
            lst_vpn = self.get_list_vpn(part_4)
            lst_vlan = self.get_list_vlan(part_5)
            self.writefile(lst_tunnel, lst_int, lst_vsi, lst_vpn, lst_vlan)

    def get_list_tunnel(self, part_1):
        pttr = 'Tunnel.*\n'
        lst_temp = re.findall(pttr, part_1, flags=re.MULTILINE)
        lst_tunnel = list(map(lambda x: x.split()[0].strip(), lst_temp))
        # print(lst_tunnel)
        return lst_tunnel

    def get_list_interface(self, part_2):
        pttr = '\s+(?:\*Client Interface).*\n'
        lst_temp = re.findall(pttr, part_2, flags=re.MULTILINE)
        lst_interface = list(map(lambda x: x.split(':')[1].strip(), lst_temp))
        #print(lst_interface)
        return lst_interface

    def get_list_vsi(self, part_3):
        pttr = '(?:\S+\s+){4}vlan\s+.*\n'
        lst_temp = re.findall(pttr, part_3, flags=re.MULTILINE)
        lst_vsi =list(map(lambda x: x.split()[0].strip() , lst_temp))
        #print(lst_vsi)
        return lst_vsi

    def get_list_vpn(self, part_4):
        pttr = '.*ipv4.*\n'
        lst_temp = re.findall(pttr, part_4, flags=re.MULTILINE)
        lst_vpn = list(map(lambda x: x.split()[0].strip(), lst_temp))
        #print(lst_vpn)
        return lst_vpn

    def get_list_vlan(self, part_5):
        pttr = '\s+Interface list.*\n'
        lst_temp = re.findall(pttr, part_5, flags=re.MULTILINE)
        #print(len(lst_temp))
        vlan = lst_temp[0].split(':')[1]
        # for now this line have one Vlanif - maybe in the future they have multiple value
        lst_vlan = [vlan.split('Vlanif')[1].strip()]
        #print(lst_vlan)
        return lst_vlan

    def read_file(self):
        filename = self.path_input_txt + '/' + self.file_txt
        if os.path.isfile(filename):
            with open(filename, 'r') as data_file:
                return data_file.read()
        else:
            return ""

    def writefile(self, lst_tunnel, lst_int, lst_vsi, lst_vpn, lst_vlan):
        template_env = Environment(autoescape=False, loader=FileSystemLoader(self.path_input_template), trim_blocks=False)
        hw_command = {'lst_tunnel': lst_tunnel,
                      'lst_int': lst_int,
                      'lst_vsi': lst_vsi,
                      'lst_vpn': lst_vpn,
                      'lst_vlan': lst_vlan}
        file_ouput = self.path_output + "/" + 'HW_Command-' + self.hostname + '-'.join(str(datetime.datetime.now()).split(":")) + ".txt"
        with open(file_ouput, 'w') as f:
            f_txt = template_env.get_template(self.template_file).render(hw_command)
            f.write(f_txt)
        print("write successful")


Main().main()