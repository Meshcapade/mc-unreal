// Copyright Epic Games, Inc. All Rights Reserved.

#include "Meshcapade.h"
#include "MeshcapadeStyle.h"

#define LOCTEXT_NAMESPACE "FMeshcapadeModule"

void FMeshcapadeModule::StartupModule()
{
    UE_LOG(LogTemp, Warning, TEXT("MeshcapadeEditorModule started"));
    FMeshcapadeStyle::Initialize();
}

void FMeshcapadeModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
	// we call this function before unloading the module.
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FMeshcapadeModule, Meshcapade)