# @INVIENT_COPYRIGHT@
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

from muntjac.terminal.gwt.server.application_servlet import ApplicationServlet


class InvientChartsDemoAppServlet(ApplicationServlet):

    def writeAjaxPageHtmlMuntjacScripts(self, window, themeName, application, page, appUrl, themeUri, appId, request):
        page.write('<script type=\"text/javascript\">\n')
        page.write('//<![CDATA[\n')
        page.write('document.write(\"<script language=\'javascript\' src=\'./jquery/jquery-1.4.4.min.js\'><\\/script>\");\n')
        page.write('document.write(\"<script language=\'javascript\' src=\'./js/highcharts.js\'><\\/script>\");\n')
        page.write('document.write(\"<script language=\'javascript\' src=\'./js/modules/exporting.js\'><\\/script>\");\n')
        page.write('//]]>\n</script>\n')
        super(InvientChartsDemoAppServlet, self).writeAjaxPageHtmlMuntjacScripts(window, themeName, application, page, appUrl, themeUri, appId, request)
