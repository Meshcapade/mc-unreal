# set the plugin configuration for Meshcapade Unreal Engine plugin here

USE_MODE = "PROD"  # Set to "PROD" or "DEV"

# API link configuration
# Use the production API link by default
if USE_MODE == "DEV":
    API_LINK = "https://api2.dev.meshcapade.com/"
    KEYCLOAK_DOMAIN = "https://auth.dev.meshcapade.com"
    REALM = "meshcapade-me"
    CLIENT_ID = "meshcapade-me-unreal"
else:
    API_LINK = "https://api.meshcapade.com/"
    KEYCLOAK_DOMAIN = "https://auth.meshcapade.com"
    REALM = "meshcapade-me"
    CLIENT_ID = "meshcapade-me-unreal"
