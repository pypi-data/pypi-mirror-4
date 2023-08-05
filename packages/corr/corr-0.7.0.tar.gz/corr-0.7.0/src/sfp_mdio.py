#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################################################
# Module: sfp_mdio.py
# Author: Henno Kriel
# e-mail: henno@ska.ac.za
#
# Discription:
##############################################################################################################

"""

>>>>>>>>>>>>>> MGT GPIO & SFP MDIO Registers for 
Register Map
gpio_data_in        3    60000        4
gpio_data_out       3    60004        4
gpio_data_oe        3    60008        4
gpio_data_ded       3    6000c        4
sfp_mdio_sel        3    60010        4
sfp_op_issue        3    60014        4
sfp_op_type         3    60018        4
sfp_op_addr         3    6001c        4
sfp_op_data         3    60020        4
sfp_op_result       3    60024        4

>>>>>>>>>>>>>> Virtex-6 SFP GPIO layout

Signal        SFP mapping         Signal description

mgt_gpio[11]  Unused 
mgt_gpio[10]  SFP1: MDIO          MDIO data line
mgt_gpio[9]   SFP1: MDC           MDIO clock line
mgt_gpio[8]   SFP1: PHY1 RESET    PHY reset when '1'
mgt_gpio[7]   SFP1: PHY0 RESET    PHY reset when '1'
mgt_gpio[6]   SFP1: MDIO Enable   Enable MDIO mode when '1'
mgt_gpio[5]   Unused 
mgt_gpio[4]   SFP0: MDIO          MDIO data line
mgt_gpio[3]   SFP0: MDC           MDIO clock line
mgt_gpio[2]   SFP0: PHY1 RESET    PHY reset when '1'
mgt_gpio[1]   SFP0: PHY0 RESET    PHY reset when '1'
mgt_gpio[0]   SFP0: MDIO Enable   Enable MDIO mode when '1'


#############################################################################################################
>>>>>>>>>>>>>> Software Controlled MDIO Registers

The Virtex-6 includes an MDIO controller in each TRI-MODE ETHERNET MAC. The emac_mdio
module is a wishbone slave which wrap around the embedded MDIO controller.
The emac_mdio module is mapped to a base address 0x00060010. The registers are as follows

Register      Address             Signal description
0x00000010    MDIO_SEL Bit[0]     selects which MDIO device to use, '0' SFP
                                  card 0, '1' SFP card 1

0x00000014    OPISSUE             Write '1' into bit 0 to issue an mdio operation

0x00000018    OPTYPE              When Bit[0] is '1' the operation is an EMAC
                                  configuration register. In this case set bit[2] to '1' for
                                  a read and '0' for a write.
                                  When bit 0 is '0' the operation is an MDIO
                                  operation. Bits[2:1] map to the MDIO operation
                                  bits.

0x0000001c    OPADDR              When OPTYPE[0] is '1' this is the address of the
                                  configuration register.
                                  When OPTYPE[0] is '0' this bit[4:0] are the MDIO
                                  register offset and but [12:8] are the MDIO device
                                  address.

0x00000020    OPDATA              The data to be used for the operation, in the case of
                                  MDIO bits [31:16] are unused

0x00000024    OPRESULT            The data returned from the operation
#############################################################################################################

>>>>>>>>>>>>>> VITESSE GPIO Configuration Register Layout
Table 152.
GPIO_x Config/Status (1Ex010[x*2])
Bit Name Description Access Default
15 Traditional GPIO_1 Output Controls whether the pin is in input or output RW 1
   Tri-state Control mode. Bit usage applies only when the GPIO 
                     pin is configured as a traditional GPIO pin (bits 
                     2:0=000) 
                     0: Output mode 
                     1: Input mode 
14:13 Traditional GPIO 1 Pin Bit usage applies only when the GPIO pin is RW 00
      Function Selection configured as a traditional GPIO pin (bits 
                         2:0=000) 
                         When the pin is in output mode (bit 15=0): 
                         00: Bit 12 value is driven out the pin. 
                         01: drive repeating LOW/Hi-Z pattern at 1Hz. 
                         01: drive repeating LOW/Hi-Z pattern at 2Hz. 
                         01: drive repeating LOW/Hi-Z pattern at 5Hz. 
                         When the pin is in input mode (bit 15=1): 
                         00: no interrupt is generated. 
                         01: interrupt generated on the rising edge of 
                         pin. 
                         10: interrupt generated on the falling edge of 
                         pin. 
                         11: interrupt generated on the both rising and 
                         falling edge of pin. 
12 Traditional GPIO_1 Output Logic value transmitted from pin when pin is RW 0
   data configured as a traditional general purpose 
        output (bits 2:0=000, bit 15=0, and bits 
        14:13=00) 
        0: Output data = 0 
        1: Output data = 1 
11 General Purpose Input GPIO_1 must be configured as a general RO 0
   Interrupt Pending purpose input and have interrupt generation 
                     enabled. 
                     0: no interrupt event since the last time the 
                     register was read 
                     1: an interrupt event has occurred 
                     clear on read 
10 General Purpose Input Indicates the present value of the GPIO_7 pin RO 0
   Status 0: Present Value of GPIO_7 pin is 0 
          1: Present Value of GPIO_7 pin is 1 
9:8 Reserved RW 0
7:5 GPIO_7 WIS Interrupt Determines the WIS interrupt status RW 000
    Selection transmitted from the pin when bits 2:0=010 
              000: WIS interrupt A from channel 0 
              001: WIS interrupt A from channel 1 
              010: Reserved 
              011: Reserved 
              100: Logical AND of WIS interrupt A from both 
              channels 
              101: Logical OR of WIS interrupt A from both 
              channels 
              110: Reserved 
              111: Reserved 
4:3 GPIO_7 Link Activity Determines which channel’s link activity is RW 00
    Selection transmitted from the pin when bits 2:0=001 
              00: RX Link Activity from channel 0 
              01: RX Link Activity from channel 1 
              10: Reserved 
              11: Reserved 
2:0 GPIO_7 Pin Function Selects the GPIO pin’s functionality. RW 100
    Selection 000: Traditional GPIO behavior 
              001: PCS Activity LED output 
              010: WIS Interrupt Output 
              011: Transmit internal signals 
              100: UART RX 
              101-111: Reserved for future use.
#############################################################################################################
"""

