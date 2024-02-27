// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "math.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Eigen"
#include "Quaternion.h"
#include "Kernel.generated.h"


UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class MESHCAPADE_API UKernel : public UActorComponent
{
	GENERATED_BODY()

public:	
	// Sets default values for this component's properties
	UKernel();

protected:
	// Called when the game starts
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// turns a rodrigues vector into a UE Rotator
	UFUNCTION(BlueprintPure, Category = "Meshcapade Kernel")  // this means it's BP callable inside unreal
		FRotator RodriguesVectorToUE_Rotator(FVector RodriguesVector);

	// turns a rodrigues vector into a 3x3 Matrix for blend shapes, which is then flattened
	UFUNCTION(BlueprintPure, Category = "Meshcapade Kernel")
		TArray <float> RodriguesVectorTo9_MorphTargets(FVector RodriguesVector);

	// turns a UE rotator into a rodrigues vector
	UFUNCTION(BlueprintPure, Category = "Meshcapade Kernel")
		FVector UE_RotatorToRodriguesVector(FRotator rotator);

	// turns a rodrigues vector into a quat
	UFUNCTION(BlueprintPure, Category = "Meshcapade Kernel")
		FQuat RodriguesVectorToQuaternion(FVector RodriguesVector);

	// generate a rotation matrix from the R and theta components of a rodrigues vector
	Eigen::MatrixXd GenerateRotationMatrix(float theta, FVector R);

		
};
