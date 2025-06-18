// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class Meshcapade : ModuleRules
{
	public Meshcapade(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;
		
		PublicIncludePaths.AddRange(
			new string[] {
				// ... add public include paths required here ...
			}
			);

		AddEngineThirdPartyPrivateStaticDependencies(Target, "Eigen");
		//AddEngineThirdPartyPrivateStaticDependencies(Target, "zlib");	// solea requirement

		
		PrivateIncludePaths.AddRange(
			new string[] {
				// ... add other private include paths required here ...
			}
			);


			if (Target.bBuildEditor)
			{
				PublicDependencyModuleNames.AddRange(new string[] {
					"Core", "CoreUObject", "Engine", "UnrealEd",
					"Kismet", "KismetCompiler", "BlueprintGraph", "InputCore", "EnhancedInput",

					//more stuff for icons
					"Slate", "SlateCore", "EditorStyle",
					"LevelEditor", "Blutility", "UMG", "ToolMenus", "UMGEditor"
					
				});
			}
			else
			{
				PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput" });
			}


        PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"Slate",
				"SlateCore",
				// ... add private dependencies that you statically link with here ...	
			}
			);
		
		
		DynamicallyLoadedModuleNames.AddRange(
			new string[]
			{
				// ... add any modules that your module loads dynamically here ...
			}
			);
	}
}
