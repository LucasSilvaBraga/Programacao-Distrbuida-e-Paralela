import grpc
from concurrent import futures
import random
import hashlib
import time
import mine_grpc_pb2
import mine_grpc_pb2_grpc

class MineracaoServicer(mine_grpc_pb2_grpc.apiServicer):
    def __init__(self):
        self.transactions = []
        self.current_transaction_id = 0
        self._criar_nova_transacao()
    
    def _criar_nova_transacao(self):
        """Cria uma nova transação com desafio aleatório"""
        challenge = random.randint(1, 3)
        transaction = {
            'transactionID': self.current_transaction_id,
            'challenge': challenge,
            'solution': '',
            'winner': -1
        }
        self.transactions.append(transaction)
        self.current_transaction_id += 1
        print(f"Nova transação criada: ID={transaction['transactionID']}, Challenge={challenge}")
    
    def _encontrar_transacao(self, transaction_id):
        """Encontra transação pelo ID"""
        for trans in self.transactions:
            if trans['transactionID'] == transaction_id:
                return trans
        return None
    
    def getTransactionId(self, request, context):
        """Retorna o ID da transação atual pendente"""
        # Encontra a última transação não resolvida
        for trans in reversed(self.transactions):
            if trans['winner'] == -1:
                return mine_grpc_pb2.intResult(result=trans['transactionID'])
        
        # Se todas estão resolvidas, cria nova
        self._criar_nova_transacao()
        return mine_grpc_pb2.intResult(result=self.transactions[-1]['transactionID'])
    
    def getChallenge(self, request, context):
        """Retorna o desafio de uma transação"""
        trans = self._encontrar_transacao(request.transactionId)
        if trans is None:
            return mine_grpc_pb2.intResult(result=-1)
        return mine_grpc_pb2.intResult(result=trans['challenge'])
    
    def getTransactionStatus(self, request, context):
        """Retorna o status da transação"""
        trans = self._encontrar_transacao(request.transactionId)
        if trans is None:
            return mine_grpc_pb2.intResult(result=-1)  # Inválido
        return mine_grpc_pb2.intResult(result=0 if trans['winner'] != -1 else 1)  # 0=Resolvido, 1=Pendente
    
    def submitChallenge(self, request, context):
        """Submete uma solução para o desafio"""
        trans = self._encontrar_transacao(request.transactionId)
        if trans is None:
            return mine_grpc_pb2.intResult(result=-1)  # TransactionID inválido
        
        if trans['winner'] != -1:
            return mine_grpc_pb2.intResult(result=2)  # Desafio já solucionado
        
        # Verifica se a solução é válida
        if self._verificar_solucao(request.solution, trans['challenge']):
            trans['solution'] = request.solution
            trans['winner'] = request.clientId
            print(f"Desafio {trans['transactionID']} resolvido pelo cliente {request.clientId}!")
            # Cria nova transação
            self._criar_nova_transacao()
            return mine_grpc_pb2.intResult(result=1)  # Solução válida
        else:
            return mine_grpc_pb2.intResult(result=0)  # Solução inválida
    
    def getWinner(self, request, context):
        """Retorna o vencedor da transação"""
        trans = self._encontrar_transacao(request.transactionId)
        if trans is None:
            return mine_grpc_pb2.intResult(result=-1)  # Inválido
        return mine_grpc_pb2.intResult(result=trans['winner'] if trans['winner'] != -1 else 0)  # 0 = sem vencedor
    
    def getSolution(self, request, context):
        """Retorna a solução da transação"""
        trans = self._encontrar_transacao(request.transactionId)
        if trans is None:
            return mine_grpc_pb2.structResult(status=-1, solution="", challenge=0)
        
        if trans['winner'] == -1:
            return mine_grpc_pb2.structResult(status=0, solution="", challenge=trans['challenge'])  # Pendente
        else:
            return mine_grpc_pb2.structResult(status=1, solution=trans['solution'], challenge=trans['challenge'])  # Resolvido
    
    def _verificar_solucao(self, solution, difficulty):
        """Verifica se a solução atende ao desafio"""
        hash_result = hashlib.sha1(solution.encode()).hexdigest()
        # O desafio: os primeiros 'difficulty' caracteres devem ser zeros
        return hash_result[:difficulty] == '0' * difficulty

def servir():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mine_grpc_pb2_grpc.add_apiServicer_to_server(MineracaoServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor de mineração rodando na porta 50051...")
    
    try:
        while True:
            time.sleep(86400)  # Mantém o servidor rodando
    except KeyboardInterrupt:
        print("\nParando servidor...")
        server.stop(0)

if __name__ == '__main__':
    servir()