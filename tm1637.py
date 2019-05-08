import gpiozero as gp
import time
from enum import Enum

class TM1637(gp.CompositeDevice):
    """
    This compositive device represents a multiple-digit 7 segment
    driven by a TM1637 chip. A data sheet can be found at [as of March 2019]:
    https://www.mcielectronics.cl/website_MCI/static/documents/Datasheet_TM1637.pdf.
    """
    class SEG():
        """A 7 segment digit consist of seven LED segements arranged
        and conventionally labelled as follows:

            A
           ---
        F |   | B
           -G-
        E |   | C
           ---   o H
            D

        The 8 bits of a byte 0bHGFEDCbA send to TM1637 correspond to the above
        segements (H correponds to any dots or colons integrated into the
        display):
        """
        A = 0b00000001
        B = 0b00000010
        C = 0b00000100
        D = 0b00001000
        E = 0b00010000
        F = 0b00100000
        G = 0b01000000
        H = 0b10000000
        
    # TM1637 command codes -- see data sheet.
    I2C_COMM1 = 0x40
    I2C_COMM2 = 0xC0
    I2C_COMM3 = 0x80

    def __init__(self,
                 clk_gpio=4,
                 dio_gpio=17,
                 brightness=0,
                 show=True):
        """Create a TM1637 device connected to two gpio gpins.
        :param clk_gpio: gpio # for the clock signal
        :param dio_gpio: gpio # for output and input of data
        :param brightness: of the display from [0..0x7]
        :param show: display is switched on if True, otherwise off.
        """
        gp.CompositeDevice.__init__(self,
                                    clk=gp.GPIODevice(clk_gpio),
                                    dio=gp.GPIODevice(dio_gpio)
        )
        self.clk.pin.output_with_state(0)
        self.dio.pin.output_with_state(0) 
        self.clk_tri()
        self.dio_tri()
        self.clk.pin.pull = "floating"
        self.dio.pin.pull = "floating"
        self.bit_delay()

        self.mode_command()
        self.set_segments( [0] * 6 )
        self.display_command(brightness, show)

    @staticmethod
    def bit_delay():
        """Wait 1us. According to the TM1637 datasheet we have to wait for
        at least on 1us between certain changes on the clk and dio
        lines. 

        Typically the delay time of this method will be much longer than
        1us, up to in the order for ms or even tens of ms depending on
        the underlying OS etc.  

        (In fact on a RPi Zero even elimanting this method, all
        together leaves the TM1637 working, persumably because executing
        all the code between the python interpreter and the system
        call to set the gpio takes in the order of us.)
        """
        time.sleep(1./1000000)

    def clk_low(self):
        """switch clk pin to low."""
        self.clk.pin.function="output"
    def clk_tri(self):
        """switch clk pin to tristate (seen as a high level by the
        TM1647 due to external pull-ups)."""
        self.clk.pin.function="input"
    def dio_low(self):
        """switch dio pin to low."""
        self.dio.pin.function="output"
    def dio_tri(self):
        """switch dio pin to tristate (seen as a high level by the
        TM1647 due to external pull-ups)."""
        self.dio.pin.function="input"

    def mode_command(self):
        self.start()
        self.write_byte(self.I2C_COMM1)
        self.stop()

    def display_command(self, brightness=1, show=True):

        if not 0 <= brightness < 8:
            raise ValueError("Brightness must be between 0 and 7.")

        self.start()
        self.write_byte(self.I2C_COMM3 | brightness | (0b1000 if show else 0))
        self.stop()

    def set_segments(self, segments,pos=0):
        """
        Set the 7-segement displays to the data in segements starting from
        :param segments: iterable with the bytes for the segments.
        :param pos: display number 0..5 to start from

        TODO: don't let it set segments above position 6 in any case -- it seems to wrap over!
        """
        if not 0<=pos<6: raise ValueError("Position must be in range 0..5.")

        self.start()
        self.write_byte(self.I2C_COMM2 | pos)
        for seg in segments:
            self.write_byte(seg)
        self.stop()

    def start(self):
        """Header for a transmission, see the data sheet: A
        transmission starts when DIO goes low, while CLK is high."""
        self.dio_low()
        self.bit_delay()
   
    def stop(self):
        """Trailer for a transmission, see data sheet: DIO goes high
        while CLK is high.
        Aux: Before this is called, write_byte has set clk and dio to tri"""

        self.clk_low() 
        self.dio_low() 
        self.bit_delay()
        self.clk_tri() 
        self.bit_delay()
        self.dio_tri()
        self.bit_delay()
  
    def write_byte(self, b):
        """Transmit a byte of 8 bits bitwise to the TM1637."""
        for i in range(8):
            self.clk_low()
            # self.bit_delay() # Why?

            if b & 1: self.dio_tri()
            else: self.dio_low()
            self.bit_delay()

            self.clk_tri()
            self.bit_delay()
            b >>= 1
      
        self.clk_low()
        self.dio_tri()
        self.bit_delay()

        # TODO: read in ACK bit
        ack = self.dio.pin.state

        self.clk_tri() 
        self.bit_delay() 

        
        #self.clk_low() # Why? -- this is done first thing for the next word.
        #self.bit_delay() # Why?
o
if __name__ == "__main__":
    tm = TM1637()
