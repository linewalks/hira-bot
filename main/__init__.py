import os

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from datetime import timedelta
from flask import Flask
from flask_apispec.extension import FlaskApiSpec
from flask_compress import Compress
from flask_cors import CORS


root_path = os.getcwd()
file_path = os.path.join(root_path, "main", "hira_bot.cfg")

docs = FlaskApiSpec()
compress = Compress()
cors = CORS()

def make_config_file(file_path):
  if not os.path.isfile(file_path):
    with open(f"{file_path.strip('.cfg')}.default.cfg", "r") as read_file:
      with open(file_path, "w") as file:
        file.write(read_file.read())


def read_config(file_path=file_path):
  make_config_file(file_path)
  app = Flask(__name__)
  app.config.from_pyfile(file_path)

  return app


def create_app(file_path=file_path):
  make_config_file(file_path)

  app = Flask(__name__)

  app.config.from_pyfile(file_path)

  app.config.update({
      "APISPEC_SPEC": APISpec(
          title="hira-bot",
          version="0.1.0",
          openapi_version="2.0.0",
          plugins=[FlaskPlugin(), MarshmallowPlugin()],

      ),
      "APISPEC_SWAGGER_URL": "/docs.json",
      "APISPEC_SWAGGER_UI_URL": "/docs/"
  })

  docs.init_app(app)
  compress.init_app(app)
  cors.init_app(app)

  with app.app_context():
    from background.nhiss import celery
    from nhiss.tasks.reservation_mode import run_until_success
    # Blueprint
    from main.controllers.nhiss import nhiss_bp

    blueprints = [
        nhiss_bp,
    ]

    for bp in blueprints:
      app.register_blueprint(bp)
    docs.register_existing_resources()

    # 스웨거에서 options 제거
    for key, value in docs.spec._paths.items():
      docs.spec._paths[key] = {
          inner_key: inner_value for inner_key, inner_value in value.items() if inner_key != "options"
      }

  return app
