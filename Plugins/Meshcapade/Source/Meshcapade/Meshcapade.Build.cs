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
				"Meshcapade/Public/",
				"Meshcapade/Private/",
				// ... add other private include paths required here ...
			}
			);
			
		
		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
				"CoreUObject",
				"Engine",
				"InputCore", 
			}
			);
			
		// this is no longer being used, but since it still builds, I'll leave it here in case I need it later
		// if we're in the editor add specific functionality that prevents building
		if (Target.Type == TargetRules.TargetType.Editor) 
		{
			PublicDependencyModuleNames.AddRange(
				new string[]
				{
					"UnrealEd",
					"AssetTools",
				}
				);

			AddEngineThirdPartyPrivateStaticDependencies(Target, "zlib");
		}


		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"Slate",
				"SlateCore",
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
