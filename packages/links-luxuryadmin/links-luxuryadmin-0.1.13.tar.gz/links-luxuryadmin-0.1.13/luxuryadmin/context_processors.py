from .forms import LoginForm

from models import PLUGINS, Section

def login_form(request):
    return {
        'luxuryadmin': {
            'forms': {
                'login': LoginForm
            }
        }
    }

def plugins(request):
    def admin_sections():
        for plugin in PLUGINS:
            for section in plugin.sections:
                yield section

    return {
        'admin': {
            'sections': admin_sections()
        }
    }