from tango import DeviceProxy
from beautifultable import BeautifulTable

# Check if data is flowing at the input 100g (from dish) and output 100g (to SDP)
class Eth100gClient:
    def __init__(self, vcc_boards, fsp_boards):
        self.eth_in_fqdns = [f"talondx-00{v}/ska-talondx-100-gigabit-ethernet/100g_eth_0" for v in vcc_boards]
        self.eth_out_fqdn = f"talondx-00{fsp_boards[0]}/ska-talondx-100-gigabit-ethernet/100g_eth_1"
        self.dp_eth_in = [DeviceProxy(f) for f in self.eth_in_fqdns]
        self.dp_eth_out = DeviceProxy(self.eth_out_fqdn)
        self.tx_stats_idx = {
            "cntr_tx_fragments": 0,
            "cntr_tx_jabbers": 1,
            "cntr_tx_fcs": 2,
            "cntr_tx_crcerr": 3,
            "cntr_tx_mcast_data_err": 4,
            "cntr_tx_bcast_data_err": 5,
            "cntr_tx_ucast_data_err": 6,
            "cntr_tx_mcast_ctrl_err": 7,
            "cntr_tx_bcast_ctrl_err": 8,
            "cntr_tx_ucast_ctrl_err": 9,
            "cntr_tx_pause_err": 10,
            "cntr_tx_64b": 11,
            "cntr_tx_65to127b": 12,
            "cntr_tx_128to255b": 13,
            "cntr_tx_256to511b": 14,
            "cntr_tx_512to1023b": 15,
            "cntr_tx_1024to1518b": 16,
            "cntr_tx_1519tomaxb": 17,
            "cntr_tx_oversize": 18,
            "cntr_tx_mcast_data_ok": 19,
            "cntr_tx_bcast_data_ok": 20,
            "cntr_tx_ucast_data_ok": 21,
            "cntr_tx_mcast_ctrl": 22,
            "cntr_tx_bcast_ctrl": 23,
            "cntr_tx_ucast_ctrl": 24,
            "cntr_tx_pause": 25,
            "cntr_tx_runt": 26,
        }
        self.rx_stats_idx = {
            "cntr_rx_fragments": 0,
            "cntr_rx_jabbers": 1,
            "cntr_rx_fcs": 2,
            "cntr_rx_crcerr": 3,
            "cntr_rx_mcast_data_err": 4,
            "cntr_rx_bcast_data_err": 5,
            "cntr_rx_ucast_data_err": 6,
            "cntr_rx_mcast_ctrl_err": 7,
            "cntr_rx_bcast_ctrl_err": 8,
            "cntr_rx_ucast_ctrl_err": 9,
            "cntr_rx_pause_err": 10,
            "cntr_rx_64b": 11,
            "cntr_rx_65to127b": 12,
            "cntr_rx_128to255b": 13,
            "cntr_rx_256to511b": 14,
            "cntr_rx_512to1023b": 15,
            "cntr_rx_1024to1518b": 16,
            "cntr_rx_1519tomaxb": 17,
            "cntr_rx_oversize": 18,
            "cntr_rx_mcast_data_ok": 19,
            "cntr_rx_bcast_data_ok": 20,
            "cntr_rx_ucast_data_ok": 21,
            "cntr_rx_mcast_ctrl": 22,
            "cntr_rx_bcast_ctrl": 23,
            "cntr_rx_ucast_ctrl": 24,
            "cntr_rx_pause": 25,
            "cntr_rx_runt": 26,
        }

    def clear_counters(self):
        for dp in self.dp_eth_in:
            dp.rx_cnt_clr()
            dp.rx_parity_err_clr()
        self.dp_eth_out.tx_cnt_clr()
        self.dp_eth_out.tx_parity_err_clr()

    def read_counters(self):
        tx_table = self._get_tx_stat_table()
        rx_table = self._get_rx_stat_table()
        return tx_table, rx_table
    
    def _get_name(self, fqdn):
        parts = fqdn.split('/')
        return parts[0] + '__' + parts[2]
    
    def _get_tx_stat_table(self):
        tx_stats = self.dp_eth_out.get_tx_stats()
        tx_table = BeautifulTable(maxwidth=180)
        tx_table.columns.header = [
            "device",
            "cntr_tx_fragments",
            "cntr_tx_crcerr",
            "cntr_tx_1519tomaxb",
            "cntr_tx_oversize",
        ]
        tx_table.rows.append(
            (
                self._get_name(self.eth_out_fqdn),
                tx_stats[self.tx_stats_idx["cntr_tx_fragments"]],
                tx_stats[self.tx_stats_idx["cntr_tx_crcerr"]],
                tx_stats[self.tx_stats_idx["cntr_tx_1519tomaxb"]],
                tx_stats[self.tx_stats_idx["cntr_tx_oversize"]],
            )
        )
        return tx_table

    def _get_rx_stat_table(self):
        rx_table = BeautifulTable(maxwidth=180)
        rx_table.columns.header = [
            "device",
            "cntr_tx_fragments",
            "cntr_rx_fragments",
            "cntr_tx_oversize",
            "cntr_rx_oversize",
            "cntr_tx_1519tomaxb",
            "cntr_rx_1519tomaxb",
            "TxFrameOctetsOK",
            "RxFrameOctetsOK",
        ]
        for dp, fqdn in zip(self.dp_eth_in, self.eth_in_fqdns):
            rx_stats = dp.get_rx_stats()
            rxframeoctetsok = dp.RxFrameOctetsOK
            tx_stats = dp.get_tx_stats()
            txframeoctetsok = dp.TxFrameOctetsOK
            rx_table.rows.append(
                (
                    self._get_name(fqdn),
                    tx_stats[self.tx_stats_idx["cntr_tx_fragments"]],
                    rx_stats[self.rx_stats_idx["cntr_rx_fragments"]],
                    tx_stats[self.tx_stats_idx["cntr_tx_oversize"]],
                    rx_stats[self.rx_stats_idx["cntr_rx_oversize"]],
                    tx_stats[self.tx_stats_idx["cntr_tx_1519tomaxb"]],
                    rx_stats[self.rx_stats_idx["cntr_rx_1519tomaxb"]],
                    txframeoctetsok,
                    rxframeoctetsok,
                )
            )
        return rx_table

