import socket
import time


class Client():
    def __init__(self, host, port, timeout=None):
        if type(host) is not str or \
            type(port) is not int or \
            (type(timeout) is not float and type(timeout) is not int and
             timeout is not None):
            self.sock = None
            assert False, f'wrong format for host/port/timeout: \
                            {type(host)}, {type(port), {type(timeout)}}'
        try:
            self.sock = socket.create_connection((host, port), timeout=timeout)
        except socket.error as ex:
            self.sock = None
            assert False, f'socket error: {ex}'

    def get(self, metric_name):
        ''' get metrics from server '''
        def _sort_metrics(metrics):
            print(metrics)
            for key, metric in metrics.items():
                metrics[key] = sorted(metric, key=lambda item: item[0])
            print(metrics)
            sorted_list = sorted(
                metrics.items(), key=lambda item: item[1][0][0])
            metrics = {}
            for item in sorted_list:
                metrics[item[0]] = item[1]
            return metrics

        try:
            ret_metrics = {}
            self.sock.sendall(f'get {metric_name}\n'.encode('utf8'))
            data = self.sock.recv(1024)
            data = data.decode('utf8').split('\n')
            if data[-1] != '' and data[-2] != '':
                raise ClientError(
                    "two last positions of matrics list are not ''")
            if data[0] != 'ok':
                raise ClientError("first position of metrics list is not 'ok'")
            for i in range(1, len(data) - 2):
                metric = data[i].split(' ')
                if len(metric) != 3:
                    raise ClientError("wrong answer from server")
                try:
                    convert = True
                    key = metric[0]
                    values = (int(metric[2]), float(metric[1]))
                except (ValueError, TypeError, IndexError):
                    convert = False
                if not convert:
                    raise ClientError("wrong answer from server")
                if key not in ret_metrics.keys():
                    ret_metrics[key] = []
                ret_metrics[key].append(values)
            return _sort_metrics(ret_metrics)
        except socket.error:
            raise ClientError('problem with recieving msg')

    def put(self, metric_name, num, timestamp=None):
        ''' put metrics to the server '''
        if not timestamp:
            timestamp = int(time.time())
        if type(metric_name) is not str or \
           (type(num) is not float and type(num) is not int) or \
                type(timestamp) is not int:
            raise ClientError('wrong arguments format in put() method')

        try:
            self.sock.sendall(
                f'put {metric_name} {num} {timestamp}\n'.encode('utf8'))
        except socket.error:
            raise ClientError('problem with sending msg')
        try:
            data = self.sock.recv(1024)
            data = data.decode('utf8').split('\n')
            if data[0] != 'ok':
                print('ANS:', data) # TODO: delete
                raise ClientError("server doesn't accept metrics")
        except socket.error:
            raise ClientError("can't recv answer from server")

    def __del__(self):
        if self.sock:
            self.sock.close()
        del self


class ClientError(Exception):
    pass
