from kivy.uix.boxlayout import BoxLayout
from threading import Thread
from datetime import datetime
from popups import ModbusPopup, ScanPopup
BOT = ["imgs/botao_off.PNG",'imgs/botao_on.PNG']

class MainWidget(BoxLayout):
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

    def atualizar_hora(self):
        hora = datetime.now()
        self.ids.txt_hora.text = str(hora)[0:19]

    def atualiza_botao(self, botao):
        if botao.background_normal == BOT[0]:
            botao.background_normal = BOT[1]
        else:
            botao.background_normal = BOT[0]
        