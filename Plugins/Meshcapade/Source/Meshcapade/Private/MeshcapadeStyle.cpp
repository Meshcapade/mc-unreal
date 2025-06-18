#include "MeshcapadeStyle.h"
#include "Styling/SlateStyleRegistry.h"
#include "Engine/Texture2D.h"

TSharedPtr<FSlateStyleSet> FMeshcapadeStyle::StyleInstance = nullptr;

void FMeshcapadeStyle::Initialize()
{
    UE_LOG(LogTemp, Warning, TEXT("***************************************************************************"));

    UE_LOG(LogTemp, Warning, TEXT("MeshcapadeStyle::Initialize() called"));

    if (StyleInstance.IsValid())
        return;

    StyleInstance = MakeShared<FSlateStyleSet>("MeshcapadeStyle");

    // Load the actual UTexture2D from /Game/UI/Icons/MeshcapadeIcon
    FString IconPath = TEXT("/Meshcapade/UI/Icons/MeshcapadeIcon.MeshcapadeIcon");
    UTexture2D* IconTexture = LoadObject<UTexture2D>(nullptr, *IconPath);
    if (IconTexture)
    {
        FSlateBrush* Brush = new FSlateImageBrush(IconTexture, FVector2D(120.0f, 120.0f));
        StyleInstance->Set("Meshcapade.Icon", Brush);
    }

    FSlateStyleRegistry::RegisterSlateStyle(*StyleInstance);

    UE_LOG(LogTemp, Warning, TEXT("Loaded texture: %s"), *GetNameSafe(IconTexture));
}

void FMeshcapadeStyle::Shutdown()
{
    if (StyleInstance.IsValid())
    {
        FSlateStyleRegistry::UnRegisterSlateStyle(*StyleInstance);
        StyleInstance.Reset();
    }
}

TSharedPtr<ISlateStyle> FMeshcapadeStyle::Get()
{
    return StyleInstance;
}
