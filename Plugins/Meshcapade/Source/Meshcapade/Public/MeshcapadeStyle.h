#pragma once

#include "CoreMinimal.h"
#include "Styling/SlateStyle.h"

class FMeshcapadeStyle
{
public:
    static void Initialize();
    static void Shutdown();

    static TSharedPtr<class ISlateStyle> Get();

private:
    static TSharedPtr<FSlateStyleSet> StyleInstance;
};
