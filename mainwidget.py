from kivy.uix.boxlayout import BoxLayout
from pyModbusTCP.client import ModbusClient
from threading import Thread
from datetime import datetime
from popups import ModbusPopup, ScanPopup
BOT = ["imgs/botao_off.PNG",'imgs/botao_on.PNG']

class MainWidget(BoxLayout):
    _updateThread = None
    _updateWidgt = True

    """
    Classe do widget principal da aplicacao
    """
    
    _updateThread = None
    def __init__(self, **kwargs):
        """
        Construtor do widget principal
        """
        super().__init__()
        self._scantime = kwargs.get('scantime')
        self._ip = kwargs.get('server_ip')
        self._port = kwargs.get('port')
        self._hora = str(datetime.now())
        self._modbusPopup = ModbusPopup(self._ip, self._port)
        self._scanPopup = ScanPopup(scantime = self._scantime)
        self._modbusClient = ModbusClient(self._ip, self._port)

    def atualizar_hora(self):
        hora = datetime.now()
        self.ids.txt_hora.text = str(hora)[0:19]

    def atualiza_botao(self, botao):
        if botao.background_normal == BOT[0]:
            botao.background_normal = BOT[1]
        else:
            botao.background_normal = BOT[0]

    def conectar(self, ip, port):
        """
        Faz a conexão com o servidor
        """
        try:
            self._ip = ip
            self._port = port
            self._modbusClient.host = self._ip
            self._modbusClient.port = self._port
            self._modbusClient.open()
            print(self._modbusClient)
            if self._modbusClient.is_open:
                self._updateThread = Thread(target=self.updater)
                self._updateThread.start()
                print('conectado')
                self._modbusPopup.dismiss()
            else:
                print('falha na conexao')
                self._modbusPopup.set_info('falha na conexao')
        except Exception as e:
            print('Erro na conexao: ', e.args)
        
    def updater(self):
        pass
        