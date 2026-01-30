package main

import (
	"log"
	"net"

	"user_management/internal/config"
	"user_management/internal/handlers"
	"user_management/internal/repositories"
	"user_management/internal/services"

	"google.golang.org/grpc"
)

func main() {
	cfg := config.LoadConfig()
	
	// Initialize database connection
	db, err := repositories.NewPostgresConnection(cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Initialize repositories
	userRepo := repositories.NewUserRepository(db)
	tenantRepo := repositories.NewTenantRepository(db)

	// Initialize services
	userService := services.NewUserService(userRepo, tenantRepo)
	authService := services.NewAuthenticationService(userRepo, cfg.JWTSecret)

	// Initialize gRPC server
	lis, err := net.Listen("tcp", cfg.GRPCAddress)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer(
		grpc.UnaryInterceptor(handlers.UnaryServerInterceptor()),
	)

	// Register gRPC services
	handlers.RegisterUserManagementServer(grpcServer, &handlers.UserManagementServer{
		UserService: userService,
		AuthService: authService,
	})

	log.Printf("Starting gRPC server on %s", cfg.GRPCAddress)
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}