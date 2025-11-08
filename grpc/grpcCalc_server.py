import grpc
import time
from concurrent import futures
import grpcCalc_pb2
import grpcCalc_pb2_grpc


def serve():
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpcCalc_pb2_grpc.add_apiServicer_to_server(CalculatorServicer(), grpc_server)
    grpc_server.add_insecure_port('[::]:8080')
    grpc_server.start()
    grpc_server.wait_for_termination()


class CalculatorServicer(grpcCalc_pb2_grpc.apiServicer):

    def calculate(self, request, context):

        # Soma
        if request.operacao == grpcCalc_pb2.Operation.SOMA:
            resultado = request.numOne + request.numTwo

        # Subtração
        elif request.operacao == grpcCalc_pb2.Operation.SUB:
            resultado = request.numOne - request.numTwo

        # Multiplicação
        elif request.operacao == grpcCalc_pb2.Operation.MUL:
            resultado = request.numOne * request.numTwo

        # Divisão (com verificação de divisão por zero)
        elif request.operacao == grpcCalc_pb2.Operation.DIV:
            if request.numTwo == 0:
                context.set_details("Divisão por zero não é permitida")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                return grpcCalc_pb2.result()
            resultado = request.numOne // request.numTwo  # divisão inteira

        else:
            context.set_details("Operação inválida")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return grpcCalc_pb2.result()

        return grpcCalc_pb2.result(num=resultado)


if __name__ == '__main__':
    print("servidor rodando na porta 8080")
    serve()
    
