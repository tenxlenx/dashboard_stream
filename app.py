from flask import Flask, render_template
import subprocess
import atexit
from flask_cors import cross_origin
import argparse

parser = argparse.ArgumentParser(description='Dashboard')
parser.add_argument('--password', type=str, help='password for the server')
parser.add_argument('--user', type=str, help='user for the server')
parser.add_argument('--host', type=str, help='the domain of the server')
parser.add_argument('--port', type=str, help='the port of the server')
args = parser.parse_args()

app = Flask(__name__)
host_domain = args.host
ssl_cert = host_domain.join('.crt')
ssl_key = host_domain.join('.key')
host_port = args.port
print(rf"""running server at {host_domain}:{host_port}""" + '\n ssl cert file= ' + ssl_cert + ' ssl key file= ' + ssl_key + '\n')


def run_command(tmux_session_name: str, command: str):
    shell_script = f'''
    #!/bin/bash
    session_name="{tmux_session_name}"
    if tmux has-session -t "$session_name" 2>/dev/null; then
        tmux attach-session -t "$session_name"
    else
        tmux new-session -d -s "$session_name" "{command}"
        tmux attach-session -t "$session_name"
    fi
    '''
    return shell_script


def start_wetty(server_port: str, process_to_run: str):
    return subprocess.Popen(['wetty',
                             '--ssh-host', args.host,
                             '--ssh-port', '22',
                             '--port', server_port,
                             '--ssh-user', args.user, '--ssh-pass', args.password,
                             '--ssl-key', ssl_key,
                             '--ssl-cert', ssl_cert,
                             '--allow-iframe', '--command', process_to_run])


wetty_process = start_wetty(host_port, 'htop')


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
    response.headers.pop('X-Frame-Options', None)
    return response


@app.route('/')
@cross_origin()
def hello():
    return render_template('index.html')


# host 'reactor.brill-neon.ts.net'
if __name__ == '__main__':
    app.run(port=host_port, host=host_domain,
            ssl_context=(ssl_cert, ssl_key))
