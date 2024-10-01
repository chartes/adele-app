import os, sys, argparse
from app import create_app


POSSIBLE_ENV_VALUES = [ "local", "dev", "prod", "test" ]

def main():
    #################################################################
    # Selecting the .env file to use for deployment (default = dev) #
    #################################################################


    # Creating a dictionary of flask_app.py options (--config=dev) and their matching environment variables files aliases (dev)
    # Creating a flask_app.py --help listing these options
    parser = argparse.ArgumentParser(
        description='Flask app for dico-topo'
    )
    parser.add_argument('--config', type=str, choices=POSSIBLE_ENV_VALUES ,default='dev', help="/".join(POSSIBLE_ENV_VALUES) + ' to select the appropriate .env file to use, default=dev', metavar='')
    args = parser.parse_args()
    # Checking on the .env to be selected for deployment
    # For server deployments, the .env name can be provided from the server configuration
    server_env_config_env_var = os.environ.get('SERVER_ENV_CONFIG')
    if server_env_config_env_var:
        print("Server provided an .env file : ", server_env_config_env_var)
        env = server_env_config_env_var
    # Otherwise, check if .env file to use is provided in command line (with '--config=' option)
    else:
        env = args.config
    print("selected_env_file : ", env)

    ###############################################
    # Launching app with the selected environment #
    ###############################################
    flask_app = create_app(config_name=env)
    flask_app.run(debug=True, port=5000, host='0.0.0.0')

if __name__ == "__main__":
    main()
