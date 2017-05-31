"""
HWC - Hardware Capabilities
Process module and a wrapper around common Linux commands to check hardware information:
- lscpu
- lspci
- lshw
- lsusb
- parsed /proc/cpuinfo file
"""

import json
import re
from subprocess import check_output

from constants import *
from process_modules.process_modules_templates import RESTRequestProcessModule


class HWCRESTRequestProcessModule(RESTRequestProcessModule):

    def process_get_request(self, http_handler):
        if HAL_HWC_GET_LSCPU_INFO_PATH in http_handler.path:
            response = self.get_lscpu_info()
        elif HAL_HWC_GET_LSPCI_INFO_PATH in http_handler.path:
            response = self.get_lspci_info()
        elif HAL_HWC_GET_CPU_INFO_PATH in http_handler.path:
            response = self.get_proc_cpu_info_info()
        elif HAL_HWC_GET_LSHW_INFO_PATH in http_handler.path:
            response = self.get_lshw_info()
        elif HAL_HWC_GET_LSUSB_INFO_PATH in http_handler.path:
            response = self.get_lsusb_info()
        else:
            http_handler.send_error_response('This url is not supported: ' + http_handler.path)
        http_handler.send_ok_response(json.dumps(response))
        return

    @staticmethod
    def _run_cmd(cmd):
        return check_output(cmd)

    @staticmethod
    def get_lsusb_info():
        result = HWCRESTRequestProcessModule._run_cmd(LSUSB_CMD)
        processed_result = []
        lines = result.splitlines()
        for line in lines:
            tokens = line.split()
            if len(tokens) < 7:
                print('Not enough info.')
            else:
                id_tokens = tokens[5].split(b':')
                name = b' '.join(tokens[6:])
                element = {
                    HAL_LSUSB_BUS_NUMBER_PROPERTY_NAME: tokens[1],
                    HAL_LSUSB_DEVICE_NUMBER_PROPERTY_NAME: tokens[3][:-1],
                    HAL_LSUSB_MANUFACTURE_ID_PROPERTY_NAME: id_tokens[0],
                    HAL_LSUSB_DEVICE_ID_PROPERTY_NAME: id_tokens[1],
                    HAL_LSUSB_MANUFACTURE_AND_DEVICE_NAME_PROPERTY_NAME: name
                }
                processed_result.append(element)
        return processed_result

    @staticmethod
    def get_lscpu_info():
        result = HWCRESTRequestProcessModule._run_cmd(LSCPU_CMD)
        processed_result = {}
        lines = result.splitlines()
        for line in lines:
            tokens = line.split(b':')
            if len(tokens) >= 2:
                property_name = tokens[0].replace(b' ', b'_').replace(b'-', b'_')\
                    .replace(b'(', b'').replace(b')', b'').lower()
                processed_result[property_name] = tokens[1].strip()
        return processed_result

    @staticmethod
    def get_proc_cpu_info_info():
        result = HWCRESTRequestProcessModule._run_cmd(CPU_INFO_CMD)
        processed_result = []
        result = result.replace(b'\t', b'')
        tokens = result.strip(b'\t').split(b'processor')
        for token in tokens:
            if len(token) != 0:
                processor_info = {}
                properties = token.splitlines()
                for property_line in properties:
                    if len(property_line) != 0:
                        property_tokens = property_line.split(b':')
                        if len(property_tokens) == 2:
                            if len(property_tokens[0]) == 0:
                                property_name = b'processor_number'
                            else:
                                property_name = property_tokens[0].replace(b' ', b'_')
                            processor_info[property_name] = property_tokens[1]
                processed_result.append(processor_info)
        return processed_result

    @staticmethod
    def get_lspci_info():
        result = HWCRESTRequestProcessModule._run_cmd(LSPCI_CMD)
        processed_result = []
        lines = result.splitlines()
        for line in lines:
            tokens = line.split(b'"')
            if len(tokens) >= 10:
                element = {}
                numbers = re.findall(b'\d+', tokens[0])
                if len(numbers) == 3:
                    element[HAL_LSPCI_BUS_NUMBER_PROPERTY_NAME] = numbers[0]
                    element[HAL_LSPCI_DEVICE_NUMBER_PROPERTY_NAME] = numbers[1]
                    element[HAL_LSPCI_FUNCTION_NUMBER_PROPERTY_NAME] = numbers[2]
                class_props = tokens[1].split(b'[')
                if len(class_props) == 2:
                    element[HAL_LSPCI_DEVICE_CLASS_PROPERTY_NAME] = class_props[0]
                    element[HAL_LSPCI_DEVICE_CLASS_ID_PROPERTY_NAME] = class_props[1][:-1]
                vendor_props = tokens[3].split(b'[')
                if len(vendor_props) == 2:
                    element[HAL_LSPCI_DEVICE_VENDOR_PROPERTY_NAME] = vendor_props[0]
                    element[HAL_LSPCI_DEVICE_VENDOR_ID_PROPERTY_NAME] = vendor_props[1][:-1]
                device_props = tokens[5].split(b'[')
                if len(device_props) == 2:
                    element[HAL_LSPCI_DEVICE_NAME_PROPERTY_NAME] = device_props[0]
                    element[HAL_LSPCI_DEVICE_ID_PROPERTY_NAME] = device_props[1][:-1]
                element[HAL_LSPCI_REVISION_NUMBER_PROPERTY_NAME] = tokens[9][2:]
                processed_result.append(element)
        return processed_result

    @staticmethod
    def get_lshw_info():
        result = HWCRESTRequestProcessModule._run_cmd(LSHW_CMD)
        return ''