import corr, time, struct, sys, logging, socket, numpy
from corr import katcp_wrapper

# Configuration MDIO Operations
conf_wr_op = 3 # 011 - Write
conf_rd_op = 5 # 101 - Read
# Software Controlled MDIO Operations
sw_addr_op = 0 # 000 - Address
sw_wr_op = 2 # 010 - Write
sw_rd_op = 6 # 110 - Read
sw_rdinc_op = 4 #100 - Inc Address After Read


class sfp_mezz_card():
    """ An SFP+ mezzanine card, with two dual Vitesse PHYs"""

    def __init__(self,fpga,mezz_n):
        self.fpga=fpga
        self.mezz_n=mezz_n
        self.phys=[sfp_phy(mezz=self), sfp_phy(mezz=self)]

        self.set_sw_mdio()


        # mgt_gpio[11]  Unused 
        # ENABLE SW CONTROL => mgt_gpio[10]  SFP1: MDIO          MDIO data line
        # ENABLE SW CONTROL => mgt_gpio[9]   SFP1: MDC           MDIO clock line
        # ENABLE SW RESET   => mgt_gpio[8]   SFP1: PHY1 RESET    PHY reset when '1'
        # ENABLE SW RESET   => mgt_gpio[7]   SFP1: PHY0 RESET    PHY reset when '1'
        # mgt_gpio[6]   SFP1: MDIO Enable   Enable MDIO mode when '1'
        # mgt_gpio[5]   Unused 
        # ENABLE SW CONTROL => mgt_gpio[4]   SFP0: MDIO          MDIO data line
        # ENABLE SW CONTROL => mgt_gpio[3]   SFP0: MDC           MDIO clock line
        # ENABLE SW RESET   => mgt_gpio[2]   SFP0: PHY1 RESET    PHY reset when '1'
        # ENABLE SW RESET   => mgt_gpio[1]   SFP0: PHY0 RESET    PHY reset when '1'
        # mgt_gpio[0]   SFP0: MDIO Enable   Enable MDIO mode when '1'

    def select(self):
        """Select this mezzanine card"""
        self.set_sw_mdio()
        self.fpga.write_int('sfp_mdio_sel',self.mezz_n) # Select Mezzanine Card 

    def mdio_rst(self,phy_n):
        """Reset the PHYs."""
        phy_val = 0x186; # all phys
        if ((self.mezz_n == 0) & (phy_n == 0)):
            phy_val = 0x002; #     0000 0010
        if ((self.mezz_n == 0) & (phy_n == 1)):
            phy_val = 0x004; #     0000 0100
        if ((self.mezz_n == 1) & (phy_n == 0)):
            phy_val = 0x080; #     1000 0000
        if ((self.mezz_n == 1) & (phy_n == 1)):
            phy_val = 0x100; #0001 0000 0000
        self.fpga.write_int('sfp_gpio_data_oe',phy_val) # Set Output Enable
        self.fpga.write_int('sfp_gpio_data_out',phy_val) # Assert Reset High
        self.fpga.write_int('sfp_gpio_data_out',0) # Deassert Reset

    def set_sw_mdio(self):
        """enable software control of SFP MDIO's"""
        self.fpga.write_int('sfp_gpio_data_ded',0x618) # See SW enable status below:
        # set EMAC MDIO configuration clock divisor and enable MDIO
        self.fpga.write_int('sfp_op_type',conf_wr_op) # Write configuration
        self.fpga.write_int('sfp_op_addr',0x340)
        self.fpga.write_int('sfp_op_data',0x7f)
        self.fpga.write_int('sfp_op_issue',1)

    def sw_mdio_wr(self,phy_n,address,address_offs,data):
        self.select()
        # PHY Address
        if phy_n == 0:   # U1  - '0000' & '0' => Mezz Card Link 0
            phy_val = 0x0000;
        elif phy_n == 1: # U1  - '0000' & '1' => Mezz Card Link 1
            phy_val = 0x0100;
        elif phy_n == 2: # U2  - '1111' & '0' => Mezz Card Link 2
            phy_val = 0x1e00;
        else:            # U2  - '1111' & '1' => Mezz Card Link 3
            phy_val = 0x1f00;
        # set MDIO address addr x addr_offs  ie 1Ex0102
        self.fpga.write_int('sfp_op_type',sw_addr_op) # Address OP
        self.fpga.write_int('sfp_op_addr',phy_val+address)
        self.fpga.write_int('sfp_op_data',address_offs)
        self.fpga.write_int('sfp_op_issue',1)
        # write to MDIO address selected
        self.fpga.write_int('sfp_op_type',sw_wr_op) # Write OP
        self.fpga.write_int('sfp_op_data',data)
        self.fpga.write_int('sfp_op_issue',1)

    def sw_mdio_rd(self,phy_n,address,address_offs):
        self.select()
        # PHY Address
        if phy_n == 0:   # U1  - '0000' & '0' => Mezz Card Link 0
            phy_val = 0x0000;
        elif phy_n == 1: # U1  - '0000' & '1' => Mezz Card Link 1
            phy_val = 0x0100;
        elif phy_n == 2: # U2  - '1111' & '0' => Mezz Card Link 2
            phy_val = 0x1e00;
        else:          # U2  - '1111' & '1' => Mezz Card Link 3
            phy_val = 0x1f00;
        # set MDIO address addr x addr_offs  ie 1Ex0102
        self.fpga.write_int('sfp_op_type',sw_addr_op) # Address OP
        self.fpga.write_int('sfp_op_addr',phy_val+address)
        self.fpga.write_int('sfp_op_data',address_offs)
        self.fpga.write_int('sfp_op_issue',1)
        # write to MDIO address selected
        self.fpga.write_int('sfp_op_type',sw_rd_op) # Read OP
        self.fpga.write_int('sfp_op_issue',1)
        return self.fpga.read_int('sfp_op_result')

    def set_rx_leds():
        """    # Table 152.
        # VSC8488-15 Datasheet
        # Registers
        # GPIO_1 Config/Status (1Ex0102) (continued)
        # Bit 15 Traditional GPIO_1 Output Controls whether the pin is in input or output 
        # Tri-state Control mode. 
        # Bit usage applies only when the GPIO pin is configured as a traditional GPIO pin (bits 2:0=000) 
        #                   0: Output mode
        #                   1: Input mode 
        # Bit 2-0:
        # Selection 000: Traditional GPIO behavior 
        #           001: PCS Activity LED output 
        #           010: WIS Interrupt Output 
        #           011: Transmit internal signals 
        #           100-111: Reserved for future use."""

        # set address 1Ex0102 -- GPIO 1 Rx Led Link 0  
        # def sw_mdio_wr(mezz,phy,address,address_offs,data) 

        # SFP Mezzanine Card 0 RX Led Link 0
        sw_mdio_wr(0,0,0x1e,0x102,1);
        # SFP Mezzanine Card 0 RX Led Link 1
        sw_mdio_wr(0,0,0x1e,0x126,1);
        # SFP Mezzanine Card 0 RX Led Link 2
        sw_mdio_wr(0,2,0x1e,0x102,1);
        # SFP Mezzanine Card 0 RX Led Link 3
        sw_mdio_wr(0,2,0x1e,0x126,1);
        # SFP Mezzanine Card 1 RX Led Link 0
        sw_mdio_wr(1,0,0x1e,0x102,1);
        # SFP Mezzanine Card 1 RX Led Link 1
        sw_mdio_wr(1,0,0x1e,0x126,1);
        # SFP Mezzanine Card 1 RX Led Link 2
        sw_mdio_wr(1,2,0x1e,0x102,1);
        # SFP Mezzanine Card 1 RX Led Link 3
        sw_mdio_wr(1,2,0x1e,0x126,1);

    def set_tx_leds():
        """ Table 152.
        # VSC8488-15 Datasheet
        # Registers
        # GPIO_1 Config/Status (1Ex0102) (continued)
        # Bit 15 Traditional GPIO_1 Output Controls whether the pin is in input or output 
        # Tri-state Control mode. Bit usage applies only when the GPIO 
        #                   pin is configured as a traditional GPIO pin (bits 
        #                   2:0=000) 
        #                   0: Output mode
        #                   1: Input mode 
        # Bit 2-0:
        # Selection 000: Traditional GPIO behavior 
        #           001: PCS Activity LED output 
        #           010: WIS Interrupt Output 
        #           011: Transmit internal signals 
        #           100-111: Reserved for future use."""

        # set address 1Ex0102 -- GPIO 1 Rx Led Link 0  
        # def sw_mdio_wr(mezz,phy,address,address_offs,data) 

        # SFP Mezzanine Card 0 RX Led Link 0
        sw_mdio_wr(0,0,0x1e,0x104,1);
        # SFP Mezzanine Card 0 RX Led Link 2
        sw_mdio_wr(0,1,0x1e,0x104,1);
        # SFP Mezzanine Card 1 RX Led Link 0
        sw_mdio_wr(1,0,0x1e,0x104,1);
        # SFP Mezzanine Card 1 RX Led Link 2
        sw_mdio_wr(1,1,0x1e,0x104,1);

