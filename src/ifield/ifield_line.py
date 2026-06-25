#==============================================================================
# Siqo class InfoFieldLine
#------------------------------------------------------------------------------
import cmath

from   .                      import logger
from   idata.imatrix          import InfoMatrix

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER    = '1.1.0'

_LAMBDA = 1200       # Default points for Lambda axis
_AMP    =  200       # Default amplituda

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------

#==============================================================================
# InfoFieldLine
#------------------------------------------------------------------------------
class InfoFieldLine(InfoMatrix):

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name):
        "Calls constructor of InfoFieldLine"

        #----------------------------------------------------------------------
        # Super constructor
        #----------------------------------------------------------------------
        super().__init__(name)

        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------


        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------
        self.setIpType('ipIntLine')
        self.setSchema({'axes': {'l': 'Lambda'}, 'vals': {'s': 'State', 'd': 'Delta', 'c': 'Autocorr', 'a': 'Amplitude'}})
        self.init(cnts={'l':_LAMBDA})

        self.applyMatrixMethod(methodKey='Integer random uniform', valueKey='s', params={'min':0, 'max':_AMP})

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    # Dynamics methods for InfoFieldLine
    #--------------------------------------------------------------------------
    def mapSetMethods(self) -> dict:
        "Returns map of methods setting keyed value to function value for respective parameters"

        methods = super().mapSetMethods()

        methods['ILine deltas'      ] = {'matrixMethod': self.deltas,    'pointMethod':None, 'params':{}                               , 'type':'ask'  }
        methods['ILine autocorr'    ] = {'matrixMethod': self.autoCorr,  'pointMethod':None, 'params':{}                               , 'type':'ask'  }
        methods['ILine epoch step'  ] = {'matrixMethod': self.epochStep, 'pointMethod':None, 'params':{}                               , 'type':'ask'  }

        for methodKey in methods.keys():
            if not methodKey.startswith('ILine '): methods[methodKey]['visible'] = False

        return methods

    #==========================================================================
    # Line methods to apply in Dynamics methods
    #--------------------------------------------------------------------------
    def deltas(self, valueKey:str, params:dict):
        """Compute deltas of states between consecutive points."""

        logger.info(f"{self.name}.deltas: for key 'd' with params {params}")
        pts = 0

        #----------------------------------------------------------------------
        # Vsetky IPoints nastavim do subMatrix listu
        #----------------------------------------------------------------------
        points = self.actSubmatrix()

        prevS = 0
        points[0].set( vals = {'d': prevS} )

        #----------------------------------------------------------------------
        # Prejdem vsetky boby v subMatrix a pre kazdy bod nastavim hodnotu ako rozdiel medzi hodnotou bodu a predosleho bodu
        #----------------------------------------------------------------------
        for i in range(1, len(points)):

            point = points[i]
            currS = point.val(valKey='s')

            #------------------------------------------------------------------
            # Vypocet a nastavenie delty
            #------------------------------------------------------------------
            delta = currS - prevS
            point.set( vals = {'d': delta})

            #------------------------------------------------------------------
            # Posun na nasledujuci bod
            #------------------------------------------------------------------
            prevS = currS
            pts += 1

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.deltas: {pts} InfoPoints was updated for key '{valueKey}' in deltas")

    #--------------------------------------------------------------------------
    def autoCorr(self, valueKey:str, params:dict):
        """Compute auto-correlation of states."""

        logger.info(f"{self.name}.autoCorr: for key 'c' with params {params}")

        #----------------------------------------------------------------------
        # Vsetky IPoints nastavim do subMatrix listu
        #----------------------------------------------------------------------
        points = self.actSubmatrix()
        n = len(points)

        #----------------------------------------------------------------------
        # Prejdem tau od 0 po N-1, kde N je pocet bodov v subMatrixe
        #----------------------------------------------------------------------
        for tau in range(n-1):

            suma = 0
            prod = 0
            maxP = 0

            #------------------------------------------------------------------
            # Prejdem dvojice bodov (i, i+tau) a pre kazdu dvojicu bodov vypocitam produkt ich hodnot a pripoctem k sume
            #------------------------------------------------------------------
            for i in range(n):

                # Pouzijem modularnu algebru, aby som pre lub
                iPos =  i        % n
                jPos = (i + tau) % n

                iVal = points[iPos].val(valKey='d')
                jVal = points[jPos].val(valKey='d')

                prod = iVal * jVal
                if prod > maxP: maxP = prod

                suma += prod

            #------------------------------------------------------------------
            # Normujem sumu podla poctu bodov a nastavim hodnotu auto-korelacie pre tau
            #------------------------------------------------------------------
            points[tau].set(vals={'c': (suma/n) })

        #----------------------------------------------------------------------
        # Posledny bod nastavim na 0
        #----------------------------------------------------------------------
        points[n-1].set(vals={'c': 0})

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.autoCorr: Done")

    #--------------------------------------------------------------------------
    def RFT( self, valueKey:str, params:dict):
        """Compute Fast Fourier transform of real states in subMatrix.
        Parameters:
        - 'rad': radix level for FFT (default 8, i.e., 256 points)
        - 'step': step size for moving the FFT window (default: size)
        """

        rad  = params.get('rad' , 8   )  # Default radix level for FFT (256 = 2^8)
        size = 1 << rad                  # Length of the FFT window (must be a power of 2)
        step = params.get('step', size)  # Step size for moving the FFT window

        logger.info(f"{self.name}.RFT: For rad = {rad}, size = {size}, step = {step}")

        #----------------------------------------------------------------------
        # Vsetky IPoints nastavim do subMatrix listu a vytvorim vektor vec
        #----------------------------------------------------------------------
        points = self.actSubmatrix()
        n = len(points)

        vec = [0.0] * n
        for i in range(n):
            vec[i] = points[i].val(valKey='s')

        #----------------------------------------------------------------------
        # Posuvam okno vec[] s dlzkou size o krok step a pre kazde okno vypocitam FFT
        #----------------------------------------------------------------------
        start = 0
        size  = 1 << rad  # Size of the FFT window (must be a power of 2)
        step  = 50  # Step size for moving the window

        self._RFT( vec, ft, int(cmath.log(n, 2).real) )

        #----------------------------------------------------------------------
        # Nastavim vysledky do subMatrix listu
        #----------------------------------------------------------------------
        for i in range(n):
            points[i].set(vals={'a': abs(ft[i])})

        logger.info(f"{self.name}.RFT: Done")

    #--------------------------------------------------------------------------
    def _FFT( self, vec:list, fft:list[complex], rad:int, base:list[complex]|None=None, depth:int=0 ):
        """Compute Fast Fourier transform for list of real values in vector `vec`
        Cooley-Tukey FFT algorithm (odd-even decomposition).

        Parameters:
        - vec: input real values
        - fft: output complex Fourier coefficients (modified in-place)
        - rad: current radix level; size = 2^rad
        - base: base vector of twiddle factors z = e^(-i*2*pi*k/size) (created at depth=0)
        - depth: recursion depth (0 == top level where initialization happens)
        """

        if depth == 0: logger.info (f"{self.name}._FFT: Computing FFT with rad={rad}")
        else         : logger.debug(f"{self.name}._FFT: Recursion depth={depth}, rad={rad}")

        size  = 1 << rad       # 2^rad - FFT resolution at top level
        nasob = 1 << depth     # 2^depth - data stride (sample step) at current recursion level

        #----------------------------------------------------------------------
        # Initialize at top level (depth == 0)
        #----------------------------------------------------------------------
        if depth == 0:
            # Mutate fft in-place: clear and initialize with zeros
            fft.clear()
            fft.extend([0+0j] * size)

            # Create and initialize base vector with twiddle factors
            # base[k] = e^(-i*2*pi*k/size) for k=0..size/2-1
            # base[k+size/2] = -base[k] (symmetry: reduces computation)
            base = [0+0j] * size
            logger.debug(f"{self.name}._FFT: initialize twiddle factors (size={size})")

            theta = 2 * cmath.pi / size
            half = size // 2

            # First half: e^(-i*theta*k)
            for i in range(half):
                base[i] = cmath.exp(complex(0, -i * theta))

            # Second half: -base[k] for k in [0, half-1]
            # This exploits: e^(-i*theta*(half+k)) = -e^(-i*theta*k)
            for i in range(half, size):
                base[i] = -base[i - half]

        #----------------------------------------------------------------------
        # Base case: rad <= 1 (single 2-point FFT)
        # Computes: fft[k] = sum_{n=0,2,4,...} vec[n*nasob] * base[k*n % size]
        #----------------------------------------------------------------------
        if rad <= 1:
            logger.debug(f"{self.name}._FFT: base case FFT (rad={rad}, depth={depth}, size=2)")

            # Two-point FFT:
            # fft[0] = vec[0]*base[0] + vec[nasob]*base[0] = (vec[0] + vec[nasob]) * 1
            # fft[1] = vec[0]*base[0] + vec[nasob]*base[nasob] = vec[0] - vec[nasob] (since base[nasob]==-base[0])
            fft[0] = vec[0] * base[0] + vec[nasob] * base[0]
            fft[1] = vec[0] * base[0] + vec[nasob] * base[nasob]

            # Replicate results to fill the FFT array
            # At maximum frequency resolution, pattern repeats
            for i in range(2, len(fft), 2):
                fft[i] = fft[0]
                if i + 1 < len(fft):
                    fft[i + 1] = fft[1]

        else:
            # Recursive case: combine even (from lower recursion) and odd indices
            self._FFT(vec, fft, rad - 1, base, depth + 1)
            logger.debug(f"{self.name}._FFT: merging level {rad} (depth={depth})")

            # Butterfly operation: combine even-indexed terms (already in fft)
            # with odd-indexed terms (computed below)
            border = size
            if depth == 0:
                border //= 2  # FFT symmetry at top level

            # For each output frequency bin i in [0, border):
            # fft[i + k*size] += sum of odd-indexed input terms
            # This implements: X[k] = sum_{n even} + W^k * sum_{n odd}
            for i in range(border):
                z = 0 + 0j
                i_nas = i * nasob

                # Sum contributions from odd input indices (1, 3, 5, ...)
                # at stride nasob: vec[nasob], vec[3*nasob], vec[5*nasob], ...
                for j in range(1, size, 2):
                    idx = j * nasob
                    # Twiddle factor: base[(i_nas * j) % size]
                    # = e^(-i*2*pi*i*j/size) at this recursion level
                    base_idx = (i_nas * j) % len(base)
                    z += vec[idx] * base[base_idx]

                # Distribute combined result across all k such that k ≡ i (mod border)
                p = i
                while p < len(fft):
                    fft[p] += z
                    p += size

        #----------------------------------------------------------------------
        if depth == 0:
            logger.info(f"{self.name}._FFT: FFT computation complete (size={size})")

    #--------------------------------------------------------------------------
    def epochStep(self, valueKey:str, params:dict):
        """Compute next epoch state."""

        logger.info(f"{self.name}.epochStep: for key '{valueKey}' with params {params}")
        pts = 0


        logger.info(f"{self.name}.epochStep: {pts} InfoPoints was updated for key '{valueKey}' in epoch step")

    #--------------------------------------------------------------------------
    def rndBool(self, valueKey:str, params:dict):
        """Clear all model and set state as random Boolean values."""
        logger.debug(f"{self.name}.rndBool: for key '{valueKey}' with params {params}")
        pts = 0

        self.clearPoints(defs={valueKey: False})
        self.actSubmatrix( {'e': 0} )
        pts = self.applyMatrixMethod(methodKey='Random bit', valueKey=valueKey, params=params)
        self.actSubmatrix()

        logger.info(f"{self.name}.rndBool: {pts} InfoPoints was set to random Boolean values for key '{valueKey}'")

    #==========================================================================
    # Internal tools
    #--------------------------------------------------------------------------

    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f"InfoFieldLine ver {_VER}")

if __name__ == '__main__':

    logger.info("Testing InfoFieldLine class")

    #--------------------------------------------------------------------------
    # Test of the InfoFieldLine class
    #--------------------------------------------------------------------------
    imat = InfoFieldLine(name='imatTest')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
