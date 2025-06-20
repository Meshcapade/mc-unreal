// CompileBlueprintPlugin.cpp
#include "CompileBlueprintPlugin.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "Editor.h"
#include "Blueprint/BlueprintSupport.h"
#include "EdGraph/EdGraphNode.h"


void UCompileBlueprintPlugin::CompileBlueprint(UBlueprint* Blueprint)
{
#if WITH_EDITOR
    if (!Blueprint)
    {
        UE_LOG(LogTemp, Warning, TEXT("❌ Invalid Blueprint passed to CompileBlueprint."));
        return;
    }

    // STEP 1: Refresh/Reconstruct all nodes
    for (UEdGraph* Graph : Blueprint->UbergraphPages)
    {
        if (!Graph) continue;

        for (UEdGraphNode* Node : Graph->Nodes)
        {
            if (!Node) continue;

            Node->ReconstructNode();    // Repair broken pins
        }
    }

    for (UEdGraph* Graph : Blueprint->FunctionGraphs)
    {
        if (!Graph) continue;

        for (UEdGraphNode* Node : Graph->Nodes)
        {
            if (!Node) continue;

            Node->ReconstructNode();
        }
    }

    // STEP 2: Now compile
    FKismetEditorUtilities::CompileBlueprint(Blueprint);

    UE_LOG(LogTemp, Log, TEXT("✅ Reconstructed and compiled Blueprint: %s"), *Blueprint->GetName());
#else
    UE_LOG(LogTemp, Error, TEXT("❌ CompileBlueprint is only available in the Editor."));
#endif
}