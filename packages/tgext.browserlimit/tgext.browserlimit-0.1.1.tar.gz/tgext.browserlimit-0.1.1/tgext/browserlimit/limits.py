import logging
from useragent_parser import detect

log = logging.getLogger('tgext.browserlimit')

class MinimumVersionLimit(object):
    def __init__(self, user_agent):
        self.user_agent = user_agent

    def is_met(self, request):
        if not self.user_agent:
            return True

        detected_browser = detect(self.user_agent)
        if "browser" not in detected_browser:
            log.warning('Letting %s pass due to unknown browser' % self.user_agent)
            return True

        bw_name = detected_browser['browser']['name']
        if bw_name not in self.browser_versions:
            return True

        try:
            bw_version = '.'.join(detected_browser['browser']['version'].split('.')[:2])
            bw_version = float(bw_version)
        except:
            log.warning('Letting browser %s pass due to unknown release version: %s' %
                        (bw_name, detected_browser['browser']['version']))
            return True

        bw_limit = self.browser_versions[bw_name]
        if bw_version < bw_limit:
            return False

        return True

class ModernBrowserLimit(MinimumVersionLimit):
    browser_versions = {'Chrome':12,
                        'Firefox':4,
                        'Microsoft Internet Explorer':9,
                        'Safari':4}

class HTML5BrowserLimit(MinimumVersionLimit):
    browser_versions = {'Chrome':6,
                        'Firefox':3.6,
                        'Microsoft Internet Explorer':9,
                        'Safari':4}

class BasicBrowserLimit(MinimumVersionLimit):
    browser_versions = {'Chrome':4,
                        'Firefox':3.6,
                        'Microsoft Internet Explorer':8,
                        'Safari':3.2}

class MinimalBrowserLimit(MinimumVersionLimit):
    browser_versions = {'Firefox':3,
                        'Microsoft Internet Explorer':7,
                        'Safari':3}
