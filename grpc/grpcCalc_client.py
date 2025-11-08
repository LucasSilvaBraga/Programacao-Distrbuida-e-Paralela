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
        print("\n===== CALCULADORA RPC =====")
        print("1 - SOMA")
        print("2 - SUBTRAÇÃO")
        print("3 - MULTIPLICAÇÃO")
        print("4 - DIVISÃO")
        print("0 - SAIR")
        op = int(input("Escolha a operação: "))

        if op == 0:
            print("Encerrando cliente...")
            break

        if op not in [1,2,3,4]:
            print("Opção inválida!")
            continue

        x = int(input("Digite o primeiro número: "))
        y = int(input("Digite o segundo número: "))

        # Conversão da escolha do usuário para enum Operation
        operacao_enum = {
            1: grpcCalc_pb2.Operation.SOMA,
            2: grpcCalc_pb2.Operation.SUB,
            3: grpcCalc_pb2.Operation.MUL,
            4: grpcCalc_pb2.Operation.DIV
        }[op]

        try:
            response = client.calculate(
                grpcCalc_pb2.args(numOne=x, numTwo=y, operacao=operacao_enum)
            )
            print("Resultado =", response.num)

        except grpc.RpcError as e:
            print("Erro:", e.details())


if __name__ == '__main__':
    connect()

