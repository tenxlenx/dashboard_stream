from flask import Flask, render_template
from flask.views import MethodView
import subprocess
import atexit
from flask_cors import cross_origin
import argparse

# packages need: htop, ctop, cgroup-tools, nvtop
# sudo snap install cointop --stable
# export NNN_PLUG='x:!chmod +x "$nnn";g:!git log;s:!smplayer "$nnn"'  adding plugins for key shortcuts
#       use * for skipping user confirmation    e.g. NNN_PLUG='x:!chmod +x "$nnn";g:!git log;s:!smplayer "$nnn"'
#       use & for GUI apps
#       use ! for long processes                NNN_PLUG='s:!smplayer "$nnn"*;n:-!vim'

# Command-line argument parsing
parser = argparse.ArgumentParser(description='Dashboard')
parser.add_argument('--password', type=str, required=True, help='password for the server')
parser.add_argument('--user', type=str, required=True, help='user for the server')
parser.add_argument('--host', type=str, required=True, help='the domain of the server')
parser.add_argument('--port', type=str, required=True, help='the port of the server')
args = parser.parse_args()

# Initialize Flask app
app = Flask(__name__)
host_domain = args.host
ssl_cert = f"{host_domain}.crt"
ssl_key = f"{host_domain}.key"
host_port = args.port

print(f"Running server at {host_domain}:{host_port}\nSSL cert file= {ssl_cert} SSL key file= {ssl_key}\n")


class SecondPageView(MethodView):
    @staticmethod
    @cross_origin()
    def get():
        return render_template('llms.html')

class DashboardView(MethodView):
    @staticmethod
    def run_command(tmux_session_name: str, command: str):
        shell_script = f'''
        #!/bin/bash
        session_name="{tmux_session_name}"
        if tmux has-session -t "$session_name" 2>/dev/null; then
            tmux attach-session -t "$session_name"
        else
            tmux new-session -s "$session_name" "{command}"
            tmux attach-session -t "$session_name"
        fi
        '''
        return shell_script

    @staticmethod
    def start_wetty(service_port: str, process_to_run: str, process_name : str):
        return subprocess.Popen(['wetty',
                                 '--ssh-host', args.host,
                                 '--ssh-port', '22',
                                 '--port', service_port,
                                 '--ssh-user', args.user, '--ssh-pass', args.password,
                                 '--ssl-key', ssl_key,
                                 '--ssl-cert', ssl_cert,
                                 '--allow-iframe', '--command', DashboardView.run_command(process_name, process_to_run)
                                 ])

    @staticmethod
    @cross_origin()
    def get():
        return render_template('index.html')


nvtop_service_port = '9003'
htop_service_port = '9004'
nnn_service_port = '9002'
dry_service_port = '9001'
htop_process = DashboardView.start_wetty(htop_service_port, 'btop -lc -p 5', 'btop-session')
nvtop_process = DashboardView.start_wetty(nvtop_service_port, 'nvtop', 'nvtop-session')
nnn_process = DashboardView.start_wetty(nnn_service_port, 'nnn -d -D -e -R -U -c -x ~/', 'nnn-session')
dry_process = DashboardView.start_wetty(dry_service_port, 'dry', 'dry-session')


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
    response.headers.pop('X-Frame-Options', None)
    return response


app.add_url_rule('/', view_func=DashboardView.as_view('dashboard'))
app.add_url_rule('/llms', view_func=SecondPageView.as_view('llms'))


if __name__ == '__main__':
    app.run(port=host_port, host=host_domain,
            ssl_context=(ssl_cert, ssl_key))
