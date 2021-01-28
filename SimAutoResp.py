from PublicLib.public import *
from PublicLib.SerialModule.simSerial import *


class MtrUartTest():
    def uart_test(self, cfg, keepalive, n):
        ss = simSerial()
        ret, ser = ss.DOpenPort(cfg['port'], cfg['baud'],cfg['timeout'],'hex')
        while ret:
            keepalive[n] = 0
            time.sleep(0.01)
            str = ss.DReadPort()  # 读串口数据
            if len(str) > 0:
                if str.isalnum():
                    s = frameaddspace(str)
                    ss.onSendData(ser, s, 'hex')


if __name__ == '__main__':
    ss = simSerial()

    cfg = loadDefaultSettings('SimAutoPespCfg.json')

    threadNum = cfg["Num"]
    uartCfgList = cfg["uartcfg"]
    keepAlive = [0]*threadNum
    uList = []*threadNum

    for i in range(threadNum):
        mut = MtrUartTest()
        threading.Thread(target=mut.uart_test, args=(uartCfgList[i], keepAlive, i,)).start()

    while(1):
        time.sleep(1)
        for i in range(threadNum):
            keepAlive[i] += 1
        for i in range(threadNum):
            if keepAlive[i] > 10:
                print('error', keepAlive)
                break