import time as t

# Função para registrar o tempo
def log_execution_time(message):
    current_time = t.time()
    print(f"{message} - Tempo de execução: {current_time - log_execution_time.last_time:.2f} segundos")
    log_execution_time.last_time = current_time