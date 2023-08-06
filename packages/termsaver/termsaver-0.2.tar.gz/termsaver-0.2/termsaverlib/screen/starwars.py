###############################################################################
#
# file:     rfc.py
#
# Purpose:  refer to module documentation for details
#
# Note:     This file is part of Termsaver application, and should not be used
#           or executed separately.
#
###############################################################################
#
# Copyright 2012 Termsaver
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
###############################################################################
"""
A simple screen that fetches documents from RFC (Request for Comments).

The screen class available here is:

    * `RFCScreen`
"""

#
# Python built-in modules
#
import os

#
# Internal modules
#
from termsaverlib.screen.base import ScreenBase
from termsaverlib.screen.helper.position import PositionHelperBase
from termsaverlib.i18n import _


class StarWarsScreen(ScreenBase, PositionHelperBase):
    """
    """

    frame_size = 14

    def __init__(self):
        """
        The constructor of this class, using most default values from its super
        class, `SimpleUrlFetcherBase`.
        """
        ScreenBase.__init__(self,
            "starwars",
            _("runs the asciimation Star Wars movie"),
            {'opts': 'h', 'long_opts': ['help',]},
        )
        self.cleanup_per_cycle = False

    def _run_cycle(self):
        """
        """
        
        #
        # confirm first that we are entering telnet (hard to close)
        #
        # FIXME
        
        os.system("telnet towel.blinkenlights.nl")
        


