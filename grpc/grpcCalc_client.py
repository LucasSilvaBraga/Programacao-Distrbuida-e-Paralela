import grpc
import grpcCalc_pb2
import grpcCalc_pb2_grpc
import pybreaker

breaker = pybreaker.CircuitBreaker(fail_max=2, reset_timeout=2)
@breaker


@breaker
def connect():
    channel = grpc.insecure_channel('localhost:8080')
    client = grpcCalc_pb2_grpc.apiStub(channel)
    while True:
        try:
            print('Adição:')
            x = int(input('Entre com o primeiro número: '))
            y = int(input('Entre com o segundo número: '))
            res = client.add(grpcCalc_pb2.args(numOne=x, numTwo=y))
            print(res.num)
        
        except pybreaker.CircuitBreakerError:
            print(pybreaker.CircuitBreakerError)


if __name__ == '__main__':
    connect()

