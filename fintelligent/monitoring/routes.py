from flask import Blueprint

monitoring = Blueprint('monitoring', __name__)

@monitoring.route('/monitoring')
def monitoring_home():
    return 'Financial Monitoring (Coming Soon)' 