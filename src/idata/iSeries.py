#==============================================================================
# Siqo class ISeries
#------------------------------------------------------------------------------
import cmath

from   .                      import logger
from   .idata                 import InfoData

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER   = '1.1.0'

_CNT   = 1200                          # Default number of points
_AXES  = {'i': 'Time tick'}            # Default axes
_VALS  = {'s': 'State', 'd': 'Delta'}  # Default values

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------

#==============================================================================
# ISeries
#------------------------------------------------------------------------------
class ISeries(InfoData):

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, dTime=1, cnt:dict|tuple=_CNT, axes:dict|tuple=_AXES, vals:dict|tuple=_VALS):
        """Calls constructor of ISeries, e.g. one-dimensional InfoData
        Parameters:
        - name   : Name of the ISeries object
        - dTime  : Time step between consecutive points in seconds
        - cnt    : Number of points in the series (default 1200)
        - axes   : Axes   of the series (default {'i': 'Time tick'})
        - vals   : Values of the series (default {'s': 'State', 'd': 'Delta'})
        """

        #----------------------------------------------------------------------
        # Super constructor
        #----------------------------------------------------------------------
        super().__init__(name)

        #----------------------------------------------------------------------
        # Datove polozky triedy
        #----------------------------------------------------------------------
        self.dTime = dTime     # Time step between consecutive points in seconds

        #----------------------------------------------------------------------
        # Schema setup
        #----------------------------------------------------------------------
        self.setIpType('ipSeries')
        self.setSchema({'axes': axes, 'vals': vals})

        #----------------------------------------------------------------------
        # Inicializacia cnt InfoPoints
        #----------------------------------------------------------------------
        self.init( cnts=(cnt,) )

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    # Dynamics methods for ISeries
    #--------------------------------------------------------------------------
    def mapSetMethods(self) -> dict:
        "Returns map of methods setting keyed value to function value for respective parameters"

        #----------------------------------------------------------------------
        # Get methods from super class
        #----------------------------------------------------------------------
        methods = super().mapSetMethods()

        #---------------------------------------------------------------------
        # Add ISeries specific methods
        #----------------------------------------------------------------------
        methods['ISeries deltas'      ] = {'dataMethod' : self.deltas
                                          ,'pointMethod':None
                                          ,'params'     :{}
                                          ,'visible'    :True
                                          ,'paramAsk'   :True
                                          ,'outData'    :None
                                          ,'outKey'     :'d'
                                          }
        methods['ISeries autocorr'    ] = {'dataMethod' : self.autoCorr
                                          ,'pointMethod':None
                                          ,'params'     :{}
                                          ,'visible'    :True
                                          ,'paramAsk'   :True
                                          ,'outData'    :'ICurve'
                                          ,'outKey'     :'ac'
                                          }

        #---------------------------------------------------------------------
        return methods

    #==========================================================================
    # Line methods to apply in Dynamics methods
    #--------------------------------------------------------------------------
    def deltas(self, inKey:str, outKey:str, params:dict, outData:'InfoData') -> int|None:
        """Compute deltas of states between consecutive points.
        - inKey  : Key of the value to be read by the method
        - outKey : Key of the value to be set by the method
        - params : Parameters for the method as dict
        - outData: InfoData to store output data
        Returns count of updated InfoPoints or None if initialization failed due to incompatible parameters or undefined ipType.
        """

        logger.info(f"{self.name}.deltas: {outData.name}[{outKey}] = <Deltas>({inKey}) with params {params}")
        pts = 0

        #----------------------------------------------------------------------
        # Ziskam pracovny zoznam InfoPoints na aplikovanie metody (subData)
        #----------------------------------------------------------------------
        points = self.actList

        prevS = 0
        points[0].set( vals = {outKey: prevS} )

        #----------------------------------------------------------------------
        # Prejdem vsetky body v subdata a pre kazdy bod nastavim hodnotu ako rozdiel medzi hodnotou bodu a predosleho bodu
        #----------------------------------------------------------------------
        for i in range(1, len(points)):

            point = points[i]
            currS = point.val(valKey='s')

            #------------------------------------------------------------------
            # Vypocet a nastavenie delty
            #------------------------------------------------------------------
            delta = currS - prevS
            point.set( vals = {outKey: delta})

            #------------------------------------------------------------------
            # Posun na nasledujuci bod
            #------------------------------------------------------------------
            prevS = currS
            pts += 1

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.deltas: {pts} InfoPoints was updated for key '{outKey}' in deltas")

    #--------------------------------------------------------------------------
    def autoCorr(self, inKey:str, outKey:str, params:dict, outData:'InfoData') -> int|None:
        """Compute auto-correlation of states.
        - inKey  : Key of the value to be read by the method
        - outKey : Key of the value to be set by the method
        - params : Parameters for the method as dict
        - outData: InfoData to store output data
        Returns count of updated InfoPoints or None if initialization failed due to incompatible parameters or undefined ipType.
        """

        logger.info(f"{self.name}.autoCorr: {outData.name}[{outKey}] = <AutoCorr>({inKey}) with params {params}")

        #----------------------------------------------------------------------
        # Ziskam pracovny zoznam InfoPoints na aplikovanie metody (subData)
        #----------------------------------------------------------------------
        points = self.actList
        n = len(points)

        #----------------------------------------------------------------------
        # Prejdem tau od 0 po N-1, kde N je pocet bodov v subdata
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

                iVal = points[iPos].val(valKey='s')
                jVal = points[jPos].val(valKey='s')

                prod = iVal * jVal
                if prod > maxP: maxP = prod

                suma += prod

            #------------------------------------------------------------------
            # Normujem sumu podla poctu bodov a nastavim hodnotu auto-korelacie pre tau
            #------------------------------------------------------------------
            points[tau].set(vals={outKey: (suma/n) })

        #----------------------------------------------------------------------
        # Posledny bod nastavim na 0
        #----------------------------------------------------------------------
        points[n-1].set(vals={outKey: 0})

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.autoCorr: Done")

    #--------------------------------------------------------------------------
    def autoPhaseCorr(self, inKey:str, outKey:str, params:dict, outData:'InfoData') -> int|None:
        """Compute auto-correlation of states for each phase.
        - inKey  : Key of the value to be read by the method
        - outKey : Key of the value to be set by the method
        - params : Parameters for the method as dict
        - outData: InfoData to store output data
        Returns count of updated InfoPoints or None if initialization failed due to incompatible parameters or undefined ipType.
        """

        logger.info(f"{self.name}.autoPhaseCorr: {outData.name}[{outKey}] = <AutoPhaseCorr>({inKey}) with params {params}")

        #----------------------------------------------------------------------
        # Ziskam pracovny zoznam InfoPoints na aplikovanie metody (subData)
        #----------------------------------------------------------------------
        points = self.actList
        n = len(points)

        #----------------------------------------------------------------------
        # Prejdem tau od 0 po N-1, kde N je pocet bodov v subdata
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

                iVal = points[iPos].val(valKey='s')
                jVal = points[jPos].val(valKey='s')

                prod = iVal * jVal
                if prod > maxP: maxP = prod

                suma += prod

            #------------------------------------------------------------------
            # Normujem sumu podla poctu bodov a nastavim hodnotu auto-korelacie pre tau
            #------------------------------------------------------------------
            points[tau].set(vals={outKey: (suma/n) })

        #----------------------------------------------------------------------
        # Posledny bod nastavim na 0
        #----------------------------------------------------------------------
        points[n-1].set(vals={outKey: 0})

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.autoPhaseCorr: Done")

    #--------------------------------------------------------------------------
    def RFT(self, inKey:str, outKey:str, params:dict, outData:'InfoData') -> int|None:
        """Compute Fast Fourier transform of real states in subdata.
        - inKey  : Key of the value to be read by the method
        - outKey : Key of the value to be set by the method
        - params : Parameters for the method as dict
        -- 'rad' : radix level for FFT e.g. size = 2^rad (default 0 for dynamic rad)
        - outData: InfoData to store output data
        """

        logger.info(f"{self.name}.RFT: {outData.name}[{outKey}] = <RFT>({inKey}) with params {params}")

        #----------------------------------------------------------------------
        # Ziskam pracovny zoznam InfoPoints na aplikovanie metody (subData)
        #----------------------------------------------------------------------
        points = self.actList
        n = len(points)

        vec = [0.0] * n
        for i in range(n):
            vec[i] = points[i].val(valKey='s')

        #----------------------------------------------------------------------
        # Ak je rad == 0, tak nastavim rad na najvacsiu mocninu dvojky mensiu ako n
        #----------------------------------------------------------------------
        rad  = params.get('rad', 0 )
        if rad == 0:  rad = int(cmath.log(n, 2).real)

        #----------------------------------------------------------------------
        # Inicializujem okno a skontrolujem vykonatelnost
        #----------------------------------------------------------------------
        size  = 1 << rad
        resid = n - size
        start = 0
        fft   = [0+0j] * size  # Initialize FFT output vector with complex zeros

        if resid < 0:
            logger.error(f"{self.name}.RFT: Not enough points for FFT (n={n}, rad={rad}, size={size})")
            return

        logger.info(f"{self.name}.RFT: rad set to {rad}, size = {size}")

        #----------------------------------------------------------------------
        # Posuvam okno vec[] s dlzkou size o krok step az kym reziduum nebude mensie ako 16
        #----------------------------------------------------------------------
        while resid >= 16:

            #------------------------------------------------------------------
            # Ak je reziduum > 0, tak mozem vykonat FFT pre okno vec[start:start+size]
            #------------------------------------------------------------------
            if resid > 0:
                logger.info(f"{self.name}.RFT: FFT window start={start}, stop={size}, resid={resid}")

                #--------------------------------------------------------------
                # Vytvorim vektor fft pre FFT vysledky a zavolam FFT
                #--------------------------------------------------------------
                fftLocal = [0+0j] * size
                self._FFT( vec[start:start+size], fftLocal, rad )

                #--------------------------------------------------------------
                # Pripocitam fftLocal do fft pre indexy, ktore boli aktualizovane.
                #--------------------------------------------------------------
                for i in range(size):
                    fft[i] += fftLocal[i]

                #--------------------------------------------------------------
                # Posuniem okno o krok size a aktualizujem reziduum
                #--------------------------------------------------------------
                start += size
                resid -= size

            else:
                #--------------------------------------------------------------
                # Ak je reziduum < 0, znizim rad o 1 a skusim znova
                #--------------------------------------------------------------
                #rad  -= 1
                #size  = 1 << rad
                resid = n - size

        #----------------------------------------------------------------------
        # Ak je reziduum > 0, vykonam FFT pre celu zvysnu cast
        #----------------------------------------------------------------------
        if resid > 0:
            fftLocal = [0+0j] * size
            self._FFT( vec[start:start+size] + [0]*(size-resid), fftLocal, rad )
            for i in range(size):
                fft[i] += fftLocal[i]

        #----------------------------------------------------------------------
        # Nastavim vysledky do subdata listu
        #----------------------------------------------------------------------
        for i in range(n):
            points[i].set(vals={outKey: abs(fft[i])})

        logger.info(f"{self.name}.RFT: {outData.name}[{outKey}] = <RFT>({inKey}) Done")

    #--------------------------------------------------------------------------
    def rndBool(self, inKey:str, outKey:str, params:dict, outData:'InfoData') -> int|None:
        """Clear all model and set state as random Boolean values.
        """

        logger.info(f"{self.name}.rndBool: {outData.name}[{outKey}] = <RFT>({inKey}) with params {params}")
        pts = 0

        self.clearPoints(defs={outKey: False})
        self.actSubData( {'e': 0} )
        pts = self.applyDataMethod(methodKey='Random bit', valueKey=outKey, params=params)
        self.actSubData()

        logger.info(f"{self.name}.rndBool: {pts} InfoPoints was set to random Boolean values for key '{outKey}'")

    #==========================================================================
    # Internal tools
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

        Returns:
        - fft: modified in-place with computed Fourier coefficients
        - index k of fft corresponds to frequency bin:
        -- for k = 0 → DC zložka (signal average, frequency = 0)
        -- for k = 1..size/2-1 → positive frequencies
        -- for k = size/2 → Nyquist frequency (if size is even)
        -- f(k) = k * (sampling_frequency / size) for k in [0, size/2]
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

    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f"ISeries ver {_VER}")

if __name__ == '__main__':

    logger.info("Testing ISeries class")

    #--------------------------------------------------------------------------
    # Test of the ISeries class
    #--------------------------------------------------------------------------
    imat = ISeries(name='imatTest')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
