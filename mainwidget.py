from time import sleep
from kivy.uix.boxlayout import BoxLayout
from pyModbusTCP.client import ModbusClient
from threading import Thread
from datetime import datetime
from popups import ModbusPopup, ScanPopup
BOT = ["imgs/s1.png",'imgs/s2.png']

class MainWidget(BoxLayout):
    _updateThread = None
    _updateWidgt = True
    _tags = []

    """
    Classe do widget principal da aplicacao
    """
    
    _updateThread = None
    def __init__(self, **kwargs):
        """
        Construtor do widget principal
        """
        self._tags = {}
        super().__init__()
        self._scantime = kwargs.get('scantime')
        self._ip = kwargs.get('server_ip')
        self._port = kwargs.get('port')
        self._hora = str(datetime.now())
        self._modbusPopup = ModbusPopup(self._ip, self._port)
        self._scanPopup = ScanPopup(scantime = self._scantime)
        self._modbusClient = ModbusClient(self._ip, self._port)
        self._meas = {}
        self._meas['timestamp'] = None
        self._meas['values'] = {}
        for key, value in kwargs.get('modbus_addrs').items():
            self._tags[key] = {'info': value, 'color': [1,2,3]}
        

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
                self._updateThread = Thread(target=self.update_widget)
                self._updateThread.start()
                print('conectado')
                self._modbusPopup.dismiss()
                self.ids.img_com.source = 'imgs/conectado.png'

            else:
                print('falha na conexao')
                self._modbusPopup.set_info('falha na conexao')
        except Exception as e:
            print('Erro na conexao: ', e.args)
        
    def update_widget(self):
        """
        atualizador
        """
        try:
            while self._updateWidgt:
                self.readData()
                
                # atualizar interface grafica
                # inserir valores no BD
                
        except  Exception as e:
            self._modbusClient.close()
            print('Erro na atualizacao de widgt: ', e.args)
        
    


        sleep(self._scantime/1000)

        pass

    def readData(self):
        """
        Metodo para leitura dos dados do servidor MODBUS800
        """
        self._meas['timestamp'] = datetime.now()
        for key, value in self._tags.items():
            if self._tags[key]['info']['type'] == 'holding_registers':
                self._meas['values'][key] = (self._modbusClient.read_holding_registers(self._tags[key]['info']['addr'], 1)[0]) / self._tags[key]['info']['mult']
            elif self._tags[key]['info']['type'] == 'coils':
                self._meas['values'][key] = self._modbusClient.read_coils(self._tags[key]['info']['addr'], 1)[0]
            elif self._tags[key]['info']['type'] == 'input_register':
                self._meas['values'][key] = (self._modbusClient.read_input_registers(self._tags[key]['info']['addr'], 1)[0])/ self._tags[key]['info']['mult']
            elif self._tags[key]['info']['type'] == 'discrete_inputs':
                self._meas['values'][key] = self._modbusClient.read_discrete_inputs(self._tags[key]['info']['addr'], 1)[0]
        


    def printar_values(self):
        print(self._meas)
        
    