class sfp_phy():
    def __init__(self,mezz,phy_n):


class sfp_module():

    def __init__(self,phy,sfp_n):
        self.fpga=fpga
        self.mezz_n=mezz_n
        self.phy_n=phy_n
        #1  : type of serial transceiver
        #2 : extended type identifier
        #12 : ['reg'], # The nominal bit (signaling) rate (BR, nominal) is specified in units of 100 MBd
        #14 : ['reg'], # Link length supported for 9/125mm fibre, units of km
        #15 : ['reg'], # Link length supported for 9/125mm fibre, units of 100m
        #16 : ['reg'], # Link length supported for 50/125mm fibre, units of 10m
        #17 : ['reg'], # Link length supported for 62.5/125mm fibre, units of 10m
        #18 : ['reg'], # Link length supported for copper, units of m
        #byte 19 is reserved
        #byte 20-35 is SFP transceiver vendor name (ASCII)
        #byte 36 is reserved
        #byte 37-39 Vendor OUI (SFP transceiver vendor IEEE company ID)
        #byte 40-55 Vendor PN (SFP transceiver vendor part number)
        #byte 56-59 Vendor rev (revision number for part)
        #byte 60-62 reserved
        #byte 63 CC_BASE (check code for base ID fields -- addr 0-62)
        #byte 64 is reserved for future options
        #byte 66 is upper bit rate margin (units of %)
        #byte 67 is lower bit rate margin (units of %)
        #byte 68-83 Vendor SN (vendor serial number, ASCII)
        #byte 84-91 Date Code 
        #byte 92-94 Reserved
        #byte 95 CC_EXT (check code for the extended ID fields, addr 64-94)
        #byte 96-127 READ_ONLY VENDOR SPECIFIC fields
        #byte 128-> Vendor specific
        }

    def get_transceiver_type():
        sfp_module_i2c_a0_byte0 = {
        #Type of serial transceiver
          0x0    : 'Unknown or unspecified',
          0x1    : 'GBIC',
          0x2    : 'Module soldered to motherboard (ex: SFF)',
          0x3    : 'SFP or SFP Plus',
          0x4    : 'Reserved for 300 pin XBI devices',
          0x5    : 'Reserved for Xenpak devices',
          0x6    : 'Reserved for XFP devices',
          0x7    : 'Reserved for XFF devices',
          0x8    : 'Reserved for XFP-E devices',
          0x9    : 'Reserved for XPak devices',
          0xa    : 'Reserved for X2 devices',
          0xb    : 'Reserved for DWDM-SFP devices',
          0xc    : 'Reserved for QSFP devices',
          0x80   : 'Reserved, unallocat'
        }

        sfp_module_i2c_a0_byte1 = {
        #Extended identifier of type of serial transceiver
          0x00 : 'GBIC definition is not specified or the GBIC definition is not compliant with a defined MOD_DEF. See product specification for details.',
          0x01 : 'GBIC is compliant with MOD_DEF 1',
          0x02 : 'GBIC is compliant with MOD_DEF 2',
          0x03 : 'GBIC is compliant with MOD_DEF 3',
          0x04 : 'GBIC/SFP function is defined by two-wire serial interface ID only',
          0x05 : 'GBIC is compliant with MOD_DEF 5',
          0x06 : 'GBIC is compliant with MOD_DEF 6',
          0x07 : 'GBIC is compliant with MOD_DEF 7',
          0x08 : 'Unallocated'
        }



    sfp_module_i2c_a0_byte2 = {
    #Connector type
      0x00 : 'Unknown or unspecified',
      0x01 : 'SC',
      0x02 : 'Fibre Channel Style 1 copper connector',
      0x03 : 'Fibre Channel Style 2 copper connector',
      0x04 : 'BNC/TNC',
      0x05 : 'Fibre Channel coaxial headers',
      0x06 : 'FiberJack',
      0x07 : 'LC',
      0x08 : 'MT-RJ',
      0x09 : 'MU',
      0x0A : 'SG',
      0x0B : 'Optical pigtail',
      0x0C : 'MPO Parallel Optic',
      0x20 : 'HSSDC II',
      0x21 : 'Copper pigtail',
      0x22 : 'RJ45',
      0x23 : 'Unallocated',
      0x80 : 'Vendor specific'    
    }

    #bytes 3-10 are for electronic or optical compatibility
    sfp_module_i2c_a0_byte3 = {
      # 10G Ethernet Compliance Codes
      128 : '10G Base-ER',
      64  : '10G Base-LRM',
      32  : '10G Base-LR',
      16  : '10G Base-SR',
      # Infiniband Compliance Codes
      8 : '1X SX',
      4 : '1X LX',
      2 : '1X Copper Active',
      1 : '1X Copper Passive'
    }

    sfp_module_i2c_a0_byte4 = {
      # ESCON & SONET Compliance Codes
      2: 'OC48 long reach'
      1 : 'OC48 intermediate reach'
      0 : 'OC48 short reach'  
    }

    sfp_module_i2c_a0_byte5 = {
      # ESCON & SONET Compliance Codes
      128: 'Reserved'
      64 : 'OC12 single-mode long reach'
      32 : 'OC12 single-mode inter reach'
      16 : 'OC12 multi-mode short reach'
      8 : 'Reserved'
      4 : 'OC3 single-mode long reach'
      2 : 'OC3 single-mode inter. reach'
      1 : 'OC3 multi-mode short reach'
    }

    sfp_module_i2c_a0_byte6 = {
      # Ethernet Compliance Codes
      128 : 'BASE-PX 3',
      64  : 'BASE-BX10 3',
      32  : '100BASE-FX',
      16  : '100BASE-LX/LX10',
      8 : '1000BASE-T',
      4 : '1000BASE-CX',
      2 : '1000BASE-LX',
      1 : '1000BASE-SX'
    }

    sfp_module_i2c_a0_byte7 = {
      # Fibre Channel Link Length
      128 : 'very long distance (V)',
      64  : 'short distance (S)',
      32  : 'intermediate distance (I)',
      16  : 'long distance (L)',
      8 : 'medium distance (M)',
      # Fibre Channel Transmitter Technology
      4 : 'Shortwave laser, linear Rx (SA)',
      2 : 'Longwave laser (LC)',
      1 : 'Electrical inter-enclosure (EL)'
    }

    sfp_module_i2c_a0_byte8 = {
      # Fibre Channel Transmitter Technology
      128 : 'Electrical intra-enclosure (EL)',
      64  : 'Shortwave laser w/o OFC (SN)',
      32  : 'Shortwave laser with OFC (SL)',
      16  : 'Longwave laser (LL)',
      # SFP+ Cable Technology
      8 : 'Active Cable',
      4 : 'Passive Cable',
      2 : 'Unallocated',
      1 : 'Unallocated'
    }

    sfp_module_i2c_a0_byte9 = {
      # Fibre Channel Transmission Media
      128 : 'Twin Axial Pair (TW)',
      64  : 'Twisted Pair (TP)',
      32  : 'Miniature Coax (MI)',
      16  : 'Video Coax (TV)',
      8 : 'Multimode, 62.5um (M6)',
      4 : 'Multimode, 50um (M5, M5E)',
      2 : 'Unallocated',
      1 : 'Single Mode (SM)'
    }

    sfp_module_i2c_a0_byte10 = {
      # Fibre Channel Speed
      128 : '1200 MBytes/sec',
      64  : '800 MBytes/sec',
      32  : '1600 MBytes/sec',
      16  : '400 MBytes/sec',
      8 : 'Unallocated',
      4 : '200 MBytes/sec',
      2 : 'Unallocated',
      1 : '100 MBytes/sec',
      0 : 'Unallocated'  
    }

    sfp_module_i2c_a0_byte11 = {
      # Description of encoding mechanism
      0x00 : 'Unspecified',
      0x01 : '8B/10B',
      0x02 : '4B/5B',
      0x03 : 'NRZ',
      0x04 : 'Manchester',
      0x05 : 'SONET Scrambled',
      0x06 : '64B/66B',
      0x07 : 'Unallocated' 
    }

    sfp_module_i2c_a0_byte13 = {
      0x00 : 'Unspecified',
      0x01 : 'Defined for SFF-8079 (4/2/1G Rate_Select & AS0/AS1)',
      0x02 : 'Defined for SFF-8431 (8/4/2G Rx Rate_Select only)',
      0x03 : 'Unspecified',
      0x04 : 'Defined for SFF-8431 (8/4/2G Tx Rate_Select only)',
      0x05 : 'Unspecified',
      0x06 : 'Defined for SFF-8431 (8/4/2G Independent Rx & Tx Rate_select)',
      0x07 : 'Unspecified',
      0x08 : 'Defined for FC-PI-5 (16/8/4G Rx Rate_select only) High=16G only, Low=8G/4G',
      0x09 : 'Unspecified',
      0x0A : 'Defined for FC-PI-5 (16/8/4G Independent Rx, Tx Rate_select) High=16G only, Low=8G/4G' 
    }


    sfp_module_i2c_a0_byte65 = {
     #Option values
    32: "RATE_SELECT is implemented",
    16: "TX_DISABLE is implemented and disables the serial output",
    8 : "TX_FAULT signal implemented (reset condition defined in section3",
    4: "Loss of signal implemented, signal inverted from definition in table 1",
    2 : "Loss of signal implemented, signal as defined in table 1",
    1 : 'Reserved'
    }

    sfp_module_i2c_a0_byte110 = {
      # 
      128 : 'TX Disable',
      64  : 'Soft TX Disable',
      32  : 'RS(1) State',
      16  : 'Rate_Select State',
      8 : 'Soft Rate_Select',
      4 : 'TX Fault State',
      2 : 'Rx_LOS State',
      1 : 'Data_Ready_Bar State'
    }


    def print_sfp_a0_regs(eeprom_dump):
        for i in range(16):
          # print i
          # print read_sfp_module_regs(mezz,phy,id,addr,value)[i]
          if sfp_module_i2c_a0_regs[i][0] == 'val':
            print (sfp_module_i2c_a0_regs[i][1][read_sfp_module_regs(mezz_n,phy_n,id,addr,value)[i]])
          if sfp_module_i2c_a0_regs[i][0] == 'bit':
            print string_from_bit_field(read_sfp_module_regs(mezz_n,phy_n,id,addr,value)[i],i)
          if sfp_module_i2c_a0_regs[i][0] == 'reg':
            print read_sfp_module_regs(mezz_n,phy_n,id,addr,value)[i]
    ################################################################################################################
    def read_sfp_temp(mezz_n,phy_n):
      temp = read_sfp_module_regs(mezz_n,phy_n,0x51,96,4)
      return_temp = int(temp[0])
      if temp[0] & 128 == 0:
        return_temp += temp[1]/256.0
      else:
        return_temp -= temp[1]/256.0
      return_temp = return_temp
      return return_temp # in Celsius

    ################################################################################################################
    def read_sfp_voltage(mezz_n,phy_n):
      temp = read_sfp_module_regs(mezz_n,phy_n,0x51,98,4)
      adc_val = ((temp[1]) << 8) + temp[0]
      return_volt = adc_val * 100.0/1e6  # LSB = 100uV
      return return_volt

    ################################################################################################################
    def read_sfp_TX_bias_current(mezz_n,phy_n):
      temp = read_sfp_module_regs(mezz_n,phy_n,0xa2>>1,100,4)
      adc_val = ((temp[1]) << 8) + temp[0]
      return_mA = adc_val * 2.0/1e6  # LSB = 2uA
      return return_mA

    ################################################################################################################
    def read_sfp_TX_power(mezz_n,phy_n):
      temp = read_sfp_module_regs(mezz_n,phy_n,0xa2>>1,102,4)
      adc_val = ((temp[1]) << 8) + temp[0]
      return_mW = adc_val * 0.1/1e6  # LSB = 0.1uW
      return return_mW

    ################################################################################################################
    def read_sfp_RX_power(mezz_n,phy_n):
      temp = read_sfp_module_regs(mezz_n,phy_n,0xa2>>1,104,4)
      adc_val = ((temp[1]) << 8) + temp[0]
      return_mW = adc_val * 0.1/1e6  # LSB = 0.1uW
      return return_mW

    ################################################################################################################
    def read_sfp_stat(mezz_n,phy_n):
      temp = read_sfp_module_regs(mezz_n,phy_n,0xa2>>1,110,4)
      ret_string = '' 
      bit_fields = [1,2,4,8,16,32,64,128]
      for idx in range(8):
        if ((temp[0] & bit_fields[idx]) == bit_fields[idx]):
          ret_string += (sfp_module_i2c_a2_byte110[bit_fields[idx]] + '\n')  
      return temp[0], ret_string



    def set_sfp_i2c_gpio():
        sw_mdio_wr(0,0,0x1e,0x108,8404) # set pin as SDA bus#0
        sw_mdio_wr(0,0,0x1e,0x10a,8404) # set pin as SCL bus#0

        sw_mdio_wr(0,0,0x1e,0x12c,8404) # set pin as SDA bus#1
        sw_mdio_wr(0,0,0x1e,0x12e,8404) # set pin as SCL bus#1

        sw_mdio_wr(0,2,0x1e,0x108,8404) # set pin as SDA bus#0
        sw_mdio_wr(0,2,0x1e,0x10a,8404) # set pin as SCL bus#0

        sw_mdio_wr(0,2,0x1e,0x12c,8404) # set pin as SDA bus#1
        sw_mdio_wr(0,2,0x1e,0x12e,8404) # set pin as SCL bus#1

        sw_mdio_wr(1,0,0x1e,0x108,8404) # set pin as SDA bus#0
        sw_mdio_wr(1,0,0x1e,0x10a,8404) # set pin as SCL bus#0

        sw_mdio_wr(1,0,0x1e,0x12c,8404) # set pin as SDA bus#1
        sw_mdio_wr(1,0,0x1e,0x12e,8404) # set pin as SCL bus#1

        sw_mdio_wr(1,2,0x1e,0x108,8404) # set pin as SDA bus#0
        sw_mdio_wr(1,2,0x1e,0x10a,8404) # set pin as SCL bus#0

        sw_mdio_wr(1,2,0x1e,0x12c,8404) # set pin as SDA bus#1
        sw_mdio_wr(1,2,0x1e,0x12e,8404) # set pin as SCL bus#1





