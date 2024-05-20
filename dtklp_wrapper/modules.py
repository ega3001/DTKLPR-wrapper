import ctypes as ct
import os


class Lib:
    """Wraps over DTKLP library"""

    def __init__(self, lib_path: str, buffer_size: int):
        """Init library with settings
            
            Parameters:
                lib_path: path to .dll, .so etc
                buffer_size: size of buffer which used for transfer data
        """
        
        self.lib = ct.CDLL(lib_path)
        self.BUF_SIZE = buffer_size
    
    def create_params(self):
        """Creates LPRParams object
            
            Returns:
                object: LPRParams
        """

        return self.lib.LPRParams_Create()
    
    def destroy_params(self, params_obj):
        """Destroys LPRParams object
            
            Parameters:
                params_obj: LPRParams object
        """
        
        self.lib.LPRParams_Destroy(params_obj)

    def create_engine(self, params_obj, vid_mode, callback):
        """Creates LPREngine object
            
            Parameters:
                params_obj: LPRParams object
                vid_mode: if True engine will accept only video, otherwise only images
                callback: callback function pointer, used in video mode, for backend notification
            Returns:
                object: LPREngine
        """
        
        return self.lib.LPREngine_Create(params_obj, vid_mode, callback)
    
    def destroy_engine(self, enigne_obj):
        """Destroys LPREngine object

            Parameters:
                enigne_obj: LPREngine object
        """
        
        self.lib.LPREngine_Destroy(enigne_obj)

    def read_from_mem(self, engine_obj, buffer):
        """Process image bytes

            Parameters:
                engine_obj: LPREngine object
                buffer: image bytes
            Returns:
                object: LPRResult
        """
        
        ba = bytearray(buffer)
        data = ct.create_string_buffer(bytes(ba), len(ba))
        return self.lib.LPREngine_ReadFromMemFile(engine_obj, data, len(ba))
    
    def destroy_result(self, result_obj):
        """Destroys LPRResult object

            Parameters:
                result_obj: LPRResult object
        """

        self.lib.LPRResult_Destroy(result_obj)
    
    def get_plates_count(self, result_obj):
        """Returns detected license plates count

            Parameters:
                result_obj: LPRResult object
            Returns:
                int: detected count
        """

        return self.lib.LPRResult_GetPlatesCount(result_obj)
    
    def get_plate(self, result_obj, index: int):
        """Returns LicensePlate object

            Parameters:
                result_obj: LPRResult object
                index: detected object index
            Returns:
                object: LicensePlate
        """

        return self.lib.LPRResult_GetPlate(result_obj, index)
    
    def destroy_plate(self, plate_obj):
        """Destroys LicensePlate object

            Parameters:
                plate_obj: LicensePlate object
        """

        self.lib.LicensePlate_Destroy(plate_obj)
    
    def get_plate_text(self, plate_obj):
        """Returns LicensePlate detected number

            Parameters:
                plate_obj: LicensePlate object
            Returns:
                str: number text
        """

        data = ct.create_string_buffer(self.BUF_SIZE)
        writen = self.lib.LicensePlate_GetText(plate_obj, data, self.BUF_SIZE)
        return str(data.value[0:writen])
    
    def engine_licensed(self, engine_obj):
        """Check license for LPREngine

            Parameters:
                engine_obj: LPREngine object
            Returns:
                int: 0 is ok, otherwise error code
        """

        return self.lib.LPREngine_IsLicensed(engine_obj)
    
    def activate_online(self, key: str):
        """Trying activate license with key

            Parameters:
                key: license key
            Returns:
                int: 0 is success, otherwise error code
        """

        ba = bytearray(key.encode())
        data = ct.create_string_buffer(bytes(ba), len(ba))
        return self.lib.LPREngine_ActivateLicenseOnline(data)


class EngineParams:
    """Wraps over LPRParams object"""

    def __init__(self, lib: Lib):
        """Binds lib with object

            Parameters: Lib object for bind
        """
        
        self.lib = lib

    def __enter__(self):
        """Creates LPRParams object"""

        self.obj = self.lib.create_params()
        return self.obj
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Destroys LPRParams object"""

        self.lib.destroy_params(self.obj)


class ImageEngine:
    """Wraps over LPREngine object"""

    def __init__(self, lib, params: EngineParams = None):
        """Binds lib and params with object

            Parameters:
                lib: Lib object
                params: EngineParams object
        """
        
        self.lib = lib
        self.params = params
    
    def __enter__(self):
        """Initialize LPREngine object for processing images"""

        if not self.params:
            self.params = EngineParams(self.lib)
        with self.params as ep:
            self.obj = self.lib.create_engine(ep, False, None)
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Destroys LPREngine object"""

        self.lib.destroy_engine(self.obj)

    def is_licensed(self):
        """Checks engine license
        
            Parameters:
                bool: True if licensed
        """

        res = self.lib.engine_licensed(self.obj)
        return res == 0
    
    def activate(self, key):
        """Tries activate license

            Parameters:
                key: license key
            Returns:
                bool: True if activation success
        """

        res = self.lib.activate_online(key)
        return res == 0

    def process(self, bytes):
        """Process image bytes

            Parameters:
                bytes: image bytes
            Returns:
                dict: {"found": int, "plates": [str,]}
        """

        res = Result(self.lib.read_from_mem(bytes), self.lib)
        with res:
            return res.describe()

    
class Result():
    """Wraps over LPRResult object"""

    def __init__(self, obj, lib: Lib):
        """Binds lib and LPRResult object
        
            Parameters:
                obj: LPRResult object
                lib: Lib object
        """

        self.obj = obj
        self.lib = lib

    def __enter__(self):
        """Loads data about LPRResult"""

        self._load()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Destroys LPRResult object"""

        self.lib.destroy_result(self.obj)

    def _load(self):
        self.plates_count = self.lib.get_plates_count(self.obj)
        self.plates = []
        for i in range(self.plates_count):
            with Plate(self.lib.get_plate(self.obj, i), self.lib) as pl:
                self.plates.append(pl.describe())
    
    def describe(self):
        """Returns description

            Returns:
                dict: {"found": int, "plates": [str,]}
        """

        return {
            "found": self.plates_count,
            "plates": self.plates
        }
    

class Plate():
    """Wraps over LicensePlate object"""

    def __init__(self, obj, lib: Lib):
        """Binds object and lib

            Parameters:
                obj: LicansePlate object
                lib: Lib object
        """

        self.obj = obj
        self.lib = lib

    def __enter__(self):
        """Loads data about LicensePlate object"""

        self._load()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Destroys LicensePlate object"""

        self.lib.destroy_plate(self.obj)

    def _load(self):
        self.text = self.lib.get_plate_text(self.obj)

    def describe(self):
        """Returns description

            Returns:
                str: plate detected text
        """

        return self.text
