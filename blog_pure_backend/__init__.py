from flask import Flask
from flask_graphql import GraphQLView
from .schema import schema
from .database import session

app = Flask(__name__)
app.logger.propagate = True

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    session.remove()
    return response_or_exc