def string_from_bit_field(val,reg):
    ret_string = ''
    bit_fields = [1,2,4,8,16,32,64,128]
    for idx in range(8):
      if ((int(val) & bit_fields[idx]) == bit_fields[idx]):
        ret_string += (sfp_module_i2c_a0_regs[reg][1][bit_fields[idx]] + '\n')

    return ret_string 

################################################################################################################
def chk_sfp_busy(mezz_n,phy_n):
    time_out = 0
    res = sw_mdio_rd(mezz_n,phy_n,0x1e,0x8000) & 0xc
    while (res != 0):
        # print 'read busy %i'%res
        res = sw_mdio_rd(mezz_n,phy_n,0x1e,0x8000) & 0xc
        if time_out > 5:
          print 'Error: Read Time Out!'
          break
        else:
          time_out += 1

################################################################################################################

def read_sfp_module_regs(mezz_n,phy_n,id,addr,value):
    """    # Table 152.
    # VSC8488-15 Datasheet
    • 30x8001: slave device ID, using 7-bit addressing, default 0x50 (for slave ID A0)
    • 30x8002: starting slave device memory location, default 0x0000
    • 30x8003: number of registers to be read, default 0x0020 (32)
    • 30x8004: starting on-device register address to store read data, default 0x8010
    • 30x8005: write register, default 0x0000
    The user can write to 30x8000 to start two-wire serial (master) operation:
    • 30x8000.15: two-wire serial speed, 0: 400 kHz; 1: 100 kHZ
    • 30x8000.14: Interface, 0: MDIO/two-wire serial slave; 1: uP
    • 30x8000.13: reserved, should be 0x0
    • 30x8000.12: disable reset sequence, 0: enable reset sequence; 1: disable reset
       sequence
    • 30x8000.11:5: reserved, should be 0x0
    • 30x8000.4: read or write action, 0: read, 1: write
    • 30x8000.3:2: instruction status for MDIO/two-wire serial slave interfaces, 00: idle;
       01: command completed successfully; 10: command in progress; 11: command
      failed.
    • 30x8000.1:0: instruction status for uP interface, 00: idle; 01: command completed
       successfully; 10: command in progress; 11: command failed.
       """
    """
    The per channel two-wire serial bus interface pins SDA and SCL available for connection
    to SFP/SFP+ modules may be used as general purpose I/O (GPIO) when the two-wire
    serial (master) function is not needed. Registers 30x012C, 30x012E, 30x0104,
    30x0106, 30x0118, 30x011A, 30x010C, 30x010E program whether the pins function as
    two-wire serial interface pins or GPIO
    """
    
    # SFP Mezzanine Card 0 RX Led Link 0
    if id != 0x50:
      sw_mdio_wr(mezz_n,phy_n,0x1e,0x8001,id) # diagnostic interface # slave device ID, using 7-bit addressing, default 0x50 (for slave ID A0)
    if addr != 0:
      sw_mdio_wr(mezz_n,phy_n,0x1e,0x8002,addr) # starting slave device memory location, default 0x0000
    if value != 32:
      ## NB!!! value must be multiples of 2!
      sw_mdio_wr(mezz_n,phy_n,0x1e,0x8003,value) # number of registers to be read, default 0x0020 (32)

    sw_mdio_wr(mezz_n,phy_n,0x1e,0x8000,0x0000) # Read Request

    chk_sfp_busy(mezz_n,phy_n)

    res_sfp = numpy.uint8(numpy.zeros(value))
    idx = 0
    # print 'After Read'
    for i in range(value/2):
        res = sw_mdio_rd(mezz_n,phy_n,0x1e,0x8010 + i)
        # print 'val %x'%res
        res_sfp[idx] = numpy.uint8((sw_mdio_rd(mezz_n,phy_n,0x1e,0x8010 + i) & 0xff))
        res_sfp[idx+1] = numpy.uint8(((sw_mdio_rd(mezz_n,phy_n,0x1e,0x8010 + i) >> 8) & 0xff))
        idx += 2
    return res_sfp

