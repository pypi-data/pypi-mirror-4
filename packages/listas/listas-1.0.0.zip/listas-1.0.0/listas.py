"""Esté é meu primeiro modulo em Python. Ele imprimi listas aninhadas"""

def arrumaListas(lista, alinhar = False, alinhamento = 0):
        for item_lista in lista:
                if isinstance(item_lista, list):
                        arrumaListas(item_lista, alinhar, alinhamento + 1)
                else:
                        if alinhar:
                                for a in range(alinhamento):
                                        print("\t", end='')
                        print(item_lista)
