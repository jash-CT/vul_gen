package handlers

import (
	"context"

	"user_management/internal/services"
	"user_management/proto" // Assume this is generated from protobuf definitions

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type UserManagementServer struct {
	proto.UnimplementedUserManagementServiceServer
	UserService *services.UserService
	AuthService *services.AuthenticationService
}

func (s *UserManagementServer) Register(ctx context.Context, req *proto.RegisterRequest) (*proto.RegisterResponse, error) {
	user, err := s.UserService.RegisterUser(req.Email, req.Password, req.TenantDomain)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "registration failed: %v", err)
	}

	return &proto.RegisterResponse{
		UserId:   user.ID.String(),
		TenantId: user.TenantID.String(),
	}, nil
}

func (s *UserManagementServer) Login(ctx context.Context, req *proto.LoginRequest) (*proto.LoginResponse, error) {
	user, token, err := s.AuthService.Authenticate(req.Email, req.Password)
	if err != nil {
		return nil, status.Errorf(codes.Unauthenticated, "login failed")
	}

	return &proto.LoginResponse{
		Token:    token,
		UserId:   user.ID.String(),
		TenantId: user.TenantID.String(),
	}, nil
}