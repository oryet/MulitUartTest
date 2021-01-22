#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2020-3-5 13:12:16

@author: jiagnzy
"""

import sys

sys.path.append('../')
import threading
import time
import queue
import datetime
from PublicLib.SerialModule.simSerial import simSerial
import logging

logger = logging.getLogger('MulitUTMain')


class UartTest():
    def addspace(self, frame):
        # 字节间增加空格
        framespace = ''
        for i in range(0, len(frame), 2):
            framespace += frame[i:i + 2] + ' '
        return framespace


    def uart_send(self, q, ss, ser, cfgparm, cfgdata):
        logger = logging.getLogger('uart_send')

        senddelayinit = cfgdata['timeout'] / 0.01
        senddelay = senddelayinit
        sfe = cfgdata['send'][0].replace(' ', '')

        if cfgdata['autoresp'] == 1:
            cfgdata['sendcnt'] = 0

        while 1:
            time.sleep(0.01)
            if senddelay >= 0:
                senddelay -= 1
            else:
                senddelay = senddelayinit
                if cfgdata['sendcnt'] > 0 or cfgdata['autoresp'] == 1:
                    fe = self.addspace(sfe)
                    ss.onSendData(ser, fe, 'hex')

                    # 打印 或 日志记录
                    # print(datetime.datetime.now(), cfgparm['port'], 'Send:', sfe)
                    lg = str(datetime.datetime.now()) + '  ' + cfgparm['port'] + '  ' + 'Send:' + sfe
                    logger.info(lg)

                    cfgdata['sendbytecnt'] += (len(sfe) / 2)
                    if cfgdata['autoresp'] == 0:
                        cfgdata['sendcnt'] -= 1
                    else:
                        cfgdata['sendcnt'] += 1
                elif cfgdata['sendcnt'] == 0:
                    lg = str(datetime.datetime.now()) + '  ' + cfgparm['port']  + '  ' + str(cfgdata['sendcnt']) + ',' + str(
                        cfgdata['sendbytecnt']) + ',' + str(cfgdata['recvcnt']) + ',' + str(cfgdata['recvbytecnt'])
                    logger.info(lg)
                    cfgdata['sendcnt'] -= 1


            if not q.empty():
                rfe = q.get()
                lg = str(datetime.datetime.now()) + '  ' + cfgparm['port'] + '  ' + 'Recv:' + rfe
                logger.info(lg)

                cfgdata['recvcnt'] += 1
                cfgdata['recvbytecnt'] += (len(rfe) / 2)


    def uart_test(self, cfgparm, cfgdata):
        logger = logging.getLogger(__name__)

        # 创建 模拟表串口
        ss = simSerial()
        q = queue.Queue()
        openret, ser = ss.DOpenPort(cfgparm['port'], cfgparm['baud'])
        if openret:
            threading.Thread(target=self.uart_send, args=(q, ss, ser, cfgparm, cfgdata)).start()

        while openret:
            str = ss.DReadPort()  # 读串口数据
            # 协议判断 或 帧长度判断
            if len(str) > 10:
                q.put(str)


if __name__ == '__main__':
    logging.basicConfig(filename='mut.log', level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info('Mulit Uart Test Start')

    cfg_uart_parm_1 = dict(port='COM30', baud='9600', parity="Even", bytesize=8, stopbits=1, timeout=1)
    cfg_uart_parm_2 = dict(port='COM31', baud='9600', parity="Even", bytesize=8, stopbits=1, timeout=1)
    cfg_uart_parm_3 = dict(port='COM32', baud='9600', parity="Even", bytesize=8, stopbits=1, timeout=1)
    cfg_uart_parm_4 = dict(port='COM33', baud='9600', parity="Even", bytesize=8, stopbits=1, timeout=1)
    cfg_uart_parm_5 = dict(port='COM34', baud='9600', parity="Even", bytesize=8, stopbits=1, timeout=1)

    teststr = 'FEFEFEFE689100C30572670190312000947D9000788502390200800200010105060000000006000000000600000000060000000006000000001010020001010502020600000CF21C07E4030116210002020600000CE91C07E40302023B0002020600000CF01C07E40302031D0002020600000CED1C07E4030114120002020600'

    cfg_uart_data_1 = dict(recv='68123456789016', send=[teststr], timeout=0.5, autoresp=1, sendbytecnt=0,
                           sendcnt=10, recvbytecnt=0, recvcnt=0)
    cfg_uart_data_2 = dict(recv='68123456789016', send=[teststr], timeout=0.5, autoresp=0, sendbytecnt=0,
                           sendcnt=10, recvbytecnt=0, recvcnt=0)
    cfg_uart_data_3 = dict(recv='68123456789016', send=[teststr], timeout=0.5, autoresp=0, sendbytecnt=0,
                           sendcnt=10, recvbytecnt=0, recvcnt=0)
    cfg_uart_data_4 = dict(recv='68123456789016', send=[teststr], timeout=0.5, autoresp=0, sendbytecnt=0,
                           sendcnt=10, recvbytecnt=0, recvcnt=0)
    cfg_uart_data_5 = dict(recv='68123456789016', send=[teststr], timeout=0.5, autoresp=0, sendbytecnt=0,
                           sendcnt=10, recvbytecnt=0, recvcnt=0)

    cfg_uart_parm_list = [cfg_uart_parm_1, cfg_uart_parm_2, cfg_uart_parm_3, cfg_uart_parm_4, cfg_uart_parm_5]
    cfg_uart_data_list = [cfg_uart_data_1, cfg_uart_data_2, cfg_uart_data_3, cfg_uart_data_4, cfg_uart_data_5]


    uart1thread = UartTest()
    uart2thread = UartTest()
    uart3thread = UartTest()
    uart4thread = UartTest()
    uart5thread = UartTest()

    threadNum = 5

    for i in range(threadNum):
        threading.Thread(target=uart1thread.uart_test, args=(cfg_uart_parm_list[i], cfg_uart_data_list[i])).start()

    while 1:
        time.sleep(1)
        printEn = 0
        for i in range(threadNum):
            if cfg_uart_data_list[i]['autoresp'] == 1:
                printEn = 1
                break

        if printEn == 0:
            for i in range(threadNum):
                if cfg_uart_data_list[i]['sendcnt'] > 0:
                    printEn = 1
                    break

        if printEn:
            printstr = ''
            for i in range(threadNum):
                printstr += cfg_uart_parm_list[i]['port'] + ': '\
                            + str(cfg_uart_data_list[i]['sendcnt'])+ ','\
                            + str(cfg_uart_data_list[i]['sendbytecnt']) \
                            + str(cfg_uart_data_list[i]['sendcnt']) + ','\
                            + str(cfg_uart_data_list[i]['sendbytecnt']) + ';  '
            print(printstr)