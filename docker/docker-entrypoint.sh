#!/bin/sh -eu

# Generate JWT keys
if [ ! -e /scigateway-auth-run/keys/jwt-key ]
then
    ssh-keygen -t rsa -m 'PEM' -f /scigateway-auth-run/keys/jwt-key -q -N ""
fi

# Use a tempfile instead of sed -i so that only the file, not the directory needs to be writable
TEMPFILE="$(mktemp)"

# Set values in config.yaml from environment variables
# No quotes for verify because it's boolean
sed -e "s|\"icat_url\": \".*\"|\"icat_url\": \"$ICAT_URL\"|" \
    -e "s|\"log_location\": \".*\"|\"log_location\": \"$LOG_LOCATION\"|" \
    -e "s|\"private_key_path\": \".*\"|\"private_key_path\": \"$PRIVATE_KEY_PATH\"|" \
    -e "s|\"public_key_path\": \".*\"|\"public_key_path\": \"$PUBLIC_KEY_PATH\"|" \
    -e "s|\"maintenance_config_path\": \".*\"|\"maintenance_config_path\": \"$MAINTENANCE_CONFIG_PATH\"|" \
    -e "s|\"scheduled_maintenance_config_path\": \".*\"|\"scheduled_maintenance_config_path\": \"$SCHEDULED_MAINTENANCE_CONFIG_PATH\"|" \
    -e "s|\"verify\": [^,]*|\"verify\": $VERIFY|" \
    scigateway_auth/config.json > "$TEMPFILE"

cat "$TEMPFILE" > scigateway_auth/config.json
rm "$TEMPFILE"

# Run the CMD instruction
exec "$@"