################################################################################################################

def write_sfp_module_regs(mezz_n,phy_n,id,addr,value):
    """    # Table 152.
    # VSC8488-15 Datasheet
    • 30x8001: slave device ID, using 7-bit addressing, default 0x50 (for slave ID A0)
    • 30x8002: starting slave device memory location, default 0x0000
    • 30x8003: number of registers to be read, default 0x0020 (32)
    • 30x8004: starting on-device register address to store read data, default 0x8010
    • 30x8005: write register, default 0x0000
    The user can write to 30x8000 to start two-wire serial (master) operation:
    • 30x8000.15: two-wire serial speed, 0: 400 kHz; 1: 100 kHZ
    • 30x8000.14: Interface, 0: MDIO/two-wire serial slave; 1: uP
    • 30x8000.13: reserved, should be 0x0
    • 30x8000.12: disable reset sequence, 0: enable reset sequence; 1: disable reset
       sequence
    • 30x8000.11:5: reserved, should be 0x0
    • 30x8000.4: read or write action, 0: read, 1: write
    • 30x8000.3:2: instruction status for MDIO/two-wire serial slave interfaces, 00: idle;
       01: command completed successfully; 10: command in progress; 11: command
      failed.
    • 30x8000.1:0: instruction status for uP interface, 00: idle; 01: command completed
       successfully; 10: command in progress; 11: command failed.
       """
    """
    The per channel two-wire serial bus interface pins SDA and SCL available for connection
    to SFP/SFP+ modules may be used as general purpose I/O (GPIO) when the two-wire
    serial (master) function is not needed. Registers 30x012C, 30x012E, 30x0104,
    30x0106, 30x0118, 30x011A, 30x010C, 30x010E program whether the pins function as
    two-wire serial interface pins or GPIO
    """
    
    # SFP Mezzanine Card 0 RX Led Link 0
    if id != 0x50:
      sw_mdio_wr(mezz_n,phy_n,0x1e,0x8001,id) # diagnostic interface # slave device ID, using 7-bit addressing, default 0x50 (for slave ID A0)
    if addr != 0:
      sw_mdio_wr(mezz_n,phy_n,0x1e,0x8002,addr) # starting slave device memory location, default 0x0000

    sw_mdio_wr(mezz_n,phy_n,0x1e,0x8005,val) # value to write

    chk_sfp_busy(mezz_n,phy_n)

    sw_mdio_wr(mezz_n,phy_n,0x1e,0x8000,0x0010) # execute write 

    chk_sfp_busy(mezz_n,phy_n)

    # read back value to ensure it was correctly written
    res = read_sfp_module_regs(mezz_n,phy_n,id,addr,2)

    if res[0] == val:
      wr_stat = 0 # no write error
    else:
      wr_stat = 1 

    return wr_stat

