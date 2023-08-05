# -*- coding: utf-8 -*-
#
# Copyright (c) 2007-2010 Parisson
# Copyright (c) 2010 Paul Brossier <piem@piem.org>
#
# This file is part of TimeSide.

# TimeSide is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# TimeSide is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with TimeSide.  If not, see <http://www.gnu.org/licenses/>.

# Author: Paul Brossier <piem@piem.org>

from timeside.core import Processor, implements, interfacedoc
from timeside.api import IEncoder
from timeside.encoder.gstutils import *

class WavEncoder(GstEncoder):
    """ gstreamer-based encoder """
    implements(IEncoder)

    def __init__(self, output,  streaming=False):
        if isinstance(output, basestring):
            self.filename = output
        else:
            self.filename = None
        self.streaming = streaming
        
        if not self.filename and not self.streaming:
            raise Exception('Must give an output')

        self.eod = False
        
    @interfacedoc
    def setup(self, channels=None, samplerate=None, nframes=None):
        super(WavEncoder, self).setup(channels, samplerate, nframes)
        # TODO open file for writing
        # the output data format we want
        self.pipe = ''' appsrc name=src
                  ! audioconvert 
                  ! wavenc
                  '''
        if self.filename and self.streaming:
            self.pipe += ''' ! tee name=t
            ! queue ! filesink location=%s
            t. ! queue ! appsink name=app sync=False
            ''' % self.filename
            
        elif self.filename :
            self.pipe += '! filesink location=%s ' % self.filename
        else:
            self.pipe += '! appsink name=app sync=False'
            
        # start pipeline
        self.start_pipeline(channels, samplerate)
        
    @staticmethod
    @interfacedoc
    def id():
        return "gst_wav_enc"

    @staticmethod
    @interfacedoc
    def description():
        return "Wav GStreamer based encoder"

    @staticmethod
    @interfacedoc
    def format():
        return "WAV"

    @staticmethod
    @interfacedoc
    def file_extension():
        return "wav"

    @staticmethod
    @interfacedoc
    def mime_type():
        return "audio/x-wav"

    @interfacedoc
    def set_metadata(self, metadata):
        #TODO
        pass
