import grpc
import mine_grpc_pb2
import mine_grpc_pb2_grpc
import hashlib
import random
import string
import threading
import time

class ClienteMineracao:
    def __init__(self, endereco_servidor):
        self.channel = grpc.insecure_channel(endereco_servidor)
        self.stub = mine_grpc_pb2_grpc.apiStub(self.channel)
        self.client_id = random.randint(1000, 9999)
        print(f"Cliente {self.client_id} conectado ao servidor {endereco_servidor}")
    
    def getTransactionId(self):
        try:
            response = self.stub.getTransactionId(mine_grpc_pb2.void())
            print(f"TransactionID atual: {response.result}")
            return response.result
        except grpc.RpcError as e:
            print(f"Erro ao obter TransactionID: {e.details()}")
            return -1
    
    def getChallenge(self, transaction_id):
        try:
            request = mine_grpc_pb2.transactionId(transactionId=transaction_id)
            response = self.stub.getChallenge(request)
            if response.result == -1:
                print("TransactionID inválido!")
            else:
                print(f"Desafio da transação {transaction_id}: {response.result}")
            return response.result
        except grpc.RpcError as e:
            print(f"Erro ao obter desafio: {e.details()}")
            return -1
    
    def getTransactionStatus(self, transaction_id):
        try:
            request = mine_grpc_pb2.transactionId(transactionId=transaction_id)
            response = self.stub.getTransactionStatus(request)
            status_map = {-1: "Inválido", 0: "Resolvido", 1: "Pendente"}
            print(f"Status da transação {transaction_id}: {status_map[response.result]}")
            return response.result
        except grpc.RpcError as e:
            print(f"Erro ao obter status: {e.details()}")
            return -1
    
    def getWinner(self, transaction_id):
        try:
            request = mine_grpc_pb2.transactionId(transactionId=transaction_id)
            response = self.stub.getWinner(request)
            if response.result == -1:
                print("TransactionID inválido!")
            elif response.result == 0:
                print(f"Transação {transaction_id} ainda não tem vencedor")
            else:
                print(f"Vencedor da transação {transaction_id}: Cliente {response.result}")
            return response.result
        except grpc.RpcError as e:
            print(f"Erro ao obter vencedor: {e.details()}")
            return -1
    
    def getSolution(self, transaction_id):
        try:
            request = mine_grpc_pb2.transactionId(transactionId=transaction_id)
            response = self.stub.getSolution(request)
            if response.status == -1:
                print("TransactionID inválido!")
            elif response.status == 0:
                print(f"Transação {transaction_id} ainda não foi resolvida. Desafio: {response.challenge}")
            else:
                print(f"Solução da transação {transaction_id}: {response.solution} (Desafio: {response.challenge})")
            return response
        except grpc.RpcError as e:
            print(f"Erro ao obter solução: {e.details()}")
            return None
    
    def submitChallenge(self, transaction_id, solution):
        """Método auxiliar para submeter desafio"""
        try:
            request = mine_grpc_pb2.challengeArgs(
                transactionId=transaction_id,
                clientId=self.client_id,
                solution=solution
            )
            response = self.stub.submitChallenge(request)
            return response.result
        except grpc.RpcError as e:
            print(f"Erro ao submeter desafio: {e.details()}")
            return -1
    
    def mine(self):
        print("\n=== INICIANDO MINERAÇÃO ===")
        
        # 1. Buscar transactionID atual
        transaction_id = self.getTransactionId()
        if transaction_id == -1:
            return
        
        # 2. Buscar challenge
        difficulty = self.getChallenge(transaction_id)
        if difficulty == -1:
            return
        
        # 3. Buscar solução localmente (com múltiplas threads)
        print(f"Minando transação {transaction_id} com dificuldade {difficulty}...")
        solution = self._encontrar_solucao(difficulty)
        
        if solution:
            print(f"Solução encontrada: {solution}")
            
            # 5. Submeter solução
            result = self.submitChallenge(transaction_id, solution)
            
            # 6. Imprimir resposta
            status_map = {
                -1: "TransactionID inválido",
                0: "Solução inválida",
                1: "Solução válida! Você venceu!",
                2: "Desafio já foi solucionado"
            }
            print(f"Resposta do servidor: {status_map.get(result, 'Erro desconhecido')}")
        else:
            print("Não foi possível encontrar uma solução a tempo.")
    
    def _encontrar_solucao(self, difficulty):
        """Encontra uma solução para o desafio usando múltiplas threads"""
        encontrou = {'solucao': None, 'encontrado': False}
        threads = []
        
        def worker(worker_id):
            chars = string.ascii_letters + string.digits
            attempts = 0
            while not encontrou['encontrado'] and attempts < 100000:
                # Tenta uma solução aleatória
                candidate = ''.join(random.choices(chars, k=10))
                hash_result = hashlib.sha1(candidate.encode()).hexdigest()
                
                if hash_result[:difficulty] == '0' * difficulty:
                    encontrou['solucao'] = candidate
                    encontrou['encontrado'] = True
                    print(f"Thread {worker_id} encontrou solução após {attempts} tentativas!")
                    return
                attempts += 1
        
        # Cria 4 threads para mineração
        for i in range(4):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Aguarda por 30 segundos máximo
        timeout = 30
        start_time = time.time()
        
        for t in threads:
            t.join(timeout=max(0, timeout - (time.time() - start_time)))
        
        # Para qualquer thread restante
        encontrou['encontrado'] = True
        
        return encontrou['solucao']

def menu_principal():
    cliente = ClienteMineracao('localhost:50051')
    
    while True:
        print("\n" + "="*50)
        print("MINERADORA DE CRIPTOMOEDAS")
        print("="*50)
        print("1 - getTransactionId")
        print("2 - getChallenge") 
        print("3 - getTransactionStatus")
        print("4 - getWinner")
        print("5 - getSolution")
        print("6 - Mine (Mineração Automática)")
        print("0 - Sair")
        
        try:
            opcao = input("\nEscolha uma opção: ").strip()
            if not opcao:
                continue
                
            opcao = int(opcao)
            
            if opcao == 0:
                print("Encerrando cliente...")
                break
            elif opcao == 1:
                cliente.getTransactionId()
            elif opcao == 2:
                tid = int(input("Digite o TransactionID: "))
                cliente.getChallenge(tid)
            elif opcao == 3:
                tid = int(input("Digite o TransactionID: "))
                cliente.getTransactionStatus(tid)
            elif opcao == 4:
                tid = int(input("Digite o TransactionID: "))
                cliente.getWinner(tid)
            elif opcao == 5:
                tid = int(input("Digite o TransactionID: "))
                cliente.getSolution(tid)
            elif opcao == 6:
                cliente.mine()
            else:
                print("Opção inválida!")
                
        except ValueError:
            print("Por favor, digite um número válido!")
        except KeyboardInterrupt:
            print("\nEncerrando cliente...")
            break

if __name__ == '__main__':
    menu_principal()