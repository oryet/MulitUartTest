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
from PublicLib.public import *

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
        sfe = cfgdata['send'].replace(' ', '')
        # 增加帧序号 2字节
        sn = 0

        while 1:
            time.sleep(0.01)
            if senddelay >= 0:
                senddelay -= 1
            else:
                senddelay = senddelayinit
                if cfgdata['sendcnt'] > 0 and cfgdata['autoresp'] == 1:
                    sn += 1
                    strsn = hex(sn).replace('0x', '0000')[-4:]
                    snfe = strsn + sfe
                    fe = self.addspace(snfe)
                    ss.onSendData(ser, fe, 'hex')

                    # 打印 或 日志记录
                    # print(datetime.datetime.now(), cfgparm['port'], 'Send:', sfe)
                    lg = str(datetime.datetime.now()) + '  ' + cfgparm['port'] + '  ' + 'Send:' + sfe
                    logger.info(lg)
                    cfgdata['sendbytecnt'] += (len(sfe) // 2)
                    cfgdata['sendcnt'] -= 1
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
                cfgdata['recvbytecnt'] += (len(rfe) // 2)


    def uart_test(self, cfgparm, cfgdata):
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

    cfg = loadDefaultSettings('MulitUTMainCfg.json')

    cfg_uart_parm_list = cfg['uartcfg']
    teststr = cfg['teststr']
    cfg_uart_data_list = cfg['datacfg']

    threadNum = cfg['Num']

    for i in range(threadNum):
        ut = UartTest()
        cfg_uart_data_list[i]['send'] = teststr
        threading.Thread(target=ut.uart_test, args=(cfg_uart_parm_list[i], cfg_uart_data_list[i])).start()

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
                            + str(cfg_uart_data_list[i]['sendcnt'])+ ', '\
                            + str(cfg_uart_data_list[i]['sendbytecnt']) + ', ' \
                            + str(cfg_uart_data_list[i]['recvcnt']) + ', '\
                            + str(cfg_uart_data_list[i]['recvbytecnt']) + ';  '
            print(printstr)