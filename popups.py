from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout

class ModbusPopup(Popup):
    """
    Popup da tela de conexção (modbus)
    """
    def __init__(self, server_ip, port, **kwargs):
        super().__init__(*kwargs)
        self.ids.txt_ip.text = str(server_ip)
        self.ids.txt_port.text = str(port)

class ScanPopup(Popup):
    def __init__(self,scantime, **kwargs):
        super().__init__(**kwargs)
        self.ids.ti_scan.text = str(scantime)