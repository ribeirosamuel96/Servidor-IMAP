import socket
import getpass


#criando a conexão TCP com o servidor usando a porta do IMAP
serverName = "mail.labredes.info"
serverPort = 143
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.connect((serverName, serverPort))
recv = tcp.recv(1024)
print(recv.decode('utf-8'))

if "* OK" in recv.decode("utf-8"):
    print("Conexão estabelecida")
else:
    print("Conexão Recusada")

#Realizando autenticação do usuário
def login():

    login = input("Entre com seu e-mail: ")
    senha = getpass.getpass(prompt='Password: ', stream=None)
    login = login.split("@")
    tcp.send(f"1 LOGIN {login[0]} {senha}\r\n".encode())
    recv = (tcp.recv(1024))
    if recv[0:4].decode(('utf-8')) == ("1 OK"):
        print("Login Realizado com Sucesso\n")
        return True
    else:
        print("Falha ao logar")
        return False

#função que retorna o número total de mensagens existentes
def numeroTotalMensagens():
    tcp.send("2 SELECT inbox\r\n".encode())
    recv = (tcp.recv(1024))
    recv = recv.decode('utf-8').split("\r\n")
    numeroMesangens = recv[2]
    numeroMesangens = list(numeroMesangens)
    numeroMesangens = int(numeroMesangens[2]) #pegando o número total de mensagens 
    return numeroMesangens

#função que cria uma matriz com os uids, flags e status das mensagem
def uids(tamanho): 
    tcp.send("4 UID fetch 1:* (FLAGS)\r\n".encode())
    recv = tcp.recv(2048)
    recv = recv.decode('utf-8')
    recv = recv.split("\r\n")
    
    for i in range(tamanho):
        recv[i] = recv[i].split(" ") #criando uma matriz com a resposta do servidor [x][4] = coluna 4 guarda o uid e [x][1] e o numero do email 
    
    del recv[-1]
    
    if "OK" in recv[-1]:
        return recv
    else:
        print("UID FETCH FALHOU")


def listarCabecalho(tamanho):    
    uid = uids(tamanho)
    for cont in range(len(uid)-1):
        tcp.send(f"5 UID fetch {uid[cont][4]} (body[header.fields (from to subject date)])\r\n".encode())
        recv = tcp.recv(2048)
        recv = recv.decode("utf-8")
        recv = recv.split("\r\n")
        if  (uid[cont][6]) == "(\Seen" or (uid[cont][6]) == "(\Seen))":
            print(f"Email {uid[cont][1]} Visualizado".center(70, '_'))
        else:
            print(f"Email {uid[cont][1]} Não Visualizado".center(70, '_'))
        for i in range(1,5):
            print(recv[i])
    print()

def abrirEmail(tamanho):
    uid = uids(tamanho)
    numeroDoEmail = input("Forneça o número do email que deseja abrir: ")
    print("-"*70)
    for cont in range(len(uid)):
        if numeroDoEmail == uid[cont][1]:
            tcp.send(f"6 UID fetch {uid[cont][4]} (UID RFC822.SIZE BODY.PEEK[])\r\n".encode())
            #tcp.send(f"6 fetch {uid[cont][4]} body[text]\r\n".encode())
            recv = tcp.recv(1024)
            recv = recv.decode("utf-8")
            return print("\n",recv)
            
    print("Número que corresponde ao email não foi encontrado")  
    return abrirEmail(tamanho)

    



#Realizando Logout 
def logout():

    tcp.send("9 LOGOUT\r\n".encode("utf-8"))
    recv = (tcp.recv(1024))
    if recv[:5].decode(("utf-8")) == ("* BYE"):
        print("\nLogout Feito com sucesso !!\n")
    else:
        print("\nFalha ao sair do servidor\n")
    tcp.close() #Fechando a conexão com o servidor