import tm1637
import io

class S7:
    """
    Define high level operations for seven segement displays.
    """
    def chars_from_segments(self,SEG):
        """create mapping from characters to segments
        :param: enumeration of segment bit masks.
        """
        self.s7 = {
            ' ': 0b0000000,
            # characters with one segment:
            '-': SEG.G,
            '_': SEG.D,
            # characters with two segments:
            '1': SEG.B | SEG.C,
            'I': SEG.F | SEG.E,
            'R': SEG.E | SEG.G
        }
        # characters with three segments:
        self.s7.update({
            "J": s7["1"] | SEG.D,
            "L": s7["I"] | SEG.D,
            "N": s7["R"] | SEG.C,
            "V": SEG.E | SEG.D | SEG.C,
            "GAMMA": s7["I"] | SEG.A,
            "X": SEG.A | SEG.G | SEG.D,
            "7": s7["1"] | SEG.A,
            "K": s7["I"] | SEG.G
        })
        # characters with four segments:
        self.s7.update({
            "M": s7["N"] | SEG.A,
            "C": s7["L"] | SEG.A,
            "W": SEG.D | SEG.F | SEG.G | SEG.B,
            "?": SEG.A | SEG.B | SEG.G | SEG.E,
            "DEGREE":  SEG.A | SEG.B | SEG.G | SEG.F,
            "T": s7["L"] | SEG.G,
            "4": s7["1"] | SEG.G | SEG.F,
            "O": s7["N"] | SEG.D
        })
        # characters with five segments:
        self.s7.update({
            "U": s7["V"] | SEG.B | SEG.F,
            "B": s7["O"] | SEG.F,         
            "D": s7["O"] | SEG.B,
            "P": s7["F"] | SEG.B,
            "2": s7["?"] | SEG.D,
            "F": s7["GAMMA"] | SEG.G,
            "G": s7["C"] | SEG.C,
            "H": s7["1"] | s7["I"] | SEG.G,
            "Q": s7["DEGREE"] | SEG.C,
            "Y": s7["1"] | SEG.F | SEG.G,
            "3": s7["J"] | SEG.G | SEG.A,
            "@": s7_C | SEG.B,
            "5": SEG.A | SEG.F | SEG.G | SEG.C | SEG.D,
            "E": s7["C"] | SEG.G,
            "9": s7["DEGREE"] | SEG.C | SEG.D,
            "0": s7["C"] | S7["1"]            
        })
        self.s7.update({
            "Z": s7["2"],
            "S": s7["5"],
            # characters with six segments:
            "A": s7["Q"] | SEG.E,
            "6": s7["B"] | SEG.A,
            # characters with seven segments:
            "8": s7["0"] | SEG.G
        })

        def __init__(self,tm):
            self.tm = tm
            self.chars_from_segments(tm.SEG)

        def open(self):
            return Stream(self)

        class Stream(io.IOBase):
            def __init__(self,s7):
                self.s7 = s7
                self._blank()

            def _blank(self):
                self.s7.tm.set_segments( (0,0,0,0) )
                self.do_blank = False
                self.pos = 0

            def write(self,str):
                if self.do_blank: self.blank()
                
                for written, ch in enumerate(str):
                    if ch == "\n":
                        self.do_blank = True
                    elif ch == "\r":
                        self.pos = 0
                    elif ch in self.s7:
                        self.tm.set_segments(self.s7[ch], pos=self.pos)
                        pos+=1
                    else:
                        log.debug("{}: Non-displayable character: {}.".format(repr(self),ch))
                return written


if __name__ =="__main__":

    tm = tm1637.TM1637()
    s7 = S7(tm)

    s = s7.open()

    for str in ("ABCD\n",
                "EFGH\n", 
                "IJKL\n", 
                "MNOP\n",
                "QRTS\n",
                "UVWX\n",
                "YZ01\n",
                "2345\n",
                "6789\n",
                "@_?+\n"):
        s7.write(str)

    
    


#        '0': 0b0111111, 
#       '1': 0b0000110, 
#        '2': 0b1011011, 
#        '3': 0b1001111,
#        '4': 0b1100110,
#        '5': 0b1101101, 
#        '6': 0b1111101, 
#        '7': 0b0000111,
#        '8': 0b1111111,
#        '9': 0b1101111, 
#        'A': 0b1110111, 
#        'B': 0b1111100,
#        'C': 0b0111001,
#        'D': 0b1011110,
#        'E': 0b1111001,
#        'F': 0b1110001,



