import asyncio


def run_server(host, port):
    """ ----------------------------  protocol ---------------------------- """
    class ClientServerProtocol(asyncio.Protocol):
        def __init__(self):
            nonlocal storage
            self.storage = storage

        def connection_made(self, transport):
            self.transport = transport

        def data_received(self, data):
            resp = self._process_data(data.decode())
            self.transport.write(resp.encode())

        def _process_data(self, data):
            data = data.strip('\n').split()
            if len(data) < 1:
                # empty data
                return 'error\nwrong command\n\n'

            if data[0] == 'put':
                # puting
                if len(data) != 4:
                    return 'error\nwrong command\n\n'
                try:
                    float(data[2])
                    int(data[3])
                except ValueError:
                    # wrong metric format
                    return 'error\nwrong command\n\n'

                if data[1] not in self.storage.keys():
                    self.storage[data[1]] = []

                def _timestamp_exist(storage, key, timestamp):
                    for i in range(len(storage[key])):
                        if storage[key][i][0] == timestamp:
                            return i
                    return None
                exists_idx = _timestamp_exist(self.storage, data[1], data[3])
                if exists_idx is not None:
                    # metric with current timestamp already exists
                    # (timestamp, value)
                    self.storage[data[1]][exists_idx] = (data[3], data[2])
                else:
                    # (timestamp, value)
                    self.storage[data[1]].append((data[3], data[2]))
                return 'ok\n\n'

            elif data[0] == 'get':
                # geting
                if len(data) != 2:
                    return 'error\nwrong command\n\n'
                ans = 'ok\n'
                if data[1] != '*':
                    # certain metrics send
                    if data[1] not in self.storage.keys():
                        return 'ok\n\n'
                    metrics = self.storage[data[1]]
                    for metric in metrics:
                        if (float(metric[1]) % 1) == 0 and \
                                ('.0' not in metric[1]):
                            metric = (metric[0], metric[1] + '.0')
                        ans += f'{data[1]} {metric[1]} {metric[0]}\n'
                    ans += '\n'
                elif data[1] == '*':
                    # all metrics send
                    for key, metrics in self.storage.items():
                        for metric in metrics:
                            if (float(metric[1]) % 1) == 0 and \
                                    ('.0' not in metric[1]):
                                metric = (metric[0], metric[1] + '.0')
                            ans += f'{key} {metric[1]} {metric[0]}\n'
                    ans += '\n'

                return ans

            else:
                return 'error\nwrong command\n\n'

    """ ------------------------------  main ------------------------------ """
    storage = {}
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        ClientServerProtocol,
        host, port
    )

    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
