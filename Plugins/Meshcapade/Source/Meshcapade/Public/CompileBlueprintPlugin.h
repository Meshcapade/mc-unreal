// CompileBlueprintPlugin.h
#pragma once


#include "CoreMinimal.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "UObject/ObjectMacros.h"
#include "UObject/Object.h"
#include "CompileBlueprintPlugin.generated.h"


UCLASS()
class UCompileBlueprintPlugin : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "PythonBridge")
    static void CompileBlueprint(UBlueprint* Blueprint);
};