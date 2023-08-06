# Copyright (C) 2012 Vaadin Ltd. 
# Copyright (C) 2012 Richard Lincoln
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
#     http://www.apache.org/licenses/LICENSE-2.0 
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License.

from muntjac.ui.abstract_ordered_layout import AbstractOrderedLayout


class VerticalLayout(AbstractOrderedLayout):
    """Vertical layout.

    C{VerticalLayout} is a component container, which shows the
    subcomponents in the order of their addition (vertically). A vertical
    layout is by default 100% wide.

    @author: Vaadin Ltd.
    @author: Richard Lincoln
    @version: 1.1.2
    """

    CLIENT_WIDGET = None #ClientWidget(VVerticalLayout, LoadStyle.EAGER)

    def __init__(self):
        super(VerticalLayout, self).__init__()

        self.setWidth('100%')
