import logging.config
from flask import Flask
from flask_graphql import GraphQLView
from .config import LOGGING
from .schema import schema
from .database import metadata, session

logging.config.dictConfig(LOGGING)
app = Flask(__name__)
app.logger.propagate = True

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    session.remove()
    return response_or_exc


@app.before_first_request
def reflect_tables():
    logger = logging.getLogger()
    logger.info('Successful reflect!')
    metadata.reflect()
