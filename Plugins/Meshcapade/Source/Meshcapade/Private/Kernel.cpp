// Fill out your copyright notice in the Description page of Project Settings.


#include "Kernel.h"

// Sets default values for this component's properties
UKernel::UKernel()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = true;

	// ...
}


// Called when the game starts
void UKernel::BeginPlay()
{
	Super::BeginPlay();

	// ...
	
}


// Called every frame
void UKernel::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// ...
}

FQuat UKernel::RodriguesVectorToQuaternion(FVector RodriguesVector)
{
	float theta = RodriguesVector.Length();
	FVector R = RodriguesVector / theta;

	//lifted from /Engine/Source/Runtime/Engine/Private/KismetMathLibrary.cpp
	//https://docs.unrealengine.com/5.1/en-US/API/Runtime/Engine/Kismet/UKismetMathLibrary/RotatorFromAxisAndAngle/
	FVector SafeAxis = R.GetSafeNormal(); // Make sure axis is unit length
	return(FQuat(SafeAxis, theta));
}


FRotator UKernel::RodriguesVectorToUE_Rotator(FVector RodriguesVector)
{
	FRotator PureResult = RodriguesVectorToQuaternion(RodriguesVector).Rotator();

	//special negations for unreal
	return FRotator(PureResult.Pitch, -PureResult.Yaw, -PureResult.Roll);
}


FVector UKernel::UE_RotatorToRodriguesVector(FRotator rotator) {
	FVector axis;
	float angle;
	FQuat q = rotator.Quaternion();
	q.ToAxisAndAngle(axis, angle);

	return angle * axis;
}

// generate a rotation matrix from the R and theta components of a rodrigues vector
Eigen::MatrixXd UKernel::GenerateRotationMatrix(float theta, FVector R)
{
	Eigen::MatrixXd I(3, 3);
	I = Eigen::MatrixXd::Identity(3, 3);

	if (theta < .00000001f)
		return I;

	Eigen::MatrixXd R_Transpose(3, 3);
	R_Transpose(0, 0) = R.X * R.X;
	R_Transpose(0, 1) = R.X * R.Y;
	R_Transpose(0, 2) = R.X * R.Z;
	R_Transpose(1, 0) = R.Y * R.X;
	R_Transpose(1, 1) = R.Y * R.Y;
	R_Transpose(1, 2) = R.Y * R.Z;
	R_Transpose(2, 0) = R.Z * R.X;
	R_Transpose(2, 1) = R.Z * R.Y;
	R_Transpose(2, 2) = R.Z * R.Z;

	Eigen::MatrixXd R_Cross(3, 3);
	R_Cross(0, 0) = 0;
	R_Cross(0, 1) = -R.Z;
	R_Cross(0, 2) = R.Y;
	R_Cross(1, 0) = R.Z;
	R_Cross(1, 1) = 0;
	R_Cross(1, 2) = -R.X;
	R_Cross(2, 0) = -R.Y;
	R_Cross(2, 1) = R.X;
	R_Cross(2, 2) = 0;

	return (std::cos(theta) * I + (1 - std::cos(theta)) * R_Transpose + std::sin(theta) * R_Cross);
}


TArray <float> UKernel::RodriguesVectorTo9_MorphTargets(FVector RodriguesVector)
{
	float theta = RodriguesVector.Length();
	FVector R = RodriguesVector / theta;

	Eigen::MatrixXd Rotation_Matrix = GenerateRotationMatrix(theta, R);
	Rotation_Matrix = Rotation_Matrix - Eigen::MatrixXd::Identity(3, 3);

	TArray <float> FlattenedMatrix;
	for (int i = 0; i < 3; ++i)
		for (int j = 0; j < 3; ++j)
			FlattenedMatrix.Add(Rotation_Matrix(i, j));

	return FlattenedMatrix;
}
