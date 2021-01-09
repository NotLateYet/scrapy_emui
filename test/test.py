def test_nmap():
    from nmap import nmap
    nm = nmap.PortScanner()
    nm.scan('192.168.43.1-255', arguments='-sn -PS -T5 --min-parallelism 100')
    print(nm.get_nmap_last_output())


def test_redlock():
    from redlock import RedLock
    with RedLock("distributed_lock"):
        pass


test_nmap()