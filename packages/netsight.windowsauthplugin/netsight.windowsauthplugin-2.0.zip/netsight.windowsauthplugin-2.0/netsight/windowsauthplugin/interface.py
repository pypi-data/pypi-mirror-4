from Products.PluggableAuthService.interfaces.plugins import *

class IWindowsauthpluginHelper( IAuthenticationPlugin,
                                ILoginPasswordExtractionPlugin,
                                IChallengePlugin,
                                ):
    """interface for WindowsauthpluginHelper."""
