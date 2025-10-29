FROM quay.io/keycloak/keycloak:26.0

# Copy realm configuration
COPY realm-import.json /opt/keycloak/data/import/

# Import realm on startup and enable legacy token exchange (V1)
CMD ["start-dev", "--import-realm", "--features=token-exchange"]
