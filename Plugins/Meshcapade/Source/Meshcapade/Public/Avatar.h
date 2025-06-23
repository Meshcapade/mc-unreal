#pragma once

#include "CoreMinimal.h"
#include "Misc/DateTime.h"
#include "Avatar.generated.h"

UENUM(BlueprintType)
enum class EMeshState : uint8
{
    MESH_EXIST_NOT_READY        UMETA(DisplayName = "Mesh Exist Not Ready"),
    MESH_READY                  UMETA(DisplayName = "Mesh Ready"),
    MESH_NOT_EXIST              UMETA(DisplayName = "Mesh Not Exist")
};

USTRUCT(BlueprintType)
struct FAvatar
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Avatar")
    FString Name;

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Avatar")
    FString Id;

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Avatar")
    FDateTime Creation_Date;

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Avatar")
    EMeshState Mesh_State;

    // Optional constructor for convenience
    FAvatar()
        : Name(TEXT("")), Id(TEXT("")), Creation_Date(FDateTime::Now()), Mesh_State(EMeshState::MESH_NOT_EXIST)
    {
    }
};
