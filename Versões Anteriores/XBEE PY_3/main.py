from Monitor import MonitorSerial

if __name__ == "__main__":
    monitor = MonitorSerial("COM3",9600)
    monitor.msg = 'ab8110dee936cd'
    monitor.start()
    try:
        while True:
            pass
    except:
        monitor.stop()
    #"ab8110dee936cd")
    #msg=[0xab, 0x81, 0x10, 0xde, 0xe9, 0x36, 0xcd]