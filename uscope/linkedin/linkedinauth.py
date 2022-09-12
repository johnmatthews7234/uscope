from crypt import methods
from email.mime import application
from linkedin import linkedin
from uscope.helper import get_key
from flask import redirect, Blueprint




bp = Blueprint('linkedin', __name__, url_prefix='/linkedin')

@bp.route('/login', methods=('GET',))
def login():
    LINKEDIN_APP_KEY = get_key('linkedin_app_key')
    LINKEDIN_APP_SECRET = get_key('linkedin_app_secret')
    RETURN_URL = 'http://localhost:5000/linkedin/start'

    authentication = linkedin.LinkedInAuthentication(LINKEDIN_APP_KEY, LINKEDIN_APP_SECRET, RETURN_URL, linkedin.PERMISSIONS.enums.values())
    redirect(authentication.authorization_url)
    application  = linkedin.LinkedInApplication(authentication)

