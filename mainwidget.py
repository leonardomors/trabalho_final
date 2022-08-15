from time import sleep
from kivy.uix.boxlayout import BoxLayout
from pyModbusTCP.client import ModbusClient
from threading import Thread
from datetime import datetime
from popups import ModbusPopup, ScanPopup, MotorPopup, InversorPopup, DataGraphPopup
from timeseriesgraph import TimeSeriesGraph

BOT = ["imgs/s1.png",'imgs/s2.png']

class MainWidget(BoxLayout):
    _updateThread = None
    _updateWidgt = True
    _tags = []
    _max_points = 20

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
        self._motorPopup = MotorPopup()
        self._inversorPopup = InversorPopup()
        self._dataGraph = DataGraphPopup(self._max_points, plot_color=(1,0,0,1))

        


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
                # self.atualiza_motor()
                # self.atualizar_inversor()
                self.updateGUI()
                sleep(self._scantime/1000)
                # print('tensaõ: ', self._meas['values']['tensao'])
                # print('pot_entrada: ', self._meas['values']['pot_entrada'])
                # print('corrente: ', self._meas['values']['corrente'])
                # self.ids.lb_agua.size(self.ids.lb_agua.size[0], self._meas['values']['nivel']/100*self.ids.tanque.size[1])

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
        

    def stopRefresh(self):
        self._updateWidgt= False

    def updateGUI(self):
        """
        Método que atualiza as interfaces gráficas em geral
        """
        ## Atualização do Popup do motor:
        key_motor = ['estado_mot', 't_part', 'freq_motor', 'rotacao', 'temp_estator']
        for key, value in self._meas['values'].items():
            if key in key_motor:
                self._motorPopup.ids[key].text = str(value)

        ## Atualização do Popup do inversor:
        key_inversor = ['tensao', 'pot_entrada', 'corrente']
        for key, value in self._meas['values'].items():
            if key in key_inversor:
                self._inversorPopup.ids[key].text = str(value)
        
        ## Atualizacao do tanque de agua

        self.ids.lb_agua.size = (self.ids.lb_agua.size[0], self._meas['values']['nivel']/1000*self.ids.tanque.size[1])
        self.ids.nv_agua.text = str(self._meas['values']['nivel']) + ' litros'

        ## Atualizacao do grafico
        self._dataGraph.ids.graph.updateGraph((self._meas['timestamp'], self._meas['values']['nivel']),0)


    # def atualiza_motor(self):
    #     key_motor = ['estado_mot', 't_part', 'freq_motor', 'rotacao', 'temp_estator']
    #     for key, value in self._meas['values'].items():
    #         if key in key_motor:
    #             self._motorPopup.ids[key].text = str(value)

    # def atualizar_inversor(self):
    #     key_inversor = ['tensao', 'pot_entrada', 'corrente']
    #     for key, value in self._meas['values'].items():
    #         if key in key_inversor:
    #             self._inversorPopup.ids[key].text = str(value)
                

    def operar_motor(self, freq_des):
        if self._meas['values']['estado_mot'] == False:
            self._modbusClient.write_single_register(799, freq_des)
            self._modbusClient.write_single_coil(800, True)
            self._motorPopup.ids.op_motor.text = "DESLIGAR"
        elif self._meas['values']['estado_mot'] == True:
            self._modbusClient.write_single_coil(800, False)
            self._motorPopup.ids.op_motor.text = "DESLIGAR"

    def ligar_motor(self, freq_des):

        self._modbusClient.write_single_register(799, freq_des)
        self._modbusClient.write_single_coil(800, True)

    def desligar_motor(self):
        self._modbusClient.write_single_coil(800, False)

    def operar_solenoide(self, solenoide):
        if solenoide == 'on1':
            self._modbusClient.write_single_coil(801, True)
        elif solenoide == 'on2':
            self._modbusClient.write_single_coil(802, True)
        elif solenoide == 'on3':
            self._modbusClient.write_single_coil(803, True)

        pass

    def atualiza_botao(self, botao, address):
        if botao.background_normal == BOT[0]:
            botao.background_normal = BOT[1]
            self._modbusClient.write_single_coil(int(address), True)

        else:
            botao.background_normal = BOT[0]
            self._modbusClient.write_single_coil(int(address), False)
        
        