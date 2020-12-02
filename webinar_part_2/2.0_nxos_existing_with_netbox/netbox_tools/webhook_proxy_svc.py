from flask import Flask, request
import requests
app = Flask(__name__)

gitlab_payload = {
    'token': (None, ''),
    'ref': (None, 'master'),
}

gitlab_url = ''
host_vars = ''

@app.route('/netbox_webhook/', methods=['POST'])
def parse_request():
    data = request.data  # data is empty

    try:
        if not requests.get(host_vars, files=gitlab_payload).status_code in (400, 401):
          response = requests.post(gitlab_url, files=gitlab_payload)

          pipeline_id = response.json()['id']
          msg = 'launched the pipeline - id {}'.format(pipeline_id)
          print(msg)
          return msg, 200
        else:
          print("host_vars not existing yet")
          msg = "host_vars not existing yet"
          return msg, 404

    except Exception as e:
        msg = 'Failed to launch the pipeline: {}'.format(str(e))
        print(msg)
        return msg, 500

if __name__ == '__main__':
    app.run(host="0.0.0.0")
