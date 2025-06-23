import unreal
import install_requirements
import meshcapade_UI_startup
import ui_utils
import keycloak_auth_wrapper
import meshcapade_api

unreal.log("Python startup scripts loaded successfully.")


# load mcme-unreal blueprint
bp = unreal.EditorAssetLibrary.load_asset("/Meshcapade/UI/mcme-unreal")

# Reconstruct and compile it using our custom compile function
unreal.CompileBlueprintPlugin.compile_blueprint(bp)

# Save it after compiling
unreal.EditorAssetLibrary.save_loaded_asset(bp)

unreal.log("Blueprint compiled and saved successfully. 🛠️📝")

meshcapade_UI_startup.Startup()

unreal.log("Launching Editor Button. 💻")