################################################################################################################
# def BER():
# """
# BER Calculation
# When the error detector bit is set (1x8201.0, self-clearing), bit errors are counted
# during the training pattern segment of each training frame, until the given number of
# frames (1x820B) has been received.
# A live value of the number of frames counted is in 1x820A. A live value of the bit errors
# counted is in 1x8209. These are non-rollover counters.
# The contents of these registers are frozen when the final frame is counted. They
# maintain the current counts until another start is issued at 1x8201.0 and after the start
# is cleared.
# The received training pattern is evaluated for bit errors using the reverse of the pattern
# generator. For more information, see Figure 32, page 116. Invert the incoming training
# pattern using 1x8201.5; and the outgoing training pattern using 1x8201.6.
# During the BER cycle, register 1x8208 can be monitored for a couple of things.
# Bit 0 is the busy bit that is asserted during the duration of the BER cycle. Upon the
# completion of the last frame to be counted, this bit goes to '0'.
# Bit 1 contains a latch-high flag that is set if, during frame reception, a DME violation
# occurs.
# """
################################################################################################################
def fec_en_chk():
  """
  Forward Error Correction (FEC)

  The KR FEC is implemented as defined in IEEE 802.3ap Clause 74.
  During AN, FEC ability is advertised in bit 46 of the base page. Bit 47 is used to request
  FEC on the link. If both, the VSC8488-15 device and the LP advertises FEC ability, and
  either one requests FEC on the link, then FEC will be enabled.
  FEC control, based on negotiated HCD, is handled by hardware. Also, FEC can be
  enabled independent of any other KR function. There are two vendor specific FEC bits:
  • 1x8300.1 – fec_inframe bit, which is a latch-low bit which can be used by
    management to determine the lock status of the FEC receiver.
  • 1x8300.0 – fec_rstmon bit, which is used to reset the FEC counters.

  KR FEC Ability (1x00AA)
  15:2 Reserved
  1 FEC error indication ability 
    0: This PHY device is not able to report FEC decoding errors to the PCS layer.
    1: This PHY device is able to report FEC decoding errors to the PCS layer.
  0 FEC ability 0: This PHY device does not support FEC.
                1: This PHY device supports FEC.

  KR FEC Control 1 (1x00AB)
  Bit Name 
  15:2 Reserved
  1 FEC enable error 0: Decoding errors have no effect on PCS sync RW 1
    indication bits 
               1: Enable decoder to indicate errors to PCS 
               sync bits 
  0 FEC enable 0: Disable FEC RW 0
               1: Enable FEC 

  KR FEC Corrected Lower (1x00AC)
  KR FEC Corrected Upper (1x00AD)

  KR FEC Uncorrected Lower (1x00AE)
  KR FEC Uncorrected Upper (1x00AF)


  KR FEC Control 2 (1x8300)
  15:2 Reserved
  1 fec_inframe
    0: FEC has not achieved lock RO/LL 1
    1: FEC has achieved lock 
  0 fec_rstmon
    0: no effect RW 0
    1: reset FEC counters 
  """
  fec_en = numpy.zeros(8)

  for mezz_n in range(2):
    for phy_n in range(4):
      # check FEC Ability:
      res = sw_mdio_rd(mezz_n,phy_n,1,0x00aa) & 3  
      fec_en[(mezz_n*4)+phy_n] = res  
      if res == 3:
        # Enable FEC
        sw_mdio_wr(mezz_n,phy_n,1,0x00ab,3)
        # Reset FEC counters 
        sw_mdio_wr(mezz_n,phy_n,1,0x8300,1)
        res = 0
        time_out = 0
        while (res != 2 & time_out < 5):
          res = sw_mdio_rd(mezz_n,phy_n,1,0x8300) & 2
          time_out += 1
        if time_out == 5:
          raise RuntimeError('ERROR: FEC not locking!')
      else:
        raise RuntimeError('PHY does not support FEC!')
  return fec_en

