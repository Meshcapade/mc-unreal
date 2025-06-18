import importlib
import unreal


@unreal.uclass()
class UIUtils(unreal.BlueprintFunctionLibrary):
    @unreal.ufunction(static=True, ret=None)
    def ui_cleanup() -> bool:
        import keycloak_auth_wrapper
        import authentication
        import meshcapade_api

        importlib.reload(keycloak_auth_wrapper)
        importlib.reload(meshcapade_api)
        importlib.reload(authentication)
