#!/bin/sh -eu

# Generate JWT keys
ssh-keygen -t rsa -m 'PEM' -f /scigateway-auth-run/keys/jwt-key -q -N ""

# Set values in config.yaml from environment variables
sed -i "s|\"icat_url\": \".*\"|\"icat_url\": \"$ICAT_URL\"|" /scigateway-auth-run/config.json
sed -i "s|\"log_location\": \".*\"|\"log_location\": \"$LOG_LOCATION\"|" /scigateway-auth-run/config.json
sed -i "s|\"private_key_path\": \".*\"|\"private_key_path\": \"$PRIVATE_KEY_PATH\"|" /scigateway-auth-run/config.json
sed -i "s|\"public_key_path\": \".*\"|\"public_key_path\": \"$PUBLIC_KEY_PATH\"|" /scigateway-auth-run/config.json
sed -i "s|\"maintenance_config_path\": \".*\"|\"maintenance_config_path\": \"$MAINTENANCE_CONFIG_PATH\"|" /scigateway-auth-run/config.json
sed -i "s|\"scheduled_maintenance_config_path\": \".*\"|\"scheduled_maintenance_config_path\": \"$SCHEDULED_MAINTENANCE_CONFIG_PATH\"|" /scigateway-auth-run/config.json
sed -i "s|\"verify\": [^,]*|\"verify\": $VERIFY|" /scigateway-auth-run/config.json

# Run the CMD instruction
exec "$@"