################################################################################################################
def read_fec_cnt(fec_en):
  """
  KR FEC Corrected Lower (1x00AC)
  KR FEC Corrected Upper (1x00AD)

  KR FEC Uncorrected Lower (1x00AE)
  KR FEC Uncorrected Upper (1x00AF)
  """
  fec_corrected_cnt = numpy.zeros(8)
  fec_uncorrected_cnt = numpy.zeros(8)
  for i in range(8):
    fec_corrected_cnt[i] = 0
    fec_uncorrected_cnt[i] = 0
    if fec_en[i] == 3:
      fec_corrected_cnt_i = sw_mdio_rd(mezz_n,phy_n,1,0x00ad) << 8
      fec_corrected_cnt_i += sw_mdio_rd(mezz_n,phy_n,1,0x00ac)
      fec_uncorrected_cnt_i = sw_mdio_rd(mezz_n,phy_n,1,0x00af) << 8
      fec_uncorrected_cnt_i += sw_mdio_rd(mezz_n,phy_n,1,0x00ae)
      fec_corrected_cnt[i] = fec_corrected_cnt_i
      fec_uncorrected_cnt[i] = fec_uncorrected_cnt_i
  return fec_corrected_cnt,fec_uncorrected_cnt

################################################################################################################
def read_link_status(mezz_n,phy_n):
  """
  PHY XS Status1 (4x0001) Transmit Link Status
  PCS Status: PCS Status 1 (3x0001) Receive Link Status
  """
  return_result = [0,0]
  res = sw_mdio_rd(mezz_n,phy_n,4,0x0001) & 4
  if res == 4:
    result[0] = 1
  res = sw_mdio_rd(mezz_n,phy_n,3,0x0001) & 4
  if res == 4:
    result[1] = 1
  return return_result


