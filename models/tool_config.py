import configparser
from ntpath import join
from sys import path
import time
from os import makedirs
from pathlib import Path

import threading
import enum
import os

# Better to explicitly pass if to be honest: for all Models

#ToolConfig with open fields and is a inside the models.
# SingleTone which can be only passed!!! YEAH!
# Used by many models.
# Passed to them? - Yes

class ToolConfig(object):
    _instance = None
    _initialized = False
    _lock = threading.Lock()

    class ModeEnum(enum.Enum):
        Base = 0
        Debug = 1


    class PatientType:
        def __init__(self, config):
            self.config = config

            self.__name = self.config['patient_info']['patient_name']
    
            self.__date = self.config['patient_info']['patient_date']
            self.__auto_date = self.config['general'].getboolean('patient_date_autogeneration')
    
            self.__time = self.config['patient_info']['patient_time']
            self.__auto_time = self.config['general'].getboolean('patient_time_autogeneration')
    
            self.__data_path = self.config['paths']['patient_data_path']
            self.__experiment_data_path = self.config['paths']['experiment_data_path']
            self.__results_path = self.config['paths']['results_path'] 

        @property
        def Name(self):
            return self.__name
    
        @Name.setter
        def Name(self, var):
            self.__name = var
            self.config['patient_info']['patient_name'] = self.__name

        @property
        def Date(self):
            return self.__date
    
        @Date.setter
        def Date(self, var):
            self.__date = var
            self.config['patient_info']['patient_date'] = self.__date

        @property
        def AutoDate(self):
            return self.__auto_date
    
        @AutoDate.setter
        def AutoDate(self, var):
            self.__auto_date = var
            self.config['general'].setboolean('patient_date_autogeneration', self.__auto_date)

        @property
        def Time(self):
            return self.__time
    
        @Time.setter
        def Time(self, var):
            self.__time = var
            self.config['patient_info']['patient_time'] = self.__time

        @property
        def AutoTime(self):
            return self.__auto_time
    
        @AutoTime.setter
        def AutoTime(self, var):
            self.__auto_time = var
            self.config['general'].setboolean('patient_time_autogeneration', self.__auto_time)

        @property
        def DataPath(self):
            return self.__data_path
    
        @DataPath.setter
        def DataPath(self, var):
            self.__data_path = var
            self.config['paths']['patient_data_path'] = self.__data_path

        @property
        def ExperimentDataPath(self):
            return self.__experiment_data_path
    
        @ExperimentDataPath.setter
        def ExperimentDataPath(self, var):
            self.__experiment_data_path = var
            self.config['paths']['experiment_data_path'] = self.__experiment_data_path

        @property
        def ResultsPath(self):
            return self.__results_path
    
        @ResultsPath.setter
        def ResultsPath(self, var):
            self.__results_path = var
            self.config['paths']['results_path'] = self.__results_path

        def __str__(self):
            return '    Patient:\n' + \
                   '        Name: ' + self.Name + '\n' + \
                   '        Date: ' + self.Date + '\n' + \
                   '        AutoDate: ' + str(self.AutoDate) + '\n' + \
                   '        Time: ' + self.Time + '\n' + \
                   '        AutoTime: ' + str(self.AutoTime) + '\n' + \
                   '        DataPath: ' + self.DataPath + '\n' + \
                   '        ExperimentDataPath: ' + self.ExperimentDataPath + '\n' + \
                   '        ResultsPath: ' + self.ResultsPath + '\n'

    class StimuliType:
        def __init__(self, config):
            self.config = config

            self.__action_pictures = ToolConfig.StimuliType.ActionPicturesType(config)
            self.__object_pictures = ToolConfig.StimuliType.ObjectPicturesType(config)
            self.__other_pictures  = ToolConfig.StimuliType.OtherPicturesType(config)
            self.__sound           = ToolConfig.StimuliType.SoundType(config)

        class PicturesType:
            def __init__(self, config):
                self.config = config

                self._path_to_config = None
                self._time = -1

            @property
            def PathToConfig(self):
                return self._path_to_config

            @PathToConfig.setter
            def PathToConfig(self, var):
                self._path_to_config = var
                self.config['paths']['pictures_' + 
                                     self.__class__.__name__.replace('PicturesType', '').lower() +
                                    's_path'] = self._path_to_config

            @property
            def Time(self):
                return self._time

            @Time.setter
            def Time(self, var):
                self._time = var
                self.config['display']['pictures_' +
                                        self.__class__.__name__.replace('PicturesType', '').lower() + '_time'] = \
                    str(self._time)

        class ActionPicturesType(PicturesType):
            def __init__(self, config):
                self.config = config

                self._path_to_config = self.config['paths']['pictures_actions_path']
                self._time = self.config['display'].getfloat('pictures_action_time')

            def __str__(self):
                return '        ActionPictures:\n' + \
                       '            PathToConfig: ' + self.PathToConfig + '\n' + \
                       '            Time: ' + str(self.Time) + '\n'

        @property
        def ActionPictures(self):
            return self.__action_pictures

        @ActionPictures.setter
        def ActionPictures(self, var):
            self.__action_pictures.PathToConfig = var.PathToConfig
            self.__action_pictures.Time = var.Time

        class ObjectPicturesType(PicturesType):
            def __init__(self, config):
                self.config = config

                self._path_to_config = self.config['paths']['pictures_objects_path']
                self._time = self.config['display'].getfloat('pictures_object_time')

            def __str__(self):
                return '        ObjectPictures:\n' + \
                       '            PathToConfig: ' + self.PathToConfig + '\n' + \
                       '            Time: ' + str(self.Time) + '\n'

        @property
        def ObjectPictures(self):
            return self.__object_pictures

        @ObjectPictures.setter
        def ObjectPictures(self, var):
            self.__object_pictures.PathToConfig = var.PathToConfig
            self.__object_pictures.Time = var.Time

        class OtherPicturesType(PicturesType):
            def __init__(self, config):
                self.config = config

                self._path_to_config = self.config['paths']['pictures_others_path']
                self._time = self.config['display']['time_other_pictures']

            def __str__(self):
                return '        OtherPictures:\n' + \
                       '            PathToConfig: ' + self.PathToConfig + '\n' +\
                       '            Time: ' + self.Time + '\n'

        @property
        def OtherPictures(self):
            return self.__other_pictures

        @OtherPictures.setter
        def OtherPictures(self, var):
            self.__other_pictures.PathToConfig = var.PathToConfig
            self.__other_pictures.Time = var.Time

        class SoundType:
            def __init__(self, config):
                self.config = config

                self.__path = self.config['paths']['tone_path']

            @property
            def Path(self):
                return self.__path

            @Path.setter
            def Path(self, var):
                self.__path = var
                self.config['paths']['tone_path'] = self.__path

            def __str__(self):
                return '        Sound:\n' + \
                       '            Path: ' + self.Path + '\n'

        @property
        def Sound(self):
            return self.__sound

        @Sound.setter
        def Sound(self, var):
            self.__sound.Path = var.Path

        def __str__(self):
            return '    Stimuli:\n' + \
                        str(self.ActionPictures) + \
                        str(self.ObjectPictures) + \
                        str(self.OtherPictures) + \
                        str(self.Sound)

    class PresentationType:
        class OrderEnum(enum.Enum):
            Sequential = 0
            Random = 1

        def __init__(self, config):
            self.config = config

            self.__patient_display             = ToolConfig.PresentationType.PatientDisplayType(config)
            self.__duration                    = ToolConfig.PresentationType.DurationType(config)
            self.__order                       = ToolConfig.PresentationType.OrderEnum.Random \
                                                     if self.config['display'].getboolean('shuffle_pictures') else \
                                                 ToolConfig.PresentationType.OrderEnum.Sequential        
            self.__rotate_pictures             = self.config['display'].getboolean('rotate_pictures') # orientation
            self.__play_sound_between_pictures = self.config['display'].getboolean('sound_between_pictures')

        class PatientDisplayType:
            def __init__(self, config):
                self.config = config

                # ???
                self.__width = self.config['display'].getint('window_x')
                self.__height = self.config['display'].getint('window_y')

            @property
            def Width(self):
                return self.__width

            @Width.setter
            def Width(self, var):
                self.__width = var
                self.config['display'].setint('window_x', self.__width)

            @property
            def Height(self):
                return self.__height

            @Height.setter
            def Height(self, var):
                self.__height = var
                self.config['display'].setint('window_y', self.__height)

            def __str__(self):
                return '        PatientDisplay:\n' + \
                       '            Width: ' + str(self.Width) + '\n' + \
                       '            Height: ' + str(self.Height) + '\n'

        @property
        def PatientDisplay(self):
            return self.__patient_display

        @PatientDisplay.setter
        def PatientDisplay(self, var):
            self.__patient_display.Width = var.Width
            self.__patient_display.Height = var.Height

        class DurationType:
            def __init__(self, config):
                self.config = config

                self.__resting = self.config['display'].getfloat('resting_time')
                self.__picture = self.config['display'].getfloat('single_picture_time')
                self.__between_picture = self.config['display'].getfloat('time_between_pictures')
                self.__other_picture = self.config['display'].getfloat('time_other_pictures')

            @property
            def Resting(self):
                return self.__resting

            @Resting.setter
            def Resting(self, var):
                self.__resting = var
                self.config['display']['resting_time'] = str(self.__resting)

            @property
            def Picture(self):
                return self.__picture

            @Picture.setter
            def Picture(self, var):
                self.__picture = var
                self.config['display']['single_picture_time'] = str(self.__picture)

            @property
            def BetweenPicture(self):
                return self.__between_picture

            @BetweenPicture.setter
            def BetweenPicture(self, var):
                self.__between_picture = var
                self.config['display']['time_between_pictures'] = str(self.__between_picture)

            @property
            def OtherPicture(self):
                return self.__other_picture

            @OtherPicture.setter
            def OtherPicture(self, var):
                self.__other_picture = var
                self.config['display']['time_other_pictures'] = str(self.__other_picture)

            def __str__(self):
                return '        Duration:\n' + \
                       '            Resting: ' + str(self.Resting) + '\n' + \
                       '            Picture: ' + str(self.Picture) + '\n' + \
                       '            BetweenPicture: ' + str(self.BetweenPicture) + '\n' + \
                       '            OtherPicture: ' + str(self.OtherPicture) + '\n'

        @property
        def Duration(self):
            return self.__duration

        @Duration.setter
        def Duration(self, var):
            self.__duration.Resting = var.Resting
            self.__duration.Picture = var.Picture
            self.__duration.BetweenPicture = var.BetweenPicture
            self.__duration.OtherPicture = var.OtherPicture

        @property
        def Order(self):
            return self.__order

        @Order.setter
        def Order(self, var):
            self.__order = var
            self.config['display']['shuffle_pictures'] = True \
                if self.__order is ToolConfig.PresentationType.OrderEnum.Sequential else False
        @property
        def RotatePictures(self):
            return self.__rotate_pictures

        @RotatePictures.setter
        def RotatePictures(self, var):
            self.__rotate_pictures = var
            self.config['display'].setboolean('rotate_pictures', self.__rotate_pictures)

        @property
        def PlaySoundBetweenPictures(self):
            return self.__play_sound_between_pictures

        @PlaySoundBetweenPictures.setter
        def PlaySoundBetweenPictures(self, var):
            self.__play_sound_between_pictures = var
            self.config['display'].setboolean('sound_between_pictures', self.__play_sound_between_pictures)

        def __str__(self):
            return '    Presentation:\n' + \
                        str(self.PatientDisplay) + \
                        str(self.Duration) + \
                   '        Order: ' + str(self.Order) + '\n' + \
                   '        RotatePictures: ' + str(self.RotatePictures) + '\n' + \
                   '        PlaySoundBetweenPictures: ' + str(self.PlaySoundBetweenPictures) + '\n'

    class WorkingDirectoryType:
        def __init__(self, config):
            self.config = config

            self.__root_path = self.config['paths']['root_path']
            self.__auto_root_path = self.config['general'].getboolean('root_path_autogeneration')
            self.__lsl_stream_generator_path = self.config['paths']['lsl_stream_generator_path']
            self.__make_folders = self.config['general'].getboolean('make_folders')

        @property
        def RootPath(self):
            return self.__root_path

        @RootPath.setter
        def RootPath(self, var):
            self.__root_path = var
            self.config['paths']['root_path'] = self.__root_path

        @property
        def AutoRootPath(self):
            return self.__auto_root_path

        @AutoRootPath.setter
        def AutoRootPath(self, var):
            self.__auto_root_path = var
            self.config['general'].setboolean('root_path_autogeneration', self.__auto_root_path)

        @property
        def LSLStreamGeneratorPath(self):
            return self.__lsl_stream_generator_path

        @LSLStreamGeneratorPath.setter
        def LSLStreamGeneratorPath(self, var):
            self.__lsl_stream_generator_path = var
            self.config['paths']['lsl_stream_generator_path'] = self.__lsl_stream_generator_path

        @property
        def MakeFolders(self):
            return self.__make_folders

        @MakeFolders.setter
        def MakeFolders(self, var):
            self.__make_folders = var
            self.config['general'].setboolean('make_folders', self.__make_folders)

        def __str__(self):
            return '    WorkingDirectory:\n' + \
                   '        RootPath: ' + self.RootPath + '\n' + \
                   '        AutoRootPath: ' + str(self.AutoRootPath) + '\n' + \
                   '        LSLStreamGeneratorPath: ' + self.LSLStreamGeneratorPath + '\n' + \
                   '        MakeFolders: ' + str(self.MakeFolders) + '\n'

    class RecorderType:
        def __init__(self, config):
            self.config = config

            self.__groups = self.config['recorder']['group_names']
            self.__lsl_stream_name = self.config['recorder']['lsl_stream_name']
            self.__frequency = self.config['recorder'].getint('fs')
            self.__dataset_width = self.config['recorder'].getint('dataset_width')

        @property
        def Groups(self):
            return self.__groups

        @Groups.setter
        def Groups(self, var):
            self.__groups = var
            self.config['recorder']['group_names'] = self.__groups

        @property
        def LSLStreamName(self):
            return self.__lsl_stream_name

        @LSLStreamName.setter
        def LSLStreamName(self, var):
            self.__lsl_stream_name = var
            self.config['recorder']['lsl_stream_name'] = self.__lsl_stream_name

        @property
        def Frequency(self):
            return self.__frequency

        @Frequency.setter
        def Frequency(self, var):
            self.__frequency = var
            self.config['recorder'].setint('fs', self.__frequency)

        @property
        def DatasetWidth(self):
            return self.__dataset_width

        @DatasetWidth.setter
        def DatasetWidth(self, var):
            self.__dataset_width = var
            self.config['recorder'].setint('dataset_width', self.__dataset_width)

        def __str__(self):
            return '    Recorder:\n' + \
                   '        Groups: ' + str(self.Groups) + '\n' + \
                   '        LSLStreamName: ' + self.LSLStreamName + '\n' + \
                   '        Frequency: ' + str(self.Frequency) + '\n' + \
                   '        DatasetWidth: ' + str(self.DatasetWidth) + '\n'

    class DecoderType:
        def __init__(self, config):
            self.config = config

            self.__dec = self.config['decoder'].getint('dec')
            self.__fmax = self.config['decoder'].getint('fmax')
            self.__fmin = self.config['decoder'].getint('fmin')
            self.__fstep = self.config['decoder'].getint('fstep')
            self.__th50hz =  self.config['decoder'].getint('th50hz')
            self.__grid_width = self.config['decoder'].getint('grid_size_x')
            self.__grid_height =  self.config['decoder'].getint('grid_size_y')
            self.__grid_channel_from =  self.config['decoder'].getint('grid_channel_from')
            self.__grid_channel_to = self.config['decoder'].getint('grid_channel_to')
            self.__use_interval = self.config['decoder'].getboolean('use_interval')
            self.__interval_start = self.config['decoder'].getfloat('interval_start')
            self.__interval_stop = self.config['decoder'].getfloat('interval_stop')
            self.__measure = self.config['decoder']['measure'] # Enum?

        @property
        def Dec(self):
            return self.__dec

        @Dec.setter
        def Dec(self, var):
            self.__dec = var
            self.config['decoder'].setint('dec', self.__dec)

        @property
        def FMax(self):
            return self.__fmax

        @FMax.setter
        def FMax(self, var):
            self.__fmax = var
            self.config['decoder'].setint('fmax', self.__fmax)

        @property
        def FMin(self):
            return self.__fmin

        @FMin.setter
        def FMin(self, var):
            self.__fmin = var
            self.config['decoder'].setint('fmin', self.__fmin)

        @property
        def FStep(self):
            return self.__fstep

        @FStep.setter
        def FStep(self, var):
            self.__fstep = var
            self.config['decoder'].setint('fstep', self.__fstep)

        @property
        def Th50hz(self):
            return self.__th50hz

        @Th50hz.setter
        def Th50hz(self, var):
            self.__th50hz = var
            self.config['decoder'].setint('th50hz', self.__th50hz)

        @property
        def GridWidth(self):
            return self.__grid_width

        @GridWidth.setter
        def GridWidth(self, var):
            self.__grid_width = var
            self.config['decoder'].setint('grid_size_x', self.__grid_width)

        @property
        def GridHeight(self):
            return self.__grid_height

        @GridHeight.setter
        def GridHeight(self, var):
            self.__grid_height = var
            self.config['decoder'].setint('grid_size_y', self.__grid_height)

        @property
        def GridChannelFrom(self):
            return self.__grid_channel_from

        @GridChannelFrom.setter
        def GridChannelFrom(self, var):
            self.__grid_channel_from = var
            self.config['decoder'].setint('grid_channel_from', self.__grid_channel_from)

        @property
        def GridChannelTo(self):
            return self.__grid_channel_to

        @GridChannelTo.setter
        def GridChannelTo(self, var):
            self.__grid_channel_to = var
            self.config['decoder'].setint('grid_channel_to', self.__grid_channel_to)

        @property
        def UseInterval(self):
            return self.__use_interval

        @UseInterval.setter
        def UseInterval(self, var):
            self.__use_interval = var
            self.config['decoder'].setboolean('use_interval', self.__use_interval)

        @property
        def IntervalStart(self):
            return self.__interval_start

        @IntervalStart.setter
        def IntervalStart(self, var):
            self.__interval_start = var
            self.config['decoder'].setfloat('interval_start', self.__interval_start)

        @property
        def IntervalStop(self):
            return self.__interval_stop

        @IntervalStop.setter
        def IntervalStop(self, var):
            self.__interval_stop = var
            self.config['decoder'].setfloat('interval_stop', self.__interval_stop)

        @property
        def Measure(self):
            return self.__measure

        @Measure.setter
        def Measure(self, var):
            self.__measure = var
            self.config['decoder']['measure'] = self.__measure

        def __str__(self):
            return '    Decoder:\n' + \
                   '        Dec: ' + str(self.Dec) + '\n' + \
                   '        FMax: ' + str(self.FMax) + '\n' + \
                   '        FMin: ' + str(self.FMin) + '\n' + \
                   '        FStep: ' + str(self.FStep) + '\n' + \
                   '        Th50z: ' + str(self.Th50hz) + '\n' + \
                   '        GridWidth: ' + str(self.GridWidth) + '\n' + \
                   '        GridHeight: ' + str(self.GridHeight) + '\n' + \
                   '        GridChannelFrom: ' + str(self.GridChannelFrom) + '\n' + \
                   '        GridChannelTo: ' + str(self.GridChannelTo) + '\n' + \
                   '        UseInterval: ' + str(self.UseInterval) + '\n' + \
                   '        IntervalStart: ' + str(self.IntervalStart) + '\n' + \
                   '        IntervalStop: ' + str(self.IntervalStop) + '\n' + \
                   '        Measure: ' + self.Measure + '\n'

    @property
    def Mode(self):
        return self.__mode

    @Mode.setter
    def Mode(self, var):
        self.__mode = var
        self.config['general'].setboolean('debug_mode', True) \
            if self.__mode is ToolConfig.ModeEnum.Debug else \
        self.config['general'].setboolean('debug_mode', False)

    @property
    def Patient(self):
        return self.__patient

    @Patient.setter
    def Patient(self, var):
        self.__patient.Name = var.Name
        self.__patient.Date = var.Date
        self.__patient.AutoDate = var.AutoDate
        self.__patient.Time = var.Time
        self.__patient.AutoTime = var.AutoTime
        self.__patient.DataPath = var.DataPath
        self.__patient.ExperimentDataPath = var.ExperimentDataPath
        self.__patient.ResultsPath = var.ResultsPath

    @property
    def Stimuli(self):
        return self.__stimuli

    @Stimuli.setter
    def Stimuli(self, var):
        self.__stimuli.ActionPictures = var.ActionPictures
        self.__stimuli.ObjectPictures = var.ObjectPictures
        self.__stimuli.OtherPictures = var.OtherPictures
        self.__stimuli.Sound = var.Sound

    @property
    def Presentation(self):
        return self.__presentation

    @Presentation.setter
    def Presentation(self, var):
        self.__presentation.PatientDisplay = var.PatientDisplay
        self.__presentation.Duration = var.Duration
        self.__presentation.Order = var.Order
        self.__presentation.RotatePictures = var.RotatePictures
        self.__presentation.PlaySoundBetweenPictures = var.PlaySoundBetweenPictures

    @property
    def WorkingDirectory(self):
        return self.__working_directory

    @WorkingDirectory.setter
    def WorkingDirectory(self, var):
        self.__working_directory.RootPath = var.RootPath
        self.__working_directory.AutoRootPath = var.AutoRootPath
        self.__working_directory.LSLStreamGeneratorPath = var.LSLStreamGeneratorPath
        self.__working_directory.MakeFolders = var.MakeFolders

    @property
    def LSLOutletRandom(self):
        return self.__lsl_outlet_random

    @LSLOutletRandom.setter
    def LSLOutletRandom(self, var):
        self.__lsl_outlet_random = var
        self.config['general'].setboolean('lsl_outlet_random', self.__lsl_outlet_random)

    @property
    def Recorder(self):
        return self.__recorder

    @Recorder.setter
    def Recorder(self, var):
        self.__recorder.Groups = var.Groups
        self.__recorder.LSLStreamName = var.LSLStreamName
        self.__recorder.Frequency = var.Frequency
        self.__recorder.DatasetWidth = var.DatasetWidth

    @property
    def Decoder(self):
        return self.__decoder

    @Decoder.setter
    def Decoder(self, var):
        self.__decoder.Dec = var.Dec
        self.__decoder.FMax = var.FMax
        self.__decoder.FMin = var.FMin
        self.__decoder.FStep = var.FStep
        self.__decoder.Th50hz = var.Th50z
        self.__decoder.GridWidth = var.GridWidth
        self.__decoder.GridHeight = var.GridHeight
        self.__decoder.GridChannelFrom = var.GridChannelFrom
        self.__decoder.GridChannelTo = var.GridChannelTo
        self.__decoder.UseInterval = var.UseInterval
        self.__decoder.IntervalStart = var.IntervalStart
        self.__decoder.IntervalStop = var.IntervalStop
        self.__decoder.Measure = var.Measure

    @property
    def Channels(self):
        return self.__channels

    @Channels.setter
    def Channels(self, var):
        self.__channels = var
        self.config['channels'] = self.__channels

    def __init__(self, path):
        if not self._initialized:
            self.config = configparser.ConfigParser()
            file = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), path), encoding="utf8")
            self.config.read_file(file)

            self.__mode              = ToolConfig.ModeEnum.Debug \
                                           if self.config['general'].getboolean('debug_mode') else \
                                       ToolConfig.ModeEnum.Base
            self.__patient           = ToolConfig.PatientType(self.config)
            self.__stimuli           = ToolConfig.StimuliType(self.config)
            self.__presentation      = ToolConfig.PresentationType(self.config)
            self.__working_directory = ToolConfig.WorkingDirectoryType(self.config)
            self.__lsl_outlet_random = self.config['general'].getboolean('lsl_outlet_random')
            self.__recorder          = ToolConfig.RecorderType(self.config)
            self.__decoder           = ToolConfig.DecoderType(self.config)

            self.__channels          = self.config['channels']

            self.path = path

            self.__parse_config()

            self._initialized = True
        else:
            raise Exception("ToolConfig has already instance, please use this one if you have access!")

    def __new__(cls, path):
        if not cls._instance:
            with cls._lock:
                # another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
                if not cls._instance:
                    cls._instance = super(ToolConfig, cls).__new__(cls)
        return cls._instance

    def __parse_config(self):      
        # Path autogeneration ignores path in config and generate path based on location of 'tool_config.py'
        if self.WorkingDirectory.AutoRootPath:
            if len(Path(__file__).resolve().parents) >= 2:
                self.WorkingDirectory.RootPath = str(Path(__file__).resolve().parents[1])
            else:
                raise Exception("Something went wrong with code structure!")            

        # Date and time autogeneration ignores values in config and generate them based on current date and time
        if  self.Patient.AutoDate:
            self.Patient.Date = time.strftime('%y%m%d')

        if  self.Patient.AutoTime:
            self.Patient.Time = time.strftime('%H%M%S')

        self.Patient.DataPath =  os.path.join(self.WorkingDirectory.RootPath, 'PatientData',
                                              str(self.Patient.Date) + '_' + self.Patient.Name,
                                              str(self.Patient.Time) + '_experiment')
        self.Patient.ExperimentDataPath = os.path.join(self.Patient.DataPath, 'experiment_data.h5')
        self.Patient.ResultsPath = os.path.join(self.Patient.DataPath, 'results')
    
        resource_path = os.path.join(self.WorkingDirectory.RootPath, 'resources')
        self.Stimuli.ActionPictures.PathToConfig = os.path.join(os.path.abspath(__file__),
            '..', 'pictures_configs', 'actions_script.json')
        self.Stimuli.ObjectPictures.PathToConfig = os.path.join(os.path.abspath(__file__),
            '..', 'pictures_configs', 'objects_script.json')
        self.Stimuli.OtherPictures.PathToConfig = os.path.join(os.path.abspath(__file__),
            '..', 'pictures_configs', 'others_script.json')
        self.Stimuli.Sound.Path = str(os.path.join(resource_path, 'sounds', 'tone.wav'))
        
        if self.Mode == ToolConfig.ModeEnum.Debug:
            self.Recorder.LSLStreamName = 'Debug'
            self.WorkingDirectory.LSLStreamGeneratorPath = str(os.path.join(self.WorkingDirectory.RootPath,
                                                                            'models', 'recording_model',
                                                                            'lsl_stream_generator.py'))

        # What is this?? Ask question
        # if config['general'].getboolean('show_objects_mode') or config['general'].getboolean('show_actions_mode'):
        #     config['display']['resting_time'] = '1'
            
        
        for i in range(self.Decoder.GridChannelFrom, self.Decoder.GridChannelTo + 1):
            self.Channels['{}'.format(i)] = str(i - self.Decoder.GridChannelFrom + 1)
        
        #print('1')
        # create directories
        os.makedirs(self.Patient.DataPath, exist_ok=True)
        os.makedirs(self.Patient.ResultsPath, exist_ok=True)
        # if not picture_numbers_action_remove_path.is_file():
        #     with open(picture_numbers_action_remove_path, 'w') as file:
        #         pass
        # if not picture_numbers_object_remove_path.is_file():
        #     with open(picture_numbers_object_remove_path, 'w') as file:
        #         pass
        #print('2')
        #print(config['general']['make_folders'])
        #if config['general']['make_folders']:
        #    return config
        #print('3')
        # makedirs(patient_data_path, exist_ok=True)
        self.sync()

    def sync(self):
        experiment_config = os.path.join(self.Patient.DataPath, 'experiment_config.ini')
        with open(experiment_config, 'w') as configfile:
            self.config.write(configfile)
            print(self.config)

    def __str__(self):
        return 'Config:\n' + \
               '    Mode: ' + str(self.Mode) + '\n' + \
                    str(self.Patient) + \
                    str(self.Stimuli) + \
                    str(self.Presentation) + \
                    str(self.WorkingDirectory) + \
               '    LSLOutletRandom: ' + str(self.LSLOutletRandom) + '\n' + \
                    str(self.Recorder) + \
                    str(self.Decoder) + \
               '    Channels: ' + str(dict(self.Channels)) + '\n'
