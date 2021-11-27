from queue import Queue
from threading import Thread
from decoder import Decoder

class SCMappingModel:
    def __init__(self, tool_config):
        self.tool_config = tool_config
        self.decoder = Decoder(tool_config)
        self.decoder_thread = Thread(target=self.decoder.decode, args=())
        self.decoder_thread.daemon = True
        self.is_started = False

    def set_input_queue(self, input_queue):
        self.decoder.set_input_queue(input_queue)

    def start(self):
        # remove_mode does not use data from lsl, just show pictures
        # This should be transfered to PreviewModel
        # if config['general'].getboolean('show_objects_mode') or config['general'].getboolean('show_actions_mode'):
        #     patient_display = Display(config, qs)
        #     patient_display.start()
        #     return
       
        while not self.decoder.input_queue:
           key, value = self.decoder.input_queue.get()
           print(key, value.shape)
        #time.sleep(10)
        # process data and plot results
        #recorder.thread.join()

        self.decoder_thread.start()
        self.is_started = True

        #recorder.thread.join()
        #recorder.thread.join()

    def stop(self):
        if self.is_started:
            self.decoder.get_input_queue().put((3, []))
            self.decoder.decode_finish()
            if self.decoder_thread.is_alive():
                self.decoder_thread.join()
        self.is_started = False