################################################################################################################
def read_sfp_temp(mezz_n,phy_n):
  temp = read_sfp_module_regs(mezz_n,phy_n,0x51,96,4)
  return_temp = int(temp[0])
  if temp[0] & 128 == 0:
    return_temp += temp[1]/256.0
  else:
    return_temp -= temp[1]/256.0
  return_temp = return_temp
  return return_temp # in Celsius

################################################################################################################
def read_sfp_voltage(mezz_n,phy_n):
  temp = read_sfp_module_regs(mezz_n,phy_n,0x51,98,4)
  adc_val = ((temp[1]) << 8) + temp[0]
  return_volt = adc_val * 100.0/1e6  # LSB = 100uV
  return return_volt

################################################################################################################
def read_sfp_TX_bias_current(mezz_n,phy_n):
  temp = read_sfp_module_regs(mezz_n,phy_n,0xa2>>1,100,4)
  adc_val = ((temp[1]) << 8) + temp[0]
  return_mA = adc_val * 2.0/1e6  # LSB = 2uA
  return return_mA

################################################################################################################
def read_sfp_TX_power(mezz_n,phy_n):
  temp = read_sfp_module_regs(mezz_n,phy_n,0xa2>>1,102,4)
  adc_val = ((temp[1]) << 8) + temp[0]
  return_mW = adc_val * 0.1/1e6  # LSB = 0.1uW
  return return_mW

################################################################################################################
def read_sfp_RX_power(mezz_n,phy_n):

  temp = read_sfp_module_regs(mezz_n,phy_n,0xa2>>1,104,4)
  adc_val = ((temp[1]) << 8) + temp[0]
  return_mW = adc_val * 0.1/1e6  # LSB = 0.1uW
  return return_mW

################################################################################################################
def read_sfp_stat(mezz_n,phy_n):
  temp = read_sfp_module_regs(mezz_n,phy_n,0xa2>>1,110,4)
  ret_string = ''
  bit_fields = [1,2,4,8,16,32,64,128]
  for idx in range(8):
    if ((temp[0] & bit_fields[idx]) == bit_fields[idx]):
      ret_string += (sfp_module_i2c_a2_byte110[bit_fields[idx]] + '\n')  
  return temp[0], ret_string

################################################################################################################

    sfp_id = 0x50
    # reset all phy's
    mdio_rst(-1,-1) 
    set_rx_leds()
    set_tx_leds()
    set_sfp_i2c_gpio()

    # print_sfp_a0_regs(mezz,phy,0x50)

    fec_en = fec_en_chk()
    fec_corrected_cnt, fec_uncorrected_cnt = read_fec_cnt(fec_en)
    for i in range(8):
      print 'Link %i FEC corrected cnt: %i, FEC UNcorrected_cnt: %i'%(i,fec_corrected_cnt[i],fec_uncorrected_cnt[i])

    for mezz_card in range(1):
      for phy_mod in range(2,4):
        mezz = mezz_card
        phy = phy_mod
        print 'Mezzanine %i, Phy %i'%(mezz_card,phy_mod)

        res = sw_mdio_rd(mezz,phy,0x1e,0)
        print res
        # check if the sfp module supports diagnostics
        temp = read_sfp_module_regs(mezz,phy,0x50,92,4)

        if int(temp[0]) & 104 == 104:
          print 'Diagnostic Interface Supported'
          temp = read_sfp_temp(mezz,phy)
          print 'SFP Module Temperature :%2.3f [C]'%temp
          # voltage = read_sfp_voltage(mezz,phy)
          # print 'SFP Module Supply Voltage: %2.3f [V]'%voltage
          # current = read_sfp_TX_bias_current(mezz,phy)
          # print 'SFP Module TX Bias Current: %2.3f [uA]'%current
          # power = read_sfp_TX_power(mezz,phy)
          # print 'SFP Module TX Output Power: %2.6f [mW]'%power
          # power = read_sfp_RX_power(mezz,phy)
          # print 'SFP Module RX Output Power: %2.6f [mW]'%power
          # stat, stat_str = read_sfp_stat(mezz,phy)
          # print 'SFP Module Status Value: %i'%stat
          # print 'SFP Module Status Strings: ' + stat_str
        else:
          print 'Diagnostic Interface NOT supported!'


    # fpga.write_int('pkt_sim_period',1024) #
    # fpga.write_int('pkt_sim_payload_len',64) #
    # fpga.write_int('pkt_sim_enable',1) #
    
       
except KeyboardInterrupt:
    exit_clean()
except:
    exit_fail()

exit_clean()


