
from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, DataGraphPopup, HistGraphPopup
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from threading import Thread
from time import sleep
from datetime import datetime
import random
from timeseriesgraph import TimeSeriesGraph
from bdhandler import BDHandler
from kivy_garden.graph import LinePlot


class MainWidget(BoxLayout):
    """
    Widget principal
    """
    _updateThread = None
    _updateWidgets = True
    _tags = {}
    _max_points = 20

    def __init__ (self,**kwargs):
        """
        """
        super().__init__()
        self._scan_time = kwargs.get('scan_time') # Passar um argumento com esse mesmo nome na chamda da função no main, o método get faz a busca na lista dos kwargs.
        self._serverIP = kwargs.get('server_ip')
        self._server_port = kwargs.get('port')       
        self._modbusPopup = ModbusPopup(self._serverIP, self._server_port)
        self._scanPopup = ScanPopup(self._scan_time)
        self._modbusClient = ModbusClient(host= self._serverIP, port = self._server_port)
        self._meas = {}
        self._meas['timestamp'] = None
        self._meas['values'] = {}

        for key, value in kwargs.get('modbus_addrs').items():
            if key == 'fornalha':
                plot_color = (1,0,0,1)
            else:
                plot_color = (random.random(),random.random(),random.random(),random.random())
            self._tags[key] = {'addr': value, 'color': plot_color} 
        self._graph = DataGraphPopup(self._max_points, self._tags['fornalha']['color'])
        self._hgraph = HistGraphPopup(tags = self._tags)
        self._bd = BDHandler(kwargs.get('db_path'), self._tags)


    def startDataRead(self, ip, port):
        """
        confgiuracao de Ip e porta do servidor modbus
        Inicializa uma thread para leitura dos dados e
        atualização da interface grafica
        """
        self._serverIP = ip
        self._server_port = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.port = self._server_port

        try:
            Window.set_system_cursor("wait")
            self._modbusClient.open()
            Window.set_system_cursor("arrow")
            if self._modbusClient.is_open:
                self._updateThread = Thread(target = self.updater)
                self._updateThread.start()
                self.ids.img_com.source = 'imgs/conectado.png'
                self._modbusPopup.dismiss()

            else:
                self._modbusPopup.setInfo("Falha na conexao do servidor")

        except Exception as e:
            print('Erro: ', e.args)

    def updater(self):
        """
        invocador de rotina de leitura de dados/atualizacao
        """
        try:
            while self._updateWidgets:
                self.readData()  #Ler os dados doodbus
                self.updateGUI() #atualizar a interface
                self._bd.insertData(self._meas)
                #inserir no banco de dados
                sleep(self._scan_time/1000)

        except Exception as e:
            self._modbusClient.close()
            print("Erro: ", e.args)

    def  readData(self):
        self._meas['timestamp'] = datetime.now()
        self._meas
        for key, value in self._tags.items():
            self._meas['values'][key] = self._modbusClient.read_holding_registers(value['addr'],1)[0]


    def updateGUI(self):
        """
        metdo de atualizacao da interface grafica
        """
        for key,value in self._tags.items():
            self.ids[key].text = str(self._meas['values'][key]) + 'ºC'
        # Atualizacao do nivel de termometro
        self.ids.lb_temp.size = (self.ids.lb_temp.size[0], self._meas['values']['fornalha']/450*self.ids.termometro.size[1])            
        
        # Atualizacao do grafico: 
        self._graph.ids.graph.updateGraph((self._meas['timestamp'], self._meas['values']['fornalha']), 0)



    def stopRefresh(self):
        self._updateWidgets = False

    def getDataDB(self):
        """
        coleta informacoes da interface fornecida
        e requisita a busca no BD
        """
        try:
            init_t = self.parseDTString(self._hgraph.ids.txt_init_time.text)
            final_t = self.parseDTString(self._hgraph.ids.txt_final_time.text)
            cols = []
            for sensor in self._hgraph.ids.sensores.children:
                if sensor.ids.checkbox.active:
                    cols.append(sensor.id)
            if init_t is None or final_t is None or len(cols)==0:
                return

            cols.append('timestamp')

            dados = self._bd.selectData(cols, init_t, final_t)

            if dados is None or len(dados['timestamp'])==0:
                return

            self._hgraph.ids.graph.clearPlots()

            for key, value in dados.items():
                if key == 'timestamp':
                    continue
                p = LinePlot(line_width=1.5, color = self._tags[key]['color'])
                p.points = [(x, value[x]) for x in range(0, len(value))]
                self._hgraph.ids.graph.add_plot(p)

            self._hgraph.ids.graph.xmax = len(dados[cols[0]])
            self._hgraph.ids.graph.update_x_labels([datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f") for x in dados['timestamp']])



        
        except Exception as e:
            print("Erro na coleta de dados: ", e.args)

    def parseDTString(self, datetime_str):
        """
        Converte a string inserida pelo usuario
        para o formato a ser utilizado na busca do BD
        """
        try:
            d = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
            return d.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print("Erro na conversao de data: ", e.args